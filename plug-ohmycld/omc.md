# omc

## team

```
[plug-ohmycld] user:~$ omc team
Usage: omc team [N:agent-type[:role]] [--new-window] "<task description>"
       omc team status <team-name>
       omc team shutdown <team-name> [--force]
       omc team api <operation> [--input <json>] [--json]
       omc team api --help

Examples:
  omc team 3:claude "fix failing tests"
  omc team 2:codex:architect "design auth system"
  omc team 1:gemini:executor "implement feature"
  omc team 1:codex,1:gemini "compare approaches"
  omc team 2:codex "review auth flow" --new-window
  omc team status fix-failing-tests
  omc team shutdown fix-failing-tests
  omc team api send-message --input '{"team_name":"my-team","from_worker":"worker-1","to_worker":"leader-fixed","body":"ACK"}' --json

Roles (optional): architect, executor, planner, analyst, critic, debugger, verifier,
  code-reviewer, security-reviewer, test-engineer, debugger, designer, writer, scientist
[plug-ohmycld] user:~$ 

```


## usage

```
[plug-ohmycld] user:~$ omc wait

🕐 Rate Limit Status

✓ Not rate limited

```
