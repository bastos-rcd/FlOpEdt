#!/usr/bin/make -f
GLOBAL_ENV=./docker/env/global.env
-include $(GLOBAL_ENV)

BOLD := \033[1m
RESET := \033[0m
GREEN := \033[1;32m

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

default: h

.PHONY: config install init build start stop start-db stop-db push deploy rm debug bootstrap

bootstrap: ## Prepare Docker images for the project
bootstrap: \
	config \
	build \
	start


config: ## Create config files
	printf "PORT=${PORT}\n" > $(GLOBAL_ENV)
	printf "FLOP_HOST=${FLOP_HOST}\n" >> $(GLOBAL_ENV)
	printf "DNS1=${DNS1}\n" >> $(GLOBAL_ENV)
	printf "DNS2=${DNS2}\n" >> $(GLOBAL_ENV)
	printf "USE_GUROBI=${USE_GUROBI}\n" >> $(GLOBAL_ENV)

install: ## Install the project in production mode
ifeq ($(CONFIG), production)
	envsubst < docker/env/web.prod.in  > docker/env/web.prod.env
	printf "POSTGRES_PASSWORD=$(shell dd if=/dev/urandom bs=1 count=32 2>/dev/null | base64 -w 0 | rev | cut -b 2- | rev)" > docker/env/db.prod.env
else
	echo "Install is only used in production mode."
endif

init: ## Initialize database with basic datas contained in dump.json for tests purposes
	docker compose -f docker-compose.$(CONFIG).yml \
		run --rm \
		-e BRANCH \
		-e DJANGO_LOADDATA=on \
		-e DJANGO_MIGRATE=on \
		-e START_SERVER=off \
		web

build-vue: ## builds edt's vuejs service
	docker compose -f docker-compose.production.yml --profile vue up

ifeq ($(CONFIG), production)
build: build-vue
endif

build: ## builds edt's docker services
	docker compose -f docker-compose.$(CONFIG).yml --profile full build


start: ## starts edt's docker services
	stop
	docker compose -f docker-compose.$(CONFIG).yml --profile full up -d


start_verbose: ## starts edt's docker services in terminal
	stop
	docker compose -f docker-compose.$(CONFIG).yml --profile full up


stop: ## stops edt's docker services
	docker compose -f docker-compose.$(CONFIG).yml --profile full --profile vue stop


start-db: ## starts edt's docker database service
	docker compose -f docker-compose.$(CONFIG).yml up -d db

stop-db: ## sts edt's docker database service
	docker compose -f docker-compose.$(CONFIG).yml stop db

create-certif: ## creates the SSL certificate
	mkdir -p -m a=rwx ./FlOpEDT/acme_challenge/token && docker compose -f docker-compose.production.yml --profile ssl up

renew-certif: ## renews the SSL certificate
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

debug: ## Show config infos
	@echo PORT: $(PORT)
	@echo HOSTS: $(HOSTS)
	@echo CONFIG: $(CONFIG)
	@echo COMPOSE_PROJECT_NAME: $(COMPOSE_PROJECT_NAME)
	@echo FLOP_HOST: $(FLOP_HOST)
	@echo DNS1: $(DNS1)
	@echo DNS2: $(DNS2)

switch-http: ## switch port to 80
	make PORT=80 config && cp -v docker/nginx/templates/http docker/nginx/templates/default.conf.template

switch-https: ## switch port to 443
	make PORT=443 config && cp -v docker/nginx/templates/https docker/nginx/templates/default.conf.template

h: ## (default) Short default help task
	@echo "$(BOLD)flop Makefile$(RESET)"
	@echo "Please use 'make $(BOLD)target$(RESET)' where $(BOLD)target$(RESET) is one of:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-50s$(RESET) %s\n", $$1, $$2}'
.PHONY: h

help:  ## Show a more readable help on multiple lines
	@echo "$(BOLD)flop Makefile$(RESET)"
	@echo "Please use 'make $(BOLD)target$(RESET)' where $(BOLD)target$(RESET) is one of:"
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%s$(RESET)\n    %s\n\n", $$1, $$2}'
.PHONY: help