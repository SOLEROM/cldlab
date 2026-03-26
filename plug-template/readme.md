# plug-template layer

Extends `cldimg-base`. Add plugin-specific installs to `Dockerfile`.

## Build

```
make plug-template    # from root (builds base + plug-template, spins container)
```

## Contents

- `Dockerfile` — `FROM cldimg-base` + plugin installs
