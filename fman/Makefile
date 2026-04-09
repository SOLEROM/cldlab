IMG_PREFIX ?= cldimg
CON_PREFIX ?= cldcon
NAME       ?= fman

.PHONY: build run

.DEFAULT_GOAL := build

build:
	docker build -t $(IMG_PREFIX)-$(NAME) .

run:
	xhost +local:docker 2>/dev/null || true
	docker run -it --rm \
		--name $(CON_PREFIX)-$(NAME) \
		-e DISPLAY=$(DISPLAY) \
		-e ANTHROPIC_API_KEY=$(ANTHROPIC_API_KEY) \
		-e CLDLAB_NAME=$(NAME) \
		--network host \
		-v /tmp/.X11-unix:/tmp/.X11-unix:rw \
		--shm-size=2g \
		$(IMG_PREFIX)-$(NAME)
