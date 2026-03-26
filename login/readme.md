# login layer

Extends `cldimg-base`. Purpose: persistent login sessions (claude.ai, GitHub, etc).

## Build

```
make login    # from root (builds base + login, spins container)
```

## Notes

- `~/.claude` is **not** volume-mounted — kept private inside the container so login sessions/credentials stay isolated from the host
- Use `make merge NAME=login` to snapshot login state into `cldimg-login` after authenticating
- Use `make run NAME=login` to re-enter and resume the saved session
