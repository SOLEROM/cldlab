"""
Tmux session management — adapted from ccpan reference.
"""
import os
import subprocess
import time
import logging

logger = logging.getLogger('tmux_manager')


class TmuxManager:
    def __init__(self, config):
        self.config = config

    def _run(self, *args, timeout=10):
        cmd = ['tmux', '-L', self.config.tmux_socket] + list(args)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            logger.warning(f'tmux command timed out: {args}')
            # Return a fake failed result
            result = subprocess.CompletedProcess(cmd, returncode=1, stdout='', stderr='timeout')
        return result

    def get_sessions(self):
        """List all sessions with our prefix."""
        result = self._run('list-sessions', '-F', '#{session_name}')
        if result.returncode != 0:
            return []
        prefix = self.config.session_prefix
        return [line for line in result.stdout.strip().split('\n')
                if line and line.startswith(prefix)]

    def session_exists(self, name):
        full = self.get_full_name(name)
        return full in self.get_sessions()

    def get_full_name(self, name):
        prefix = self.config.session_prefix
        return name if name.startswith(prefix) else f'{prefix}{name}'

    def create_session(self, name, cwd=None, shell_cmd=None):
        """Create a new detached tmux session.

        shell_cmd: if provided, becomes the session's direct process (not typed
                   into a host shell).  This prevents 'drop to host shell' when
                   the inner command (e.g. docker exec) exits.
        """
        full = self.get_full_name(name)
        if self.session_exists(full):
            return False, 'Session already exists'

        args = ['new-session', '-d', '-s', full, '-x', '220', '-y', '50']
        if cwd and os.path.isdir(cwd):
            args.extend(['-c', cwd])
        if shell_cmd:
            # Pass command directly so it IS the session process, not typed into a shell
            args.extend(['--', 'bash', '-c', shell_cmd])

        result = self._run(*args)
        if result.returncode != 0:
            logger.error(f'Failed to create session {full}: {result.stderr}')
            return False, result.stderr

        self._run('set-option', '-t', full, 'status', 'off')
        self._run('set-option', '-t', full, 'mouse', 'off')
        self._run('set-option', '-t', full, 'history-limit',
                  str(self.config.scrollback_limit))
        self._run('set-window-option', '-t', full, 'aggressive-resize', 'on')
        self._run('set-option', '-t', full, 'default-terminal', 'xterm-256color')
        self._run('set-option', '-t', full, 'allow-rename', 'off')
        self._run('set-option', '-t', full, 'set-titles', 'off')

        logger.info(f'Created session {full}')
        return True, full

    def destroy_session(self, name):
        full = self.get_full_name(name)
        result = self._run('kill-session', '-t', full)
        return result.returncode == 0

    def resize_window(self, name, cols, rows):
        full = self.get_full_name(name)
        self._run('resize-window', '-t', full, '-x', str(cols), '-y', str(rows))

    def send_keys(self, name, keys):
        full = self.get_full_name(name)
        result = self._run('send-keys', '-t', full, '-l', keys)
        return result.returncode == 0

    def enter_copy_mode(self, name):
        full = self.get_full_name(name)
        self._run('copy-mode', '-t', full)

    def exit_copy_mode(self, name):
        full = self.get_full_name(name)
        self._run('send-keys', '-t', full, 'q')

    def scroll(self, name, direction, lines=3):
        """Scroll inside tmux copy-mode."""
        full = self.get_full_name(name)
        if direction == 'up':
            self._run('send-keys', '-t', full, '-N', str(lines), 'C-y')
        elif direction == 'down':
            self._run('send-keys', '-t', full, '-N', str(lines), 'C-e')
        elif direction == 'page_up':
            self._run('send-keys', '-t', full, 'C-b')
        elif direction == 'page_down':
            self._run('send-keys', '-t', full, 'C-f')
        elif direction == 'top':
            self._run('send-keys', '-t', full, 'g')
        elif direction == 'bottom':
            self._run('send-keys', '-t', full, 'G')

    def get_scrollback(self, name, start_line=-10000, end_line=None):
        full = self.get_full_name(name)
        args = ['capture-pane', '-t', full, '-p', '-e', '-J', '-S', str(start_line)]
        if end_line is not None:
            args.extend(['-E', str(end_line)])
        result = self._run(*args)
        return result.stdout if result.returncode == 0 else ''

    def get_history_size(self, name):
        full = self.get_full_name(name)
        result = self._run('display-message', '-t', full, '-p', '#{history_size}')
        if result.returncode == 0:
            try:
                return int(result.stdout.strip())
            except Exception:
                pass
        return 0
