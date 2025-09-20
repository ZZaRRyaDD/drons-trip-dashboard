ifeq ($(shell test -e '.env' && echo -n yes),yes)
	include .env
endif

args := $(wordlist 2, 100, $(MAKECMDGOALS))
ifndef args
MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
MESSAGE = "Done"
endif

APPLICATION_NAME = app
TEST = poetry run python3 -m pytest --verbosity=2 --showlocals --log-level=DEBUG

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

# Commands
env:  ##@Environment Create .env file with variables
	@$(eval SHELL:=/bin/bash)
	@cp .env.sample .env

help: ##@Help Show this help
	@echo -e "Usage: make [target] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)

docker-up-build:  ##@Application Run and build application server
	docker compose -f docker-compose.yml up --build --remove-orphans

docker-up-buildd:  ##@Application Run and build application server in daemon
	docker compose -f docker-compose.yml up -d --build --remove-orphans

docker-up:  ##@Application Run application server
	docker compose -f docker-compose.yml up

docker-upd:  ##@Application Run application server in daemon
	docker compose -f docker-compose.yml up -d

docker-down:  ##@Application Stop application in docker
	docker compose -f docker-compose.yml down --remove-orphans

docker-downv:  ##@Application Stop application in docker and remove volumes
	docker compose -f docker-compose.yml down -v --remove-orphans

docker-up-build-prod:  ##@Application Run and build application server in production
	docker compose -f docker-compose.prod.yml up --build --remove-orphans

docker-up-buildd-prod:  ##@Application Run and build application server in daemon in production
	docker compose -f docker-compose.prod.yml up -d --build --remove-orphans

docker-up-prod:  ##@Application Run application server in production
	docker compose -f docker-compose.prod.yml up

docker-upd-prod:  ##@Application Run application server in daemon in production
	docker compose -f docker-compose.prod.yml up -d

docker-down-prod:  ##@Application Stop application in docker in production
	docker compose -f docker-compose.prod.yml down --remove-orphans

docker-downv-prod:  ##@Application Stop application in docker and remove volumes in production
	docker compose -f docker-compose.prod.yml down -v --remove-orphans

docker-run-server:  ##@Application Run command in server container
	docker compose -f docker-compose.yml run server $(args)

open-db:  ##@Database Open database inside docker-image
	docker exec -it postgres psql -d $(POSTGRES_DB) -U $(POSTGRES_USER) -p $(POSTGRES_PORT)

test-docker:  ##@Testing Test application with pytest in docker
	docker compose -f docker-compose.test.yml up -d --build --remove-orphans
	docker compose -f docker-compose.test.yml run server make tests
	docker compose -f docker-compose.test.yml down -v --remove-orphans

test-cov-docker:  ##@Testing Test application with pytest and create coverage report
	docker compose -f docker-compose.test.yml up -d --build --remove-orphans
	docker compose -f docker-compose.test.yml run server make tests-cov
	docker compose -f docker-compose.test.yml down -v --remove-orphans

linters:  ##@Linters Run linters
	make docker-run-server "make lint"
	make docker-run-server "make format"

migrate:  ##@Database Do all migrations in database
	make docker-run-server "make migrate"

revision:  ##@Database Create new revision file automatically
	make docker-run-server "make revision"

docker-login:  ##@Docker Login in GitHub Container Registry
	echo $(PAT) | docker login ghcr.io -u $(USERNAME) --password-stdin

docker-clean:  ##@Application Remove all docker objects
	docker system prune --all -f

docker-stack-deploy:  ##@Docker Deploy containers in stack in docker swarm
	docker stack deploy --with-registry-auth --resolve-image always --prune --compose-file docker-compose.prod.yml backend

docker-cleanv:  ##@Application Remove all docker objects with volumes
	docker system prune --all --volumes -f

docker-stop:  ##@Application Stop all docker containers
	@docker rm -f $$(docker ps -aq) || true

%::
	echo $(MESSAGE)
