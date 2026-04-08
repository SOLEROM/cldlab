FROM cldimg-login:latest

RUN date >> /home/user/.create_time
# install any additional dependencies here, e.g.:
# RUN apt-get update && apt-get install -y <package-name>


RUN pip install graphifyy
RUN /home/user/.local/bin/graphify install --platform claude