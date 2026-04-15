FROM cldimg-login:latest

RUN date >> /home/user/.create_time
#############################################################################
############################ GENERAL  ###########################################
#############################################################################
## general tools 
# RUN sudo apt-get update && sudo apt-get install -y wget git vim tmux h
## github cli
# RUN sudo mkdir -p -m 755 /etc/apt/keyrings \
# 	&& out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
# 	&& cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
# 	&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
# 	&& sudo mkdir -p -m 755 /etc/apt/sources.list.d \
# 	&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
# 	&& sudo apt update \
# 	&& sudo apt install gh -y

#############################################################################
########################   PROJECT SPECIFIC   ###############################
#############################################################################
# https://github.com/yeachan-heo/oh-my-claudecode
RUN sudo npm i -g oh-my-claude-sisyphus@latest
RUN	omc setup