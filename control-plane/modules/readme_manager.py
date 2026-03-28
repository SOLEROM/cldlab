"""
README manager — read/write per-agent README.md files safely.
"""
import os
import logging

logger = logging.getLogger('readme_manager')

MAX_SIZE = 1 * 1024 * 1024  # 1 MB

DEFAULT_TEMPLATE = """\
# {name}

## Purpose

## Setup

## Plugins / Skills

## Notes

## Experiments
"""


class ReadmeManager:
    def __init__(self, agent_registry):
        self.registry = agent_registry

    def _safe_path(self, agent_name):
        agent = self.registry.get(agent_name)
        if not agent:
            return None, 'Agent not found'
        path = agent.readme_path
        # Guard against path traversal
        if not os.path.abspath(path).startswith(os.path.abspath(agent.path)):
            return None, 'Path traversal rejected'
        return path, None

    def _resolve_file(self, agent_name, rel_path):
        """Resolve a relative file path within the agent folder. Returns (abs_path, error)."""
        agent = self.registry.get(agent_name)
        if not agent:
            return None, 'Agent not found'
        # rel_path must be a .md file and must not escape the agent root
        abs_path = os.path.normpath(os.path.join(agent.path, rel_path))
        if not abs_path.startswith(os.path.abspath(agent.path) + os.sep) and \
           abs_path != os.path.abspath(agent.path):
            return None, 'Path traversal rejected'
        if not abs_path.endswith('.md'):
            return None, 'Only .md files are supported'
        return abs_path, None

    def read_file(self, agent_name, rel_path):
        """Read any .md file relative to the agent folder."""
        abs_path, err = self._resolve_file(agent_name, rel_path)
        if err:
            return None, err
        if not os.path.exists(abs_path):
            return None, f'File not found: {rel_path}'
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                data = f.read(MAX_SIZE + 1)
            if len(data) > MAX_SIZE:
                return None, 'File too large'
            return data, None
        except Exception as e:
            return None, str(e)

    def write_file(self, agent_name, rel_path, content):
        """Write any .md file relative to the agent folder."""
        if len(content.encode('utf-8')) > MAX_SIZE:
            return False, 'Content too large'
        abs_path, err = self._resolve_file(agent_name, rel_path)
        if err:
            return False, err
        try:
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            self._write_atomic(abs_path, content)
            return True, None
        except Exception as e:
            return False, str(e)

    def read(self, agent_name):
        path, err = self._safe_path(agent_name)
        if err:
            return None, err
        if not os.path.exists(path):
            content = DEFAULT_TEMPLATE.format(name=agent_name)
            self._write_atomic(path, content)
            return content, None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = f.read(MAX_SIZE + 1)
            if len(data) > MAX_SIZE:
                return None, 'README too large'
            return data, None
        except Exception as e:
            return None, str(e)

    def write(self, agent_name, content):
        if len(content.encode('utf-8')) > MAX_SIZE:
            return False, 'Content too large'
        path, err = self._safe_path(agent_name)
        if err:
            return False, err
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self._write_atomic(path, content)
            return True, None
        except Exception as e:
            return False, str(e)

    def _write_atomic(self, path, content):
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(content)
        os.replace(tmp, path)
