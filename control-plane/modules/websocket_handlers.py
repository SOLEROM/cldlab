"""
SocketIO event handlers for terminal I/O.
"""
import logging
from flask import request
from flask_socketio import emit, join_room, leave_room

logger = logging.getLogger('ws')


def register_websocket_handlers(socketio, app):
    def mgrs():
        return app.config['managers']

    @socketio.on('connect')
    def handle_connect():
        logger.info(f'WS connect  sid={request.sid}')
        emit('connected', {'status': 'ok'})

    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info(f'WS disconnect sid={request.sid}')
        mgrs()['pty'].remove_client_all(request.sid)

    @socketio.on('subscribe')
    def handle_subscribe(data):
        session_name = data.get('session', '')
        cols = int(data.get('cols', 220))
        rows = int(data.get('rows', 50))

        if not session_name:
            emit('error', {'message': 'No session specified'})
            return

        tmux = mgrs()['tmux']
        full = tmux.get_full_name(session_name)

        if not tmux.session_exists(full):
            emit('error', {'message': f'Session {full} does not exist'})
            return

        mgrs()['pty'].resize(full, cols, rows)
        join_room(full)

        conn = mgrs()['pty'].get_or_create(full, request.sid, cols, rows)
        if not conn:
            emit('error', {'message': f'Failed to attach to {full}'})
            return

        mgrs()['pty'].resize(full, cols, rows)
        emit('subscribed', {'session': full})

    @socketio.on('unsubscribe')
    def handle_unsubscribe(data):
        session_name = data.get('session', '')
        if not session_name:
            return
        full = mgrs()['tmux'].get_full_name(session_name)
        leave_room(full)
        mgrs()['pty'].remove_client(full, request.sid)
        emit('unsubscribed', {'session': full})

    @socketio.on('input')
    def handle_input(data):
        session_name = data.get('session', '')
        keys = data.get('data', '')
        if session_name and keys:
            mgrs()['pty'].send_input(session_name, keys)

    @socketio.on('resize')
    def handle_resize(data):
        session_name = data.get('session', '')
        cols = int(data.get('cols', 80))
        rows = int(data.get('rows', 24))
        if session_name:
            mgrs()['pty'].resize(session_name, cols, rows)

    @socketio.on('scroll')
    def handle_scroll(data):
        session_name = data.get('session', '')
        command      = data.get('command', '')   # 'up'|'down'|'page_up'|'page_down'|'top'|'bottom'|'enter'|'exit'
        lines        = int(data.get('lines', 3))
        if not session_name:
            return
        tmux = mgrs()['tmux']
        if command == 'enter':
            tmux.enter_copy_mode(session_name)
        elif command == 'exit':
            tmux.exit_copy_mode(session_name)
        elif command in ('up', 'down', 'page_up', 'page_down', 'top', 'bottom'):
            tmux.scroll(session_name, command, lines)

    @socketio.on('ping_server')
    def handle_ping():
        emit('pong_server', {})
