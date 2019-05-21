IMAGE_NAMESPACE ?= purestorage
IMAGE_NAME ?= pure-exporter
IMAGE_TAG ?= latest

RUN_PORT = 9491:9491

default: build

.PHONY: all
all: build test

.PHONY: build
build: Dockerfile requirements.txt .dockerignore $(wildcard *.py)
	docker build . -f Dockerfile -t $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: test
test:
	docker run --rm -p $(RUN_PORT) $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: release
release:
	git tag "v$(VERSION)"
	git tag "$(IMAGE_TAG)" --force
	git push --force --tags

