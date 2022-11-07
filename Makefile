#!/usr/bin/make -f
GLOBAL_ENV=./docker/env/global.env
-include $(GLOBAL_ENV)

CONFIG ?= development
PORT ?= 80
FLOP_HOST ?= localhost
DNS1 ?= 1.1.1.1
DNS2 ?= 8.8.8.8
USE_GUROBI ?=

WEB_IMG := $(if $(USE_GUROBI),gurobi/optimizer:9.5.2,)

GUROBI_IMG=gurobi/optimizer:9.5.2

# Clear the certification renew variable
CERTIF_RENEW=

current_project_dir := $(shell basename ${CURDIR})
default_hosts := 127.0.0.1,localhost
secret_seed = abcdefghijklmnopqrstuvwxyz0123456789!@\#$$%^&*(-_=+)

UID=$(shell id -u)
GID=$(shell id -g)

# get the current git branch name
HOSTS := $(shell [ ! -z "$(FLOP_HOST)" ] && echo $(default_hosts),$(FLOP_HOST) || echo $(default_hosts))
SECRET_KEY := $(shell python -c 'import random; result = "".join([random.choice("$(secret_seed)") for i in range(50)]); print(result)')
BRANCH := $(shell git branch 2>/dev/null | grep '^*' | colrm 1 2)
COMPOSE_PROJECT_NAME := $(shell echo $(current_project_dir) | tr '[:upper:]' '[:lower:]')_$(shell echo $(CONFIG) | head -c 1)
export

.PHONY: config install init build start stop start-db stop-db push deploy rm debug

#
#	Create config files
#
config:
	printf "PORT=${PORT}\n" > $(GLOBAL_ENV)
	printf "FLOP_HOST=${FLOP_HOST}\n" >> $(GLOBAL_ENV)
	printf "DNS1=${DNS1}\n" >> $(GLOBAL_ENV)
	printf "DNS2=${DNS2}\n" >> $(GLOBAL_ENV)
	printf "USE_GUROBI=${USE_GUROBI}\n" >> $(GLOBAL_ENV)

install:
ifeq ($(CONFIG), production)
	envsubst < docker/env/web.prod.in  > docker/env/web.prod.env
	printf "POSTGRES_PASSWORD=$(shell dd if=/dev/urandom bs=1 count=32 2>/dev/null | base64 -w 0 | rev | cut -b 2- | rev)" > docker/env/db.prod.env
else
	echo "Install is only used in production mode."
endif

# Initialize database with basic datas contained
# in dump.json for tests purposes
init:
	docker compose -f docker-compose.$(CONFIG).yml \
		run --rm \
		-e BRANCH \
		-e DJANGO_LOADDATA=on \
		-e START_SERVER=off \
		web

build-vue:
	docker compose -f docker-compose.production.yml --profile vue up

ifeq ($(CONFIG), production)
build: build-vue
endif

build:
	docker compose -f docker-compose.$(CONFIG).yml --profile full build

# starts edt's docker services
start: stop
	docker compose -f docker-compose.$(CONFIG).yml --profile full up -d

# starts edt's docker services in terminal
start_verbose: stop
	docker compose -f docker-compose.$(CONFIG).yml --profile full up

# stops edt's docker services
stop:
	docker compose -f docker-compose.$(CONFIG).yml --profile full --profile vue stop

# starts edt's docker database service
start-db:
	docker compose -f docker-compose.$(CONFIG).yml up -d db

stop-db:
	docker compose -f docker-compose.$(CONFIG).yml stop db

# creates the SSL certificate
create-certif:
	mkdir -p -m a=rwx ./FlOpEDT/acme_challenge/token && docker compose -f docker-compose.production.yml --profile ssl up

renew-certif:
	mkdir -p -m a=rwx ./FlOpEDT/acme_challenge/token && CERTIF_RENEW="--renew 90" docker compose -f docker-compose.production.yml --profile ssl up

#
#	Docker stack helpers
#
push: build
	docker compose -f docker-compose.$(CONFIG).yml push

deploy:
	docker stack deploy --compose-file docker-compose.$(CONFIG).yml $(COMPOSE_PROJECT_NAME)

rm:
	docker stack rm $(COMPOSE_PROJECT_NAME)	


#	Show config infos
debug:
	@echo PORT: $(PORT)
	@echo HOSTS: $(HOSTS)
	@echo CONFIG: $(CONFIG)
	@echo COMPOSE_PROJECT_NAME: $(COMPOSE_PROJECT_NAME)
	@echo FLOP_HOST: $(FLOP_HOST)
	@echo DNS1: $(DNS1)
	@echo DNS2: $(DNS2)

switch-http:
	make PORT=80 config && cp -v docker/nginx/templates/http docker/nginx/templates/default.conf.template

switch-https:
	make PORT=443 config && cp -v docker/nginx/templates/https docker/nginx/templates/default.conf.template
