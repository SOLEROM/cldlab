"""
Configuration manager — loads config.yaml and exposes typed fields.
"""
import os
import re

import yaml

# app.remdev_url — the origin of remdev's Claude status-bar service, embedded
# in the header (the shared cldBar kit). Scheme-qualified on purpose: the kit
# refuses anything else, and a bare host would silently resolve against
# cldlab's own page.
REMDEV_URL_RE = re.compile(r'^https?://[^\s/]+/?$')


class ConfigManager:
    def __init__(self, config_path=None):
        if config_path is None:
            # Default: root of the repo (one level up from control-plane/)
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yaml'
            )
        self.config_path = os.path.abspath(config_path)
        self._raw = self._load()

    def _load(self):
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def _app(self):
        return self._raw.get('app', {})

    @property
    def host(self):
        return self._app().get('host', '127.0.0.1')

    @property
    def port(self):
        return int(self._app().get('port', 5080))

    @property
    def tmux_socket(self):
        return self._app().get('tmux_socket', 'claude-control')

    @property
    def session_prefix(self):
        return self._app().get('tmux_prefix', 'cldcc-')

    @property
    def scrollback_limit(self):
        return int(self._app().get('scrollback_limit', 10000))

    @property
    def cld_start_cmd(self):
        return self._app().get('cldStartCmd', 'claude')

    @property
    def remdev_url(self):
        """Pinned origin of remdev's status-bar service, or '' for "derive it".

        Empty is the normal case: the browser then builds the iframe URL from
        whatever address cldlab was opened on. Never default this to
        127.0.0.1 — an iframe src is fetched by the *viewer's* machine.
        """
        return str(self._app().get('remdev_url') or '').strip().rstrip('/')

    @property
    def agents_raw(self):
        return self._raw.get('agents', [])

    def resolve_path(self, rel_path):
        """Resolve a path relative to the config file directory."""
        base = os.path.dirname(self.config_path)
        return os.path.normpath(os.path.join(base, rel_path))

    def read_raw_yaml(self):
        """Return the raw YAML file contents as a string."""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_raw_yaml(self, content):
        """Validate and write new YAML content. Returns (ok, error)."""
        try:
            parsed = yaml.safe_load(content)
            if not isinstance(parsed, dict):
                return False, 'Invalid YAML: top-level must be a mapping'
        except yaml.YAMLError as e:
            return False, f'YAML parse error: {e}'
        # app.remdev_url ends up as an iframe origin. A malformed one leaves
        # an empty header slot and nothing else, so it is caught here — where
        # the editor can show the message — rather than in a browser console.
        remdev_url = (parsed.get('app') or {}).get('remdev_url')
        if str(remdev_url or '').strip() and not REMDEV_URL_RE.match(str(remdev_url)):
            return False, (f"app.remdev_url must be an http(s) origin like "
                           f"'http://station:6005' (got {remdev_url!r})")
        tmp = self.config_path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(content)
        os.replace(tmp, self.config_path)
        # Reload in-memory state
        self._raw = self._load()
        return True, None

    def to_dict(self):
        return {
            'host': self.host,
            'port': self.port,
            'tmux_socket': self.tmux_socket,
            'tmux_prefix': self.session_prefix,
            'config_path': self.config_path,
        }
