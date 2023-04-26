.PHONY: build
build:
	docker buildx build -t python-runner ./bot/playground/python/

	docker compose build
