FROM cldimg-login:latest

RUN date >> /home/user/.create_time

USER root
## firefox
RUN apt-get update && apt-get install -y --no-install-recommends software-properties-common && \
    add-apt-repository -y ppa:mozillateam/ppa && \
    printf 'Package: firefox*\nPin: release o=LP-PPA-mozillateam\nPin-Priority: 1001\n' > /etc/apt/preferences.d/mozilla-firefox && \
    apt-get update && apt-get install -y --no-install-recommends firefox && \
    rm -rf /var/lib/apt/lists/*
USER user

RUN sudo apt-get update && sudo apt-get install -y xdg-utils mesa-utils \
    libgl1-mesa-dri \
    libgl1-mesa-glx \
    dbus-x11 pandoc
ENV LIBGL_ALWAYS_SOFTWARE=1
ENV MOZ_DISABLE_GPU=1
ENV NO_AT_BRIDGE=1

RUN curl -fsSL https://feynman.is/install | bash
RUN curl -fsSL https://feynman.is/install-skills | bash