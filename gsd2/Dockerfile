FROM cldimg-login:latest

RUN date >> /home/user/.create_time

# Install Node.js 22
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && \
    sudo apt-get install -y nodejs

# Install gsd-pi globally
RUN sudo npm install -g gsd-pi
