#!/bin/bash
# On first start: copy ~/.claude.json template into container's own home
if [ ! -e ~/.claude/.initialized ]; then
    cp -rT /home/user/.claude-tpl/dot_claude ~/.claude
    cp /home/user/.claude-tpl/dot_claude.json ~/.claude.json
    touch ~/.claude/.initialized
fi

exec "$@"
