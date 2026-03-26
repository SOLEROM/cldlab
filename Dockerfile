# Dockerfile
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    curl git jq tree ca-certificates \
    python3 python3-pip \
    nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Install Claude CLI (adjust package name if needed)
RUN npm install -g @anthropic-ai/claude-cli || true

# Create non-root user
RUN useradd -m user && echo "user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER user
WORKDIR /home/user

# Clean default HOME noise
RUN mkdir -p /home/user/.claude

CMD ["/bin/bash"]
