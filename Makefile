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

.PHONY: help build base login plug-template new run stop stop.all merge list cmp diff diff.meta clean clean.all

.DEFAULT_GOAL := help

help:
	@echo "Claude Overlay Lab"
	@echo ""
	@echo "Layers (build image + spin container)"
	@echo "  make base                             build base image + spin container"
	@echo "  make login                            build base+login images + spin container"
	@echo "  make plug-template                    build base+plug-template images + spin container"
	@echo "  make build                            build base image only ($(BASE_IMG))"
	@echo ""
	@echo "Environments"
	@echo "  make new   NAME=<n> SRC=<img>         create container from image"
	@echo "  make run   NAME=<n>                   re-enter existing container"
	@echo "  make stop  NAME=<n>                   stop running container"
	@echo "  make stop.all                         stop all running $(CON_PREFIX)-* containers"
	@echo "  make merge NAME=<n>                   commit container → image"
	@echo ""
	@echo "Inspect"
	@echo "  make list                             list all managed images and containers"
	@echo "  make cmp  SRC=<entity> DST=<entity>   compare OverlayFS trees"
	@echo "  make diff SRC=cldimg-<n> DST=cldcon-<n> [NAME=<folder>]   export DST upperdir to diffs/"
	@echo "  make diff.meta NAME=<n>               docker diff metadata"
	@echo ""
	@echo "Cleanup"
	@echo "  make clean NAME=<n>                   remove container + image by name"
	@echo "  make clean.all                        remove everything (with confirmation)"

# -------------------------------
# build base image only
# -------------------------------

build:
	$(MAKE) -C base IMG_PREFIX=$(IMG_PREFIX)

# ===============================
# layers
# ===============================

base:
	$(MAKE) -C base IMG_PREFIX=$(IMG_PREFIX)
	$(MAKE) new NAME=base SRC=$(BASE_IMG)

login:
	$(MAKE) -C base IMG_PREFIX=$(IMG_PREFIX)
	$(MAKE) -C login IMG_PREFIX=$(IMG_PREFIX)
	$(MAKE) new NAME=login SRC=$(IMG_PREFIX)-login


plug-template:
	$(MAKE) -C base IMG_PREFIX=$(IMG_PREFIX)
	$(MAKE) -C plug-template IMG_PREFIX=$(IMG_PREFIX)
	$(MAKE) new NAME=plug-template SRC=$(IMG_PREFIX)-plug-template $(if $(wildcard plug-template/claude_tilda),TILDA=plug-template/claude_tilda)

# ===============================
# container operations
# ===============================

# -------------------------------
# list all managed entities
# -------------------------------

list:
	@echo "=== Images ($(IMG_PREFIX)-*) ==="
	@docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep $(IMG_PREFIX) || true
	@echo ""
	@echo "=== Containers running ($(CON_PREFIX)-*) ==="
	@docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" | grep $(CON_PREFIX) || true
	@echo ""
	@echo "=== Containers stopped ($(CON_PREFIX)-*) ==="
	@docker ps -a --filter "status=exited" --filter "status=created" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" | grep $(CON_PREFIX) || true

# -------------------------------
# create new env container
# usage: make new NAME=envA SRC=cldimg-base
# -------------------------------

new:
	@if [ -z "$(NAME)" ] || [ -z "$(SRC)" ]; then echo "Usage: make new NAME=envA SRC=cldimg-base"; exit 1; fi
	CONT=$(CON_PREFIX)-$(NAME); \
	docker rm -f $$CONT 2>/dev/null || true; \
	docker run -it --name $$CONT \
		-e ANTHROPIC_API_KEY=$(ANTHROPIC_API_KEY) \
		-v $(CURDIR)/aliases:/home/user/.aliases:rw \
		-v $(CURDIR)/base/claude_tilda_base:/home/user/.claude-tpl:ro \
		$(if $(TILDA),-v $(CURDIR)/$(TILDA):/home/user/.claude) \
		$${proj:+-v $$proj:/proj} \
		$(SRC)

# -------------------------------
# run existing container
# usage: make run NAME=envA
# -------------------------------

run:
	@if [ -z "$(NAME)" ]; then echo "Usage: make run NAME=envA"; exit 1; fi
	@CONT=$(CON_PREFIX)-$(NAME); \
	if ! docker inspect $$CONT >/dev/null 2>&1; then \
		echo "Container $$CONT does not exist. Run: make new NAME=$(NAME) SRC=<img>"; exit 1; \
	fi; \
	docker start -ai $$CONT

# -------------------------------
# stop a running container
# usage: make stop NAME=envA
# -------------------------------

stop:
	@if [ -z "$(NAME)" ]; then echo "Usage: make stop NAME=envA"; exit 1; fi
	CONT=$(CON_PREFIX)-$(NAME); \
	docker stop $$CONT && echo "[*] Stopped $$CONT"

# -------------------------------
# stop all running containers of our prefix
# -------------------------------

stop.all:
	@RUNNING=$$(docker ps --format "{{.Names}}" | grep "^$(CON_PREFIX)-"); \
	if [ -z "$$RUNNING" ]; then echo "[-] No running $(CON_PREFIX)-* containers"; exit 0; fi; \
	echo "$$RUNNING" | xargs docker stop; \
	echo "[*] Stopped all $(CON_PREFIX)-* containers"

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
# usage: make cmp SRC=cldimg-base DST=cldcon-envA
# -------------------------------

cmp:
	@if [ -z "$(SRC)" ] || [ -z "$(DST)" ]; then \
		echo "Usage: make cmp SRC=$(IMG_PREFIX)-<name> DST=$(CON_PREFIX)-<name>"; exit 1; fi
	@case "$(SRC)" in $(IMG_PREFIX)-*) ;; *) echo "Error: SRC must be a $(IMG_PREFIX)-* image"; exit 1; esac
	@case "$(DST)" in $(CON_PREFIX)-*) ;; *) echo "Error: DST must be a $(CON_PREFIX)-* container"; exit 1; esac
	@SRC_CONT=$$($(call resolve_container,$(SRC))); \
	DST_CONT=$$($(call resolve_container,$(DST))); \
	SRC_UPPER=$$(docker inspect $$SRC_CONT | jq -r '.[0].GraphDriver.Data.UpperDir'); \
	DST_UPPER=$$(docker inspect $$DST_CONT | jq -r '.[0].GraphDriver.Data.UpperDir'); \
	echo "=== SRC ($$SRC_CONT) ==="; \
	sudo tree $$SRC_UPPER -la || sudo find $$SRC_UPPER; \
	echo ""; \
	echo "=== DST ($$DST_CONT) ==="; \
	sudo tree $$DST_UPPER -la || sudo find $$DST_UPPER

# -------------------------------
# diff (export DST upperdir)
# usage: make diff SRC=cldimg-base DST=cldcon-envA [NAME=folder]
# -------------------------------

diff:
	@if [ -z "$(SRC)" ] || [ -z "$(DST)" ]; then \
		echo "Usage: make diff SRC=$(IMG_PREFIX)-<name> DST=$(CON_PREFIX)-<name>"; exit 1; fi
	@case "$(SRC)" in $(IMG_PREFIX)-*) ;; *) echo "Error: SRC must be a $(IMG_PREFIX)-* image"; exit 1; esac
	@case "$(DST)" in $(CON_PREFIX)-*) ;; *) echo "Error: DST must be a $(CON_PREFIX)-* container"; exit 1; esac
	@DST_CONT=$$($(call resolve_container,$(DST))); \
	DST_UPPER=$$(docker inspect $$DST_CONT | jq -r '.[0].GraphDriver.Data.UpperDir'); \
	if [ -n "$(NAME)" ]; then \
		OUT=diffs/$(NAME); \
	else \
		OUT=diffs/$(DST)_minus_$(SRC)_$$(date +%Y%m%d_%H%M%S); \
	fi; \
	mkdir -p $$OUT; \
	echo "[*] Exporting $(DST) → $$OUT"; \
	sudo rsync -a $$DST_UPPER/ $$OUT/; \
	echo "[*] Done"

# -------------------------------
# metadata diff (docker diff)
# -------------------------------

diff.meta:
	@if [ -z "$(NAME)" ]; then echo "Usage: make diff.meta NAME=envA"; exit 1; fi
	CONT=$(CON_PREFIX)-$(NAME); \
	docker diff $$CONT

# -------------------------------
# clean by name (container + image)
# usage: make clean NAME=envA
# -------------------------------

clean:
	@if [ -z "$(NAME)" ]; then echo "Usage: make clean NAME=envA"; exit 1; fi
	@CONT=$(CON_PREFIX)-$(NAME); IMG=$(IMG_PREFIX)-$(NAME); \
	if docker inspect $$CONT >/dev/null 2>&1; then \
		docker rm -f $$CONT && echo "[*] Removed container $$CONT"; \
	else \
		echo "[-] Container $$CONT not found — skipping"; \
	fi; \
	if docker image inspect $$IMG >/dev/null 2>&1; then \
		docker rmi -f $$IMG && echo "[*] Removed image $$IMG"; \
	else \
		echo "[-] Image $$IMG not found — skipping"; \
	fi

# -------------------------------
# clean all managed (with confirmation)
# -------------------------------

clean.all:
	@echo "This will remove ALL $(CON_PREFIX)-* containers and $(IMG_PREFIX)-* images."
	@printf "Confirm? [y/N] " && read ans && [ "$$ans" = "y" ] || { echo "Aborted."; exit 1; }
	@docker ps -a --format "{{.Names}}" | grep $(CON_PREFIX) | xargs -r docker rm -f && echo "[*] Removed all containers" || true
	@docker images --format "{{.Repository}}" | grep $(IMG_PREFIX) | xargs -r docker rmi -f && echo "[*] Removed all images" || true
	@echo "[*] Done"
