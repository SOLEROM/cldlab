# Dockerfile
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    curl git jq tree ca-certificates sudo \
    python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20 LTS (Ubuntu's default is too old)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Create non-root user with passwordless sudo
RUN useradd -m -s /bin/bash user && echo "user ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

USER user
WORKDIR /home/user

# Clean default HOME noise
RUN mkdir -p /home/user/.claude

# Auto-source ~/.aliases if present
RUN echo '[ -f ~/.aliases ] && source ~/.aliases' >> /home/user/.bashrc

CMD ["/bin/bash"]
