# ===============================
# Claude Overlay Lab — Root Makefile
# ===============================

IMG_PREFIX = cldimg
CON_PREFIX = cldcon
BASE_IMG   = $(IMG_PREFIX)-base

## in case makefile need to read env;
# -include .env
# export

# -------------------------------
# helpers
# -------------------------------

define resolve_container
if docker inspect $(1) >/dev/null 2>&1; then \
	echo $(1); \
elif docker image inspect $(1) >/dev/null 2>&1; then \
	TMP=$(CON_PREFIX)-tmp-$$(date +%s%N); \
	docker create --name $$TMP $(1) >/dev/null; \
	echo $$TMP; \
else \
	echo "ERROR: $(1) not found"; exit 1; \
fi
endef

# -------------------------------
# help (default)
# -------------------------------

.PHONY: help base login new spin run stop merge list cmp diff diff.meta clean clear

.DEFAULT_GOAL := help

help:
	@echo "Claude Overlay Lab"
	@echo ""
	@echo "Layers (build image + spin container)"
	@echo "  make base                                    build base image + spin container"
	@echo "  make login                                   build base+login images + spin container"
	@echo "  make new   NAME=<n>                          copy template → <n>/, build image, spin container"
	@echo ""
	@echo "Environments"
	@echo "  make spin  NAME=<n> SRC=<img> [SHARE=<path>]  spin throwaway container from any image"
	@echo "  make run   NAME=<n> [CMD=<cmd>]                re-enter existing container"
	@echo "  make merge NAME=<n>                            commit container → image"
	@echo ""
	@echo "Inspect"
	@echo "  make list                                    list all managed images and containers"
	@echo "  make cmp  BASE=<n> CON=<n>                  compare OverlayFS trees (base image vs container)"
	@echo "  make diff BASE=<n> CON=<n> [NAME=<folder>]  export container changes to diffs/"
	@echo "  make diff.meta NAME=<n>                      docker diff metadata"
	@echo ""
	@echo "Cleanup"
	@echo "  make stop  [NAME=<n>]                        stop one container or all"
	@echo "  make clean [NAME=<n>]                        remove containers only (one or all)"
	@echo "  make clear [NAME=<n>]                        remove containers + images (one or all)"

# ===============================
# layers
# ===============================

base:
	$(MAKE) -C base IMG_PREFIX=$(IMG_PREFIX)
	$(MAKE) spin NAME=base SRC=$(BASE_IMG)

login:
	if docker image inspect $(IMG_PREFIX)-login >/dev/null 2>&1; then \
		$(MAKE) run NAME=login; \
	else \
		$(MAKE) -C base IMG_PREFIX=$(IMG_PREFIX); \
		$(MAKE) -C login IMG_PREFIX=$(IMG_PREFIX); \
		$(MAKE) spin NAME=login SRC=$(IMG_PREFIX)-login; \
	fi


new:
	@if [ -z "$(NAME)" ]; then echo "Usage: make new NAME=<n>"; exit 1; fi
	@if [ ! -d $(NAME) ]; then \
		cp -r _template $(NAME); \
		sed -i 's/_template/$(NAME)/g' $(NAME)/Makefile; \
		echo "[*] Created $(NAME)/ from template"; \
	fi
	@if [ -f config.yaml ]; then \
		if ! grep -q "container: cldcon-$(NAME)" config.yaml; then \
			printf '\n  - name: $(NAME)\n    path: .\n    type: docker\n    container: cldcon-$(NAME)\n    make_run: "make run NAME=$(NAME)"\n    make_stop: "make stop NAME=$(NAME)"\n    cldStartCmd: "claude --dangerously-skip-permissions"\n    readme: $(NAME)/readme.md\n    auto_start: false\n    tags: [login, plug]\n' >> config.yaml; \
			echo "[*] Added $(NAME) to config.yaml"; \
		else \
			echo "[-] $(NAME) already present in config.yaml"; \
		fi; \
	fi
	$(MAKE) -C $(NAME) IMG_PREFIX=$(IMG_PREFIX)
	$(MAKE) spin NAME=$(NAME) SRC=$(IMG_PREFIX)-$(NAME)


# ===============================
# container operations
# ===============================

# -------------------------------
# list all managed entities
# -------------------------------

list:
	@echo "=== Images ($(IMG_PREFIX)-*) ==="
	@docker images --format "{{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep "^$(IMG_PREFIX)-" | sed 's/^$(IMG_PREFIX)-//' || true
	@echo ""
	@echo "=== Containers running ($(CON_PREFIX)-*) ==="
	@docker ps --format "{{.Names}}\t{{.Status}}\t{{.Image}}" | grep "^$(CON_PREFIX)-" | sed 's/^$(CON_PREFIX)-//' || true
	@echo ""
	@echo "=== Containers stopped ($(CON_PREFIX)-*) ==="
	@docker ps -a --filter "status=exited" --filter "status=created" --format "{{.Names}}\t{{.Status}}\t{{.Image}}" | grep "^$(CON_PREFIX)-" | sed 's/^$(CON_PREFIX)-//' || true

# -------------------------------
# spin throwaway container from any image
# usage: make spin NAME=envA SRC=cldimg-base [SHARE=/path/to/folder]
# -------------------------------

spin:
	@if [ -z "$(NAME)" ] || [ -z "$(SRC)" ]; then echo "Usage: make spin NAME=envA SRC=<img> [SHARE=/path]"; exit 1; fi
	CONT=$(CON_PREFIX)-$(NAME); \
	docker rm -f $$CONT 2>/dev/null || true; \
	docker run -it --name $$CONT \
		-e ANTHROPIC_API_KEY=$(ANTHROPIC_API_KEY) \
		-e CLDLAB_NAME=$(NAME) \
		-v $(CURDIR)/aliases:/home/user/.aliases:rw \
		-v $(CURDIR)/base/claude_tilda_base:/home/user/.claude-tpl:ro \
		$(if $(TILDA),-v $(CURDIR)/$(TILDA):/home/user/.claude) \
		$${proj:+-v $$proj:/proj} \
		$(if $(SHARE),-v $(SHARE):/home/user/share:rw) \
		$(SRC)

# -------------------------------
# run existing container
# usage: make run NAME=envA
# -------------------------------

run:
	@if [ -z "$(NAME)" ]; then echo "Usage: make run NAME=envA [CMD=<command>]"; exit 1; fi
	@CONT=$(CON_PREFIX)-$(NAME); \
	if ! docker inspect $$CONT >/dev/null 2>&1; then \
		echo "Container $$CONT does not exist. Run: make spin NAME=$(NAME) SRC=<img>"; exit 1; \
	fi; \
	if [ -n "$(CMD)" ]; then \
		docker start $$CONT >/dev/null 2>&1 || true; \
		docker exec -it -e CLDLAB_NAME=$(NAME) $$CONT bash -c "$(CMD) || bash"; \
	else \
		docker start $$CONT >/dev/null 2>&1 || true; \
		docker exec -it -e CLDLAB_NAME=$(NAME) $$CONT bash; \
	fi

# -------------------------------
# stop — NAME=x stops one, bare stops all
# -------------------------------

stop:
	@if [ -n "$(NAME)" ]; then \
		docker stop $(CON_PREFIX)-$(NAME) && echo "[*] Stopped $(CON_PREFIX)-$(NAME)"; \
	else \
		RUNNING=$$(docker ps --format "{{.Names}}" | grep "^$(CON_PREFIX)-"); \
		if [ -z "$$RUNNING" ]; then echo "[-] No running $(CON_PREFIX)-* containers"; exit 0; fi; \
		echo "$$RUNNING" | xargs docker stop; \
		echo "[*] Stopped all $(CON_PREFIX)-* containers"; \
	fi

# -------------------------------
# merge (container → image)
# usage: make merge NAME=envA
# -------------------------------

merge:
	@if [ -z "$(NAME)" ]; then echo "Usage: make merge NAME=envA"; exit 1; fi
	CONT=$(CON_PREFIX)-$(NAME); \
	IMG=$(IMG_PREFIX)-$(NAME); \
	docker commit $$CONT $$IMG; \
	echo "[*] Created image $$IMG"

# -------------------------------
# cmp (compare trees)
# usage: make cmp BASE=<name> CON=<name>
# -------------------------------

cmp:
	@if [ -z "$(BASE)" ] || [ -z "$(CON)" ]; then \
		echo "Usage: make cmp BASE=<name> CON=<name>"; exit 1; fi
	@BASE_IMG=$(IMG_PREFIX)-$(BASE); \
	CON_CON=$(CON_PREFIX)-$(CON); \
	BASE_CONT=$$($(call resolve_container,$$BASE_IMG)); \
	CON_CONT=$$($(call resolve_container,$$CON_CON)); \
	BASE_UPPER=$$(docker inspect $$BASE_CONT | jq -r '.[0].GraphDriver.Data.UpperDir'); \
	CON_UPPER=$$(docker inspect $$CON_CONT | jq -r '.[0].GraphDriver.Data.UpperDir'); \
	echo "=== BASE ($(BASE)) ==="; \
	sudo tree $$BASE_UPPER -la || sudo find $$BASE_UPPER; \
	echo ""; \
	echo "=== CON ($(CON)) ==="; \
	sudo tree $$CON_UPPER -la || sudo find $$CON_UPPER

# -------------------------------
# diff (export container changes vs base image)
# usage: make diff BASE=<name> CON=<name> [NAME=folder]
# -------------------------------

diff:
	@if [ -z "$(BASE)" ] || [ -z "$(CON)" ]; then \
		echo "Usage: make diff BASE=<name> CON=<name> [NAME=<folder>]"; exit 1; fi
	@CON_CONT=$(CON_PREFIX)-$(CON); \
	CON_UPPER=$$(docker inspect $$CON_CONT | jq -r '.[0].GraphDriver.Data.UpperDir'); \
	if [ -z "$$CON_UPPER" ] || [ "$$CON_UPPER" = "null" ]; then \
		PID=$$(docker inspect $$CON_CONT | jq -r '.[0].State.Pid'); \
		CON_UPPER=$$(grep -oP 'upperdir=\K[^,]+' /proc/$$PID/mounts 2>/dev/null | head -1); \
	fi; \
	if [ -z "$$CON_UPPER" ] || [ "$$CON_UPPER" = "null" ]; then \
		echo "Error: UpperDir not found for $$CON_CONT — container must be running"; exit 1; \
	fi; \
	if [ -n "$(NAME)" ]; then \
		OUT=diffs/$(NAME); \
	else \
		OUT=diffs/$(CON)_minus_$(BASE)_$$(date +%Y%m%d_%H%M%S); \
	fi; \
	mkdir -p $$OUT; \
	echo "[*] Exporting $(CON) changes (vs $(BASE)) → $$OUT"; \
	sudo rsync -a $$CON_UPPER/ $$OUT/; \
	echo "[*] Done"

# -------------------------------
# metadata diff (docker diff)
# -------------------------------

diff.meta:
	@if [ -z "$(NAME)" ]; then echo "Usage: make diff.meta NAME=envA"; exit 1; fi
	CONT=$(CON_PREFIX)-$(NAME); \
	docker diff $$CONT

# -------------------------------
# clean — remove containers only (NAME=x for one, bare for all)
# -------------------------------

clean:
	@if [ -n "$(NAME)" ]; then \
		CONT=$(CON_PREFIX)-$(NAME); \
		if docker inspect $$CONT >/dev/null 2>&1; then \
			docker rm -f $$CONT && echo "[*] Removed container $$CONT"; \
		else \
			echo "[-] Container $$CONT not found"; \
		fi; \
	else \
		docker ps -a --format "{{.Names}}" | grep "^$(CON_PREFIX)-" | xargs -r docker rm -f && echo "[*] Removed all containers" || true; \
	fi

# -------------------------------
# clear — remove containers + images (NAME=x for one, bare for all)
# -------------------------------

clear:
	@if [ -n "$(NAME)" ]; then \
		CONT=$(CON_PREFIX)-$(NAME); IMG=$(IMG_PREFIX)-$(NAME); \
		if docker inspect $$CONT >/dev/null 2>&1; then \
			docker rm -f $$CONT && echo "[*] Removed container $$CONT"; \
		else \
			echo "[-] Container $$CONT not found — skipping"; \
		fi; \
		if docker image inspect $$IMG >/dev/null 2>&1; then \
			docker rmi -f $$IMG && echo "[*] Removed image $$IMG"; \
		else \
			echo "[-] Image $$IMG not found — skipping"; \
		fi; \
	else \
		echo "This will remove ALL $(CON_PREFIX)-* containers and $(IMG_PREFIX)-* images."; \
		printf "Confirm? [y/N] " && read ans && [ "$$ans" = "y" ] || { echo "Aborted."; exit 1; }; \
		docker ps -a --format "{{.Names}}" | grep "^$(CON_PREFIX)-" | xargs -r docker rm -f && echo "[*] Removed all containers" || true; \
		docker images --format "{{.Repository}}" | grep "^$(IMG_PREFIX)-" | xargs -r docker rmi -f && echo "[*] Removed all images" || true; \
		echo "[*] Done"; \
	fi
