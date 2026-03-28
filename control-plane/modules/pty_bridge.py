"""
PTY bridge — forks a PTY that attaches to a tmux session, streams output via SocketIO.
Adapted from ccpan reference.
"""
import os
import pty
import fcntl
import struct
import termios
import select
import threading
import time
import errno
import re
import logging

logger = logging.getLogger('pty_bridge')

OSC_PATTERN = re.compile(
    r'\x1b\]'
    r'(?:10|11|12|4;\d+|104|110|111|112|52;[^\x07\x1b]*)'
    r';[^\x07\x1b]*'
    r'(?:\x07|\x1b\\)'
)
DCS_PATTERN = re.compile(r'\x1bP[^\x1b]*\x1b\\')

# DA2 response leaking from tmux through the PTY:
# e.g.  ESC [ > 0 ; 276 ; 0 c   →  ^[[>0;276;0c
DA2_PATTERN = re.compile(r'\x1b\[>[0-9;]*c')
# DA1 response (less common but same root cause):
# e.g.  ESC [ ? 1 ; 2 c
DA1_PATTERN = re.compile(r'\x1b\[\?[0-9;]*c')


def _filter(data):
    data = OSC_PATTERN.sub('', data)
    data = DCS_PATTERN.sub('', data)
    data = DA2_PATTERN.sub('', data)
    data = DA1_PATTERN.sub('', data)
    return data


class PtyBridge:
    def __init__(self, tmux_manager, socketio):
        self.tmux = tmux_manager
        self.socketio = socketio
        self.connections = {}   # full_session_name -> conn dict

    def _set_winsize(self, fd, rows, cols):
        winsize = struct.pack('HHHH', rows, cols, 0, 0)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)

    def _spawn(self, full_name, cols=220, rows=50):
        self.tmux.resize_window(full_name, cols, rows)
        time.sleep(0.05)

        pid, master_fd = pty.fork()
        if pid == 0:
            os.environ['TERM'] = 'xterm-256color'
            os.environ.pop('COLORFGBG', None)
            os.execlp('tmux', 'tmux', '-L', self.tmux.config.tmux_socket,
                      'attach', '-t', full_name)
        else:
            flags = fcntl.fcntl(master_fd, fcntl.F_GETFL)
            fcntl.fcntl(master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
            self._set_winsize(master_fd, rows, cols)
            time.sleep(0.1)
            self.tmux.resize_window(full_name, cols, rows)
            return master_fd, pid

    def _start_reader(self, full_name, master_fd):
        stop_event = threading.Event()

        def reader():
            try:
                while not stop_event.is_set():
                    try:
                        readable, _, _ = select.select([master_fd], [], [], 0.05)
                        if readable:
                            try:
                                data = os.read(master_fd, 16384)
                                if data:
                                    decoded = data.decode('utf-8', errors='replace')
                                    filtered = _filter(decoded)
                                    if filtered:
                                        self.socketio.emit('output', {
                                            'session': full_name,
                                            'data': filtered,
                                        }, room=full_name)
                                else:
                                    break
                            except OSError as e:
                                if e.errno in (errno.EIO, errno.EBADF):
                                    break
                                raise
                    except (ValueError, OSError):
                        break
            except Exception as e:
                logger.error(f'PTY reader error for {full_name}: {e}')
            finally:
                if full_name in self.connections:
                    self.connections[full_name]['reader_stopped'] = True

        t = threading.Thread(target=reader, daemon=True)
        t.start()
        return t, stop_event

    def get_or_create(self, session_name, sid, cols=220, rows=50):
        full = self.tmux.get_full_name(session_name)

        if full in self.connections:
            conn = self.connections[full]
            if conn.get('reader_stopped'):
                self.cleanup(full)
            else:
                conn['clients'].add(sid)
                return conn

        if not self.tmux.session_exists(full):
            return None

        master_fd, pid = self._spawn(full, cols, rows)
        reader_thread, stop_event = self._start_reader(full, master_fd)

        self.connections[full] = {
            'master_fd': master_fd,
            'pid': pid,
            'reader_thread': reader_thread,
            'stop_event': stop_event,
            'clients': {sid},
            'reader_stopped': False,
        }
        logger.info(f'PTY connected to {full}')
        return self.connections[full]

    def send_input(self, session_name, data):
        full = self.tmux.get_full_name(session_name)
        if full in self.connections:
            try:
                os.write(self.connections[full]['master_fd'], data.encode('utf-8'))
                return True
            except Exception:
                pass
        return self.tmux.send_keys(full, data)

    def resize(self, session_name, cols, rows):
        full = self.tmux.get_full_name(session_name)
        if full in self.connections:
            try:
                self._set_winsize(self.connections[full]['master_fd'], rows, cols)
            except Exception:
                pass
        self.tmux.resize_window(full, cols, rows)

    def remove_client(self, session_name, sid):
        full = self.tmux.get_full_name(session_name)
        if full not in self.connections:
            return
        conn = self.connections[full]
        conn['clients'].discard(sid)
        if not conn['clients']:
            def delayed():
                time.sleep(5)
                if full in self.connections and not self.connections[full]['clients']:
                    self.cleanup(full)
            threading.Thread(target=delayed, daemon=True).start()

    def cleanup(self, session_name):
        full = self.tmux.get_full_name(session_name)
        if full not in self.connections:
            return
        conn = self.connections.pop(full)
        conn['stop_event'].set()
        try:
            os.close(conn['master_fd'])
        except Exception:
            pass
        try:
            import signal
            os.kill(conn['pid'], signal.SIGTERM)
            os.waitpid(conn['pid'], os.WNOHANG)
        except Exception:
            pass

    def cleanup_all(self):
        for name in list(self.connections):
            self.cleanup(name)

    def remove_client_all(self, sid):
        for name in list(self.connections):
            self.remove_client(name, sid)
