# ===============================
# Claude Lab Makefile (Prefixed)
# ===============================

IMG_PREFIX=cldimg
CON_PREFIX=cldcon

BASE_IMG=$(IMG_PREFIX)-base
CLEAN_CONT=$(CON_PREFIX)-clean

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
# build base image
# -------------------------------

build:
	docker build -t $(BASE_IMG) .

# -------------------------------
# list all managed entities
# -------------------------------

list:
	@echo "=== Images ($(IMG_PREFIX)-*) ==="
	@docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep $(IMG_PREFIX) || true
	@echo ""
	@echo "=== Containers ($(CON_PREFIX)-*) ==="
	@docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" | grep $(CON_PREFIX) || true

# -------------------------------
# run clean container
# -------------------------------

run.clean:
	docker rm -f $(CLEAN_CONT) 2>/dev/null || true
	docker run -it --name $(CLEAN_CONT) $(BASE_IMG)

# -------------------------------
# create new env container
# usage: make new NAME=envA
# -------------------------------

new:
	@if [ -z "$(NAME)" ]; then echo "Usage: make new NAME=envA"; exit 1; fi
	CONT=$(CON_PREFIX)-$(NAME); \
	docker rm -f $$CONT 2>/dev/null || true; \
	docker run -it --name $$CONT $(BASE_IMG)

# -------------------------------
# run existing container
# -------------------------------

run:
	@if [ -z "$(NAME)" ]; then echo "Usage: make run NAME=envA"; exit 1; fi
	CONT=$(CON_PREFIX)-$(NAME); \
	docker start -ai $$CONT

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
# usage:
# make cmp SRC=cldcon-clean DST=cldcon-envA
# make cmp SRC=cldimg-envA DST=cldcon-envB
# -------------------------------

cmp:
	@if [ -z "$(SRC)" ] || [ -z "$(DST)" ]; then \
		echo "Usage: make cmp SRC=<entity> DST=<entity>"; exit 1; fi

	@SRC_CONT=$$($(call resolve_container,$(SRC))); \
	DST_CONT=$$($(call resolve_container,$(DST))); \
	\
	SRC_UPPER=$$(docker inspect $$SRC_CONT | jq -r '.[0].GraphDriver.Data.UpperDir'); \
	DST_UPPER=$$(docker inspect $$DST_CONT | jq -r '.[0].GraphDriver.Data.UpperDir'); \
	\
	echo "=== SRC ($$SRC_CONT) ==="; \
	sudo tree $$SRC_UPPER || sudo find $$SRC_UPPER; \
	echo ""; \
	echo "=== DST ($$DST_CONT) ==="; \
	sudo tree $$DST_UPPER || sudo find $$DST_UPPER;

# -------------------------------
# diff (export DST upperdir)
# usage:
# make diff SRC=cldcon-clean DST=cldcon-envA
# -------------------------------

diff:
	@if [ -z "$(SRC)" ] || [ -z "$(DST)" ]; then \
		echo "Usage: make diff SRC=<entity> DST=<entity>"; exit 1; fi

	@DST_CONT=$$($(call resolve_container,$(DST))); \
	\
	DST_UPPER=$$(docker inspect $$DST_CONT | jq -r '.[0].GraphDriver.Data.UpperDir'); \
	\
	OUT=envs/$(DST)_minus_$(SRC); \
	mkdir -p $$OUT; \
	\
	echo "[*] Exporting $$DST → $$OUT"; \
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
# remove container
# -------------------------------

rm:
	@if [ -z "$(NAME)" ]; then echo "Usage: make rm NAME=envA"; exit 1; fi
	docker rm -f $(CON_PREFIX)-$(NAME)

# -------------------------------
# cleanup all managed
# -------------------------------

clean:
	docker ps -a --format "{{.Names}}" | grep $(CON_PREFIX) | xargs -r docker rm -f
	docker images --format "{{.Repository}}" | grep $(IMG_PREFIX) | xargs -r docker rmi -f
	rm -rf envs/*
	echo "[*] Cleaned all $(IMG_PREFIX)* and $(CON_PREFIX)*"
