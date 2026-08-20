"""
REST API routes for the Claude Control Plane.
"""
import time
import logging
from flask import request, jsonify, render_template, g

logger = logging.getLogger('routes')


def register_routes(app):
    def mgrs():
        return app.config['managers']

    @app.before_request
    def _start_timer():
        g._req_start = time.time()

    @app.after_request
    def _log_request(response):
        ms = (time.time() - g._req_start) * 1000
        logger.info(f'{request.method} {request.path} → {response.status_code}  ({ms:.1f}ms)')
        return response

    # ---- Index ----

    @app.route('/')
    def index():
        # The header's Claude window/week meters are rendered by remdev's
        # embeddable status-bar service (the cldBar kit embeds it; cldlab
        # keeps no window state of its own). app.remdev_url pins the origin;
        # unset, the browser derives it from its own hostname — a server-side
        # 127.0.0.1 default would point remote viewers at *their* machine.
        return render_template('index.html',
                               use_webterm=app.config.get('WEBTERM_ENABLED', False),
                               remdev_url=mgrs()['config'].remdev_url)

    # ---- Config ----

    @app.route('/api/config')
    def get_config():
        return jsonify(mgrs()['config'].to_dict())

    @app.route('/api/config/help')
    def get_config_help():
        import os
        cfg_dir = os.path.dirname(mgrs()['config'].config_path)
        help_path = os.path.join(cfg_dir, 'config_yaml_help.md')
        try:
            with open(help_path, 'r', encoding='utf-8') as f:
                return jsonify({'content': f.read()})
        except FileNotFoundError:
            return jsonify({'content': '# Help file not found\n\n`config_yaml_help.md` missing from repo root.'})

    @app.route('/api/config/yaml')
    def get_config_yaml():
        content = mgrs()['config'].read_raw_yaml()
        return jsonify({'content': content})

    @app.route('/api/config/yaml', methods=['POST'])
    def save_config_yaml():
        data = request.get_json() or {}
        content = data.get('content', '')
        ok, err = mgrs()['config'].write_raw_yaml(content)
        if ok:
            return jsonify({'status': 'ok'})
        return jsonify({'error': err}), 400

    # ---- Agents ----

    @app.route('/api/agents')
    def list_agents():
        runtime = mgrs()['runtime']
        runtime.refresh_all()
        agents = [a.to_dict() for a in mgrs()['registry'].all()]
        return jsonify({'agents': agents})

    @app.route('/api/agents/<name>')
    def get_agent(name):
        registry = mgrs()['registry']
        agent = registry.get(name)
        if not agent:
            return jsonify({'error': 'Not found'}), 404
        mgrs()['runtime'].refresh_status(name)
        sessions = mgrs()['sessions'].list_for_agent(name)
        d = agent.to_dict()
        d['sessions'] = sessions
        return jsonify(d)

    # ---- Agent lifecycle ----

    @app.route('/api/agents/<name>/start', methods=['POST'])
    def start_agent(name):
        ok, msg = mgrs()['runtime'].start(name)
        if ok:
            return jsonify({'status': 'ok', 'message': msg})
        return jsonify({'status': 'error', 'message': msg}), 400

    @app.route('/api/agents/<name>/stop', methods=['POST'])
    def stop_agent(name):
        ok, msg = mgrs()['runtime'].stop(name)
        if ok:
            return jsonify({'status': 'ok', 'message': msg})
        return jsonify({'status': 'error', 'message': msg}), 400

    @app.route('/api/agents/<name>/restart', methods=['POST'])
    def restart_agent(name):
        ok, msg = mgrs()['runtime'].restart(name)
        if ok:
            return jsonify({'status': 'ok', 'message': msg})
        return jsonify({'status': 'error', 'message': msg}), 400

    @app.route('/api/agents/<name>/status')
    def agent_status(name):
        status = mgrs()['runtime'].get_status(name)
        if status is None:
            return jsonify({'error': 'Not found'}), 404
        return jsonify({'agent': name, 'status': status})

    # ---- README ----

    @app.route('/api/agents/<name>/readme')
    def get_readme(name):
        content, err = mgrs()['readme'].read(name)
        if err:
            return jsonify({'error': err}), 404
        return jsonify({'agent': name, 'content': content})

    @app.route('/api/agents/<name>/readme', methods=['POST'])
    def save_readme(name):
        data = request.get_json() or {}
        content = data.get('content', '')
        ok, err = mgrs()['readme'].write(name, content)
        if ok:
            return jsonify({'status': 'ok'})
        return jsonify({'error': err}), 400

    # ---- Agent file browser (any .md within agent folder) ----

    @app.route('/api/agents/<name>/file')
    def get_file(name):
        rel_path = request.args.get('path', '')
        if not rel_path:
            return jsonify({'error': 'path required'}), 400
        content, err = mgrs()['readme'].read_file(name, rel_path)
        if err:
            return jsonify({'error': err}), 404
        return jsonify({'agent': name, 'path': rel_path, 'content': content})

    @app.route('/api/agents/<name>/file', methods=['POST'])
    def save_file(name):
        data = request.get_json() or {}
        rel_path = data.get('path', '')
        content  = data.get('content', '')
        if not rel_path:
            return jsonify({'error': 'path required'}), 400
        ok, err = mgrs()['readme'].write_file(name, rel_path, content)
        if ok:
            return jsonify({'status': 'ok'})
        return jsonify({'error': err}), 400

    # ---- Sessions ----

    @app.route('/api/sessions')
    def list_sessions():
        sessions = mgrs()['sessions'].list_all()
        return jsonify({'sessions': sessions})

    @app.route('/api/sessions', methods=['POST'])
    def create_session():
        data = request.get_json() or {}
        agent_name = data.get('agent', '')
        kind = data.get('kind', 'shell')
        if not agent_name:
            return jsonify({'error': 'agent required'}), 400
        result, err = mgrs()['sessions'].create(agent_name, kind)
        if err:
            return jsonify({'error': err}), 400
        return jsonify({'status': 'ok', 'session': result})

    @app.route('/api/sessions/reset', methods=['POST'])
    def reset_sessions():
        """Kill all tmux sessions and PTY connections."""
        all_sessions = mgrs()['sessions'].list_all()
        mgrs()['pty'].cleanup_all()
        for sid in all_sessions:
            mgrs()['sessions'].kill(sid)
        return jsonify({'status': 'ok', 'killed': len(all_sessions)})

    @app.route('/api/sessions/<path:session_id>', methods=['DELETE'])
    def kill_session(session_id):
        mgrs()['pty'].cleanup(session_id)
        ok = mgrs()['sessions'].kill(session_id)
        if ok:
            return jsonify({'status': 'ok'})
        return jsonify({'error': 'Session not found'}), 404
