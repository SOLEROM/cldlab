FROM cldimg-login:latest

RUN date >> /home/user/.create_time
# install any additional dependencies here, e.g.:
# RUN apt-get update && apt-get install -y <package-name>


RUN git clone https://github.com/rohitg00/awesome-claude-code-toolkit.git ~/.claude/plugins/claude-code-toolkit
RUN yes | ~/.claude/plugins/claude-code-toolkit/setup/install.sh