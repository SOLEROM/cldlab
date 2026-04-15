# security

```
# Quick scan (no install needed)
npx ecc-agentshield scan

# Auto-fix safe issues
npx ecc-agentshield scan --fix

# Deep analysis with three Opus 4.6 agents
npx ecc-agentshield scan --opus --stream

# Generate secure config from scratch
npx ecc-agentshield init
```
What it scans: CLAUDE.md, settings.json, MCP configs, hooks, agent definitions, and skills across 5 categories — secrets detection (14 patterns), permission auditing, hook injection analysis, MCP server risk profiling, and agent config review.




```
/security-scan

```

The --opus flag runs three Claude Opus 4.6 agents in a red-team/blue-team/auditor pipeline. The attacker finds exploit chains, the defender evaluates protections, and the auditor synthesizes both into a prioritized risk assessment. Adversarial reasoning, not just pattern matching.