FROM cldimg-login:latest

# -------------------------
# ROOT PHASE (system setup)
# -------------------------
USER root

RUN date >> /home/user/.create_time

# base deps
RUN apt-get update && apt-get install -y \
    zip curl git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# playwright system deps (must be root)
RUN npx playwright install-deps chromium

# -------------------------
# USER PHASE (app setup)
# -------------------------
USER user
WORKDIR /home/user

# ---- BUN (user-scoped) ----
ENV BUN_INSTALL=/home/user/.bun
ENV PATH=/home/user/.bun/bin:$PATH

RUN curl -fsSL https://bun.sh/install | bash

# fail fast
RUN bun --version

# ---- PLAYWRIGHT (user cache) ----
RUN npx playwright install chromium

# ---- GSTACK ----
RUN git clone --single-branch --depth 1 \
    https://github.com/garrytan/gstack.git \
    /home/user/.claude/skills/gstack

RUN chmod +x /home/user/.claude/skills/gstack/setup

# run setup with explicit PATH
RUN export PATH=/home/user/.bun/bin:$PATH && \
    printf "1\n" | /home/user/.claude/skills/gstack/setup

# -------------------------
# FINAL DEFAULT USER
# -------------------------
USER user
WORKDIR /home/user