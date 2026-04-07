"""
Agent lifecycle management — start, stop, restart, status via docker commands.
"""
import json
import subprocess
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from .agent_registry import (
    STATUS_CONFIGURED, STATUS_STARTING, STATUS_RUNNING,
    STATUS_STOPPING, STATUS_STOPPED, STATUS_ERROR, STATUS_UNKNOWN
)
from .command_runner import run_sync, run_async

logger = logging.getLogger('agent_runtime')


def _docker_container_status(container_name):
    """Return docker container status string or None if not found."""
    result = run_sync(
        ['docker', 'inspect', '--format', '{{.State.Status}}', container_name],
        timeout=5
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _inspect_container(container_name):
    """Full docker inspect, returns first element parsed or None."""
    result = run_sync(['docker', 'inspect', container_name], timeout=5)
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout.strip())
        return data[0] if data else None
    except Exception:
        return None


class AgentRuntime:
    def __init__(self, agent_registry, socketio=None, skip_docker=False):
        self.registry = agent_registry
        self.socketio = socketio
        self.skip_docker = skip_docker  # debug mode: skip docker inspect calls

    def _emit_status(self, agent_name, status):
        if self.socketio:
            self.socketio.emit('agent_status', {'agent': agent_name, 'status': status})

    def refresh_status(self, name):
        """Refresh status for a single agent from docker inspect."""
        agent = self.registry.get(name)
        if not agent:
            return STATUS_UNKNOWN

        if agent.type == 'local_shell':
            agent.status = STATUS_RUNNING
            return agent.status

        if self.skip_docker:
            return agent.status  # return cached, no subprocess

        docker_state = _docker_container_status(agent.container)
        if docker_state is None:
            agent.status = STATUS_CONFIGURED
        elif docker_state == 'running':
            agent.status = STATUS_RUNNING
        elif docker_state in ('exited', 'created', 'dead'):
            agent.status = STATUS_STOPPED
        elif docker_state == 'paused':
            agent.status = STATUS_STOPPED
        else:
            agent.status = STATUS_UNKNOWN
        return agent.status

    def refresh_all(self):
        import time
        t0 = time.time()
        agents = self.registry.all()
        if self.skip_docker:
            logger.debug(f'refresh_all: skipped (debug mode), {len(agents)} agents')
            return
        with ThreadPoolExecutor(max_workers=min(len(agents), 8)) as pool:
            futures = {pool.submit(self.refresh_status, a.name): a.name for a in agents}
            for f in as_completed(futures):
                try:
                    f.result()
                except Exception as e:
                    logger.warning(f'refresh_status failed for {futures[f]}: {e}')
        logger.info(f'refresh_all: {len(agents)} agents in {(time.time()-t0)*1000:.1f}ms')

    def _recreate_with_share(self, agent):
        """Recreate a container preserving its config but adding/updating the share mount."""
        info = _inspect_container(agent.container)
        if not info:
            return False, f'Cannot inspect {agent.container}'

        image = info['Config']['Image']
        tty = info['Config'].get('Tty', False)
        stdin_open = info['Config'].get('OpenStdin', False)
        env = info['Config'].get('Env', [])
        mounts = info.get('Mounts', [])

        result = run_sync(['docker', 'rm', '-f', agent.container], timeout=15)
        if result.returncode != 0:
            return False, f'Failed to remove container: {result.stderr}'

        cmd = ['docker', 'create', '--name', agent.container]
        if tty:
            cmd.append('-t')
        if stdin_open:
            cmd.append('-i')
        for e in env:
            cmd += ['-e', e]
        for m in mounts:
            src = m.get('Source', '')
            dst = m.get('Destination', '')
            if not src or not dst:
                continue
            if dst == '/home/user/share':
                continue  # will be replaced below
            mode = 'rw' if m.get('RW', True) else 'ro'
            cmd += ['-v', f'{src}:{dst}:{mode}']
        cmd += ['-v', f'{agent.share}:/home/user/share:rw']
        cmd.append(image)

        result = run_sync(cmd, timeout=30)
        if result.returncode != 0:
            return False, f'Failed to recreate container: {result.stderr}'

        logger.info(f'Recreated {agent.container} with share {agent.share} → /home/user/share')
        return True, f'Recreated with share {agent.share}'

    def start(self, name):
        """Start a docker agent container (non-interactive detached start)."""
        agent = self.registry.get(name)
        if not agent:
            return False, 'Agent not found'
        if agent.type == 'local_shell':
            agent.status = STATUS_RUNNING
            return True, 'local_shell always running'

        current = self.refresh_status(name)
        if current == STATUS_RUNNING:
            return True, 'Already running'

        # If share is configured, ensure it is mounted — recreate container if not
        if agent.share and current != STATUS_CONFIGURED:
            info = _inspect_container(agent.container)
            if info:
                mounted = any(
                    m.get('Destination') == '/home/user/share' and m.get('Source') == agent.share
                    for m in info.get('Mounts', [])
                )
                if not mounted:
                    logger.info(f'Share mount missing for {name}, recreating container')
                    ok, msg = self._recreate_with_share(agent)
                    if not ok:
                        agent.status = STATUS_ERROR
                        self._emit_status(name, STATUS_ERROR)
                        return False, msg

        agent.status = STATUS_STARTING
        self._emit_status(name, STATUS_STARTING)

        def on_done(result):
            if result.success:
                agent.status = STATUS_RUNNING
            else:
                agent.status = STATUS_ERROR
                logger.error(f"Start failed for {name}: {result.stderr}")
            self._emit_status(name, agent.status)

        # docker start (detached) — starts existing container
        run_async(['docker', 'start', agent.container], callback=on_done, timeout=30)
        return True, f'Starting {agent.container}'

    def stop(self, name):
        """Stop a docker agent container."""
        agent = self.registry.get(name)
        if not agent:
            return False, 'Agent not found'
        if agent.type == 'local_shell':
            return True, 'local_shell cannot be stopped'

        current = self.refresh_status(name)
        if current == STATUS_CONFIGURED:
            return False, 'Container does not exist'
        if current == STATUS_STOPPED:
            return True, 'Already stopped'

        agent.status = STATUS_STOPPING
        self._emit_status(name, STATUS_STOPPING)

        def on_done(result):
            if result.success:
                agent.status = STATUS_STOPPED
            else:
                agent.status = STATUS_ERROR
                logger.error(f"Stop failed for {name}: {result.stderr}")
            self._emit_status(name, agent.status)

        run_async(['docker', 'stop', agent.container], callback=on_done, timeout=30)
        return True, f'Stopping {agent.container}'

    def restart(self, name):
        """Restart a docker agent container."""
        agent = self.registry.get(name)
        if not agent:
            return False, 'Agent not found'
        if agent.type == 'local_shell':
            return True, 'local_shell always running'

        agent.status = STATUS_STOPPING
        self._emit_status(name, STATUS_STOPPING)

        def on_done(result):
            if result.success:
                agent.status = STATUS_RUNNING
            else:
                agent.status = STATUS_ERROR
            self._emit_status(name, agent.status)

        run_async(['docker', 'restart', agent.container], callback=on_done, timeout=60)
        return True, f'Restarting {agent.container}'

    def get_status(self, name):
        return self.refresh_status(name)
