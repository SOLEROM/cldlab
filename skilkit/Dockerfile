FROM cldimg-login:latest

RUN date >> /home/user/.create_time
# install any additional dependencies here, e.g.:
RUN sudo apt-get update && sudo apt-get install -y zip
RUN sudo rm -rf /var/lib/apt/lists/*

# ---- BUN (user-scoped) ----
ENV BUN_INSTALL=/home/user/.bun
ENV PATH=/home/user/.bun/bin:$PATH
RUN curl -fsSL https://bun.sh/install | bash


RUN sudo npm install -g skillkit