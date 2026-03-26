#!/bin/bash
# On first start: copy the read-only template into the container's own ~/.claude
if [ ! -e ~/.claude/.initialized ]; then
    cp -rT /home/user/.claude-tpl ~/.claude
    touch ~/.claude/.initialized
fi
exec "$@"
