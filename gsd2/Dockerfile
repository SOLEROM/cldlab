FROM cldimg-login:latest

RUN date >> /home/user/.create_time

# Install Node.js 22
RUN sudo curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    sudo apt-get install -y nodejs

# Install gsd-pi globally
RUN sudo npm install -g gsd-pi
