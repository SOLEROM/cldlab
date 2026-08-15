"""
webterm pilot integration (feature flag: CLDLAB_WEBTERM=1).

Maps cldlab's agent model onto the shared webterm library: the spawn logic
that lived in session_manager._exec_cmd_for_agent moves here as an argv-based
SpawnSpec (no shell-string interpolation), and the library owns everything
else (PTY, transport, rendering, security).

Same tmux socket + prefix as the legacy stack, so live sessions survive
flipping the flag in either direction.
"""
import json
import logging
import os

import webterm
from webterm import SpawnError, SpawnSpec, TerminalConfig

from .agent_registry import STATUS_RUNNING

logger = logging.getLogger('webterm_integration')

SESSION_KINDS = ('shell', 'claude', 'exec')
# Default terminal trust: the tailnet — cldlab's actual perimeter under
# --public — plus loopback, which the library always accepts. The LAN the box
# also sits on is deliberately not included. Override per host with
# CLDLAB_WEBTERM_TRUSTED_NETS="cidr,cidr" (empty value = loopback-only).
DEFAULT_TRUSTED_NETS = webterm.TAILSCALE_CGNAT
TERM_FONT = "'JetBrains Mono','Fira Code','Cascadia Code','Courier New',monospace"


def _argv_for_agent(agent, kind):
    """The command that becomes the tmux session's root process (argv)."""
    if agent.type != 'docker':
        return None  # local_shell: tmux starts the default shell in cwd
    base = ['docker', 'exec', '-it', '-e', f'CLDLAB_NAME={agent.name}', agent.container]
    if kind == 'claude':
        # cld_start_cmd stays a bash -c string *inside* the container, same as
        # today; the outer interpolation into the host tmux command is gone.
        return base + ['bash', '-c', f'{agent.cld_start_cmd} || bash']
    return base + ['bash']


def make_spawn_resolver(registry, runtime):
    def resolver(payload: dict) -> SpawnSpec:
        name = payload.get('agent', '')
        kind = payload.get('kind', 'shell')
        if kind not in SESSION_KINDS:
            kind = 'shell'
        agent = registry.get(name)
        if agent is None:
            raise SpawnError('Agent not found')
        if agent.type == 'docker':
            status = runtime.refresh_status(name)
            if status != STATUS_RUNNING:
                raise SpawnError(
                    f'Container not running (status={status}). Start the agent first.')
        return SpawnSpec(
            tmux_name=f'{name}-{kind}',
            cwd=agent.path,
            command=_argv_for_agent(agent, kind),
            label=f'{name}-{kind}',
            metadata={'agent': name, 'kind': kind},
        )
    return resolver


def _load_term_themes():
    """Reuse cldlab's terminal-themes.json so theme names match the app theme."""
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                        'static', 'terminal-themes.json')
    try:
        with open(path, encoding='utf-8') as fh:
            themes = json.load(fh)
        themes.pop('_comment', None)
        return themes
    except (OSError, ValueError) as exc:
        logger.warning('terminal-themes.json not usable (%s); library defaults apply', exc)
        return {}


def _trusted_networks():
    raw = os.environ.get('CLDLAB_WEBTERM_TRUSTED_NETS', DEFAULT_TRUSTED_NETS)
    return tuple(net.strip() for net in raw.split(',') if net.strip())


def init_webterm(app, socketio, cfg, registry, runtime):
    insecure_lan = os.environ.get('CLDLAB_WEBTERM_LAN', '0') == '1'
    trusted_networks = _trusted_networks()
    config = TerminalConfig(
        tmux_socket=cfg.tmux_socket,
        tmux_prefix=cfg.session_prefix,
        scrollback=cfg.scrollback_limit,
        history_limit=cfg.scrollback_limit,
        font_family=TERM_FONT,
        font_size=13,
        disconnect_grace_seconds=30,
        themes=_load_term_themes(),
        # explicit, visible opt-in for LAN exposure without auth (--public)
        allow_insecure_lan=insecure_lan,
        trusted_networks=trusted_networks,
    )
    state = webterm.init_app(app, socketio,
                             config=config,
                             spawn_resolver=make_spawn_resolver(registry, runtime))
    if insecure_lan:
        auth_desc = 'insecure-lan'
    elif trusted_networks:
        auth_desc = 'loopback+' + ','.join(trusted_networks)
    else:
        auth_desc = 'loopback-only'
    logger.info('webterm pilot enabled (socket=%s prefix=%s auth=%s)',
                cfg.tmux_socket, cfg.session_prefix, auth_desc)
    return state
