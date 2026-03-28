"""
Agent registry — loads agent definitions from config and tracks runtime state.
"""
import os
import re


VALID_NAME = re.compile(r'^[a-zA-Z0-9_\-]+$')

# Allowed status transitions
STATUS_CONFIGURED = 'configured'
STATUS_STARTING   = 'starting'
STATUS_RUNNING    = 'running'
STATUS_STOPPING   = 'stopping'
STATUS_STOPPED    = 'stopped'
STATUS_ERROR      = 'error'
STATUS_UNKNOWN    = 'unknown'


class Agent:
    def __init__(self, raw, config_manager):
        self.name = raw['name']
        self.type = raw.get('type', 'local_shell')
        rel_path = raw.get('path', f'../agents/{self.name}')
        self.path = config_manager.resolve_path(rel_path)
        self.make_run = raw.get('make_run', '')
        self.make_stop = raw.get('make_stop', '')
        self.readme_file = raw.get('readme', 'README.md')
        self.readme_path = os.path.join(self.path, self.readme_file)
        self.auto_start = raw.get('auto_start', False)
        self.tags = raw.get('tags', [])
        # container name for docker agents (default cldcon-<name>)
        self.container = raw.get('container', f'cldcon-{self.name}')
        # command run by "+ Claude" button — per-agent override, falls back to global app setting
        self.cld_start_cmd = raw.get('cldStartCmd', config_manager.cld_start_cmd)
        self._status = STATUS_UNKNOWN

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    def to_dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'path': self.path,
            'make_run': self.make_run,
            'make_stop': self.make_stop,
            'readme': self.readme_file,
            'auto_start': self.auto_start,
            'tags': self.tags,
            'container': self.container,
            'status': self._status,
        }


class AgentRegistry:
    def __init__(self, config_manager):
        self._agents = {}
        for raw in config_manager.agents_raw:
            name = raw.get('name', '')
            if not name or not VALID_NAME.match(name):
                print(f"[registry] Skipping agent with invalid name: {name!r}")
                continue
            agent = Agent(raw, config_manager)
            self._agents[name] = agent
        print(f"[registry] Loaded {len(self._agents)} agents: {list(self._agents)}")

    def all(self):
        return list(self._agents.values())

    def get(self, name):
        return self._agents.get(name)

    def names(self):
        return list(self._agents.keys())
