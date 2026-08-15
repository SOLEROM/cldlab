#!/usr/bin/env python3
"""
Claude Control Plane — web UI for Docker-based Claude CLI experiments.
"""
import os
import sys
import atexit
import logging
import warnings

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, SCRIPT_DIR)

warnings.filterwarnings('ignore', category=DeprecationWarning)
# threading async mode: plain threads, no monkey-patching; real WebSockets
# are provided by the simple-websocket package (see requirements.txt).
ASYNC_MODE = 'threading'

from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

from modules.config_manager import ConfigManager
from modules.agent_registry import AgentRegistry
from modules.agent_runtime import AgentRuntime
from modules.tmux_manager import TmuxManager
from modules.pty_bridge import PtyBridge
from modules.readme_manager import ReadmeManager
from modules.session_manager import SessionManager
from modules.routes import register_routes
from modules.websocket_handlers import register_websocket_handlers

def _setup_logging(debug=False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(SCRIPT_DIR, 'runtime', 'logs', 'server.log')),
        ]
    )

logger = logging.getLogger('server')


def create_app(config_path=None, debug=False):
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    app.config['SECRET_KEY'] = os.urandom(24)
    CORS(app)

    # Terminal stack: the shared webterm library is the default;
    # CLDLAB_WEBTERM=0 falls back to the legacy native terminal.
    use_webterm = os.environ.get('CLDLAB_WEBTERM', '1') == '1'
    app.config['WEBTERM_ENABLED'] = use_webterm

    socketio = SocketIO(app, cors_allowed_origins='*', async_mode=ASYNC_MODE)

    cfg = ConfigManager(config_path)
    registry = AgentRegistry(cfg)
    runtime = AgentRuntime(registry, socketio, skip_docker=debug)
    tmux = TmuxManager(cfg)
    pty = PtyBridge(tmux, socketio)
    readme = ReadmeManager(registry)
    sessions = SessionManager(registry, runtime, tmux)

    app.config['managers'] = {
        'config': cfg,
        'registry': registry,
        'runtime': runtime,
        'tmux': tmux,
        'pty': pty,
        'readme': readme,
        'sessions': sessions,
    }

    register_routes(app)

    webterm_state = None
    if use_webterm:
        try:
            from modules.webterm_integration import init_webterm
            webterm_state = init_webterm(app, socketio, cfg, registry, runtime)
        except Exception:
            # Missing/broken webterm must not take the app down — fall back to
            # the legacy terminal and say loudly how to fix it.
            logger.exception(
                'webterm terminal unavailable — falling back to the legacy '
                'terminal. Fix with: .venv/bin/python3 -m pip install '
                '-r control-plane/requirements.txt')
            app.config['WEBTERM_ENABLED'] = False

    if webterm_state is not None:
        def cleanup():
            logger.info('Cleaning up webterm PTY connections...')
            webterm_state.pty.cleanup_all()
    else:
        register_websocket_handlers(socketio, app)

        def cleanup():
            logger.info('Cleaning up PTY connections...')
            pty.cleanup_all()

    atexit.register(cleanup)
    return app, socketio


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Claude Control Plane')
    parser.add_argument('--config', default=None, help='Path to config.yaml')
    parser.add_argument('--host', default=None)
    parser.add_argument('--port', type=int, default=None)
    parser.add_argument('--public', action='store_true', help='Bind to 0.0.0.0')
    parser.add_argument('--debug', action='store_true', help='Debug mode: skip docker checks, enable auto-reload')
    args = parser.parse_args()

    _setup_logging(args.debug)
    app, socketio = create_app(args.config, debug=args.debug)

    cfg = app.config['managers']['config']
    host = '0.0.0.0' if args.public else (args.host or cfg.host)
    port = args.port or cfg.port

    print(f"""
╔══════════════════════════════════════════════════════╗
║         Claude Control Plane                         ║
╠══════════════════════════════════════════════════════╣
║  Agents:  {len(app.config['managers']['registry'].all()):>3}                                       ║
║  Host:    {host:<43}║
║  Port:    {port:<43}║
╚══════════════════════════════════════════════════════╝
""")
    logger.info(f'Starting server on {host}:{port}' + (' [DEBUG]' if args.debug else ''))
    # threading mode serves through Werkzeug: allow_unsafe_werkzeug is
    # required outside debug; never pass debug=True (reloader double-starts)
    socketio.run(app, host=host, port=port, debug=False,
                 use_reloader=False, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    main()
