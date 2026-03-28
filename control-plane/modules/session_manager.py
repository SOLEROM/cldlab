"""
Session manager — creates and tracks tmux-backed terminal sessions per agent.
Session naming: <tmux_prefix><agent_name>[-<kind>][-<index>]
"""
import re
import logging
from .agent_registry import STATUS_RUNNING

logger = logging.getLogger('session_manager')

VALID = re.compile(r'^[a-zA-Z0-9_\-]+$')

SESSION_KINDS = ('shell', 'claude', 'exec')


class SessionManager:
    def __init__(self, agent_registry, agent_runtime, tmux_manager):
        self.registry = agent_registry
        self.runtime = agent_runtime
        self.tmux = tmux_manager

    def _session_name(self, agent_name, kind, index=None):
        """Build session name WITHOUT prefix (tmux_manager adds it)."""
        parts = [agent_name, kind]
        if index is not None:
            parts.append(str(index))
        return '-'.join(parts)

    def _find_free_index(self, agent_name, kind):
        existing = self.tmux.get_sessions()
        prefix = self.tmux.config.session_prefix
        for i in range(20):
            name = self._session_name(agent_name, kind, i if i > 0 else None)
            full = f'{prefix}{name}'
            if full not in existing:
                return name
        return self._session_name(agent_name, kind, 99)

    def _exec_cmd_for_agent(self, agent, kind):
        """Return the shell command to run as the tmux session's direct process."""
        if agent.type == 'docker':
            if kind == 'claude':
                return f'docker exec -it {agent.container} bash -c "claude || bash"'
            else:
                return f'docker exec -it {agent.container} bash'
        else:
            # local_shell — just start a shell
            return None  # tmux will start default shell in cwd

    def create(self, agent_name, kind='shell'):
        agent = self.registry.get(agent_name)
        if not agent:
            return None, 'Agent not found'

        if kind not in SESSION_KINDS:
            kind = 'shell'

        # For docker agents, container must be running (except we allow creating session first)
        if agent.type == 'docker':
            status = self.runtime.refresh_status(agent_name)
            if status != STATUS_RUNNING:
                return None, f'Container not running (status={status}). Start the agent first.'

        session_name = self._find_free_index(agent_name, kind)
        cwd = agent.path
        shell_cmd = self._exec_cmd_for_agent(agent, kind)

        ok, result = self.tmux.create_session(session_name, cwd=cwd, shell_cmd=shell_cmd)
        if not ok:
            return None, result

        full_name = self.tmux.get_full_name(session_name)
        logger.info(f'Created session {full_name} for agent {agent_name} kind={kind}')
        return {
            'session_id': full_name,
            'agent': agent_name,
            'kind': kind,
        }, None

    def list_for_agent(self, agent_name):
        prefix = self.tmux.config.session_prefix
        all_sessions = self.tmux.get_sessions()
        return [s for s in all_sessions if s.startswith(f'{prefix}{agent_name}-')]

    def list_all(self):
        return self.tmux.get_sessions()

    def kill(self, session_id):
        return self.tmux.destroy_session(session_id)
