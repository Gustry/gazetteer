.PHONY: help
help:
	@echo "Available targets:"
	@grep -E '^[$$() a-zA-Z_0-9-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		sed 's/$$(IMAGES)/$(IMAGES)/' | \
		sed 's/$$(IMAGES_PUSH)/$(IMAGES_PUSH)/' | \
		awk \
			'BEGIN {FS = ":.*?## "}; \
			{ printf "\033[36m%-30s\033[0m%s%s\n", $$1, "\n ", $$2 }'

.PHONY: docker
docker: ## Build the linz-gazetteer-db docker image
	docker build -t linz-gazetteer-db:8.4 .

.PHONY: docker-start
docker-start: ## Start the linz-gazetteer-db docker container
	docker run -d --name gazetteer-db -p 7432:5432 linz-gazetteer-db:8.4

.PHONY: docker-stop
docker-stop: ## Stop the linz-gazetteer-db docker container
	docker rm -f gazetteer-db

.PHONY: docker-db-shell
docker-db-shell: ## Start a shell to the containerized db
	docker run --rm -ti --entrypoint bash linz-gazetteer-db:8.4

.PHONY: docker-connect
docker-connect: ## Connect to the dockerized linz-gazetteer-db db using psql
	PGPASSWORD=******** psql -h localhost -p 7432 -U gaz_web gazetteer
