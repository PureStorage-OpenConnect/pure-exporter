NS ?= purestorage
VERSION ?= latest

CONTAINER_NAME = pure-prom-exp
CONTAINER_INSTANCE ?= default
PORTS = 9091:9091

IMAGE_NAME ?= pure-prom-exporter

.PHONY: build

build: Dockerfile
	docker build -t $(NS)/$(IMAGE_NAME):$(VERSION) -f Dockerfile .

run:
	docker run -d --name $(CONTAINER_NAME)-$(CONTAINER_INSTANCE) -p$(PORTS) $(NS)/$(IMAGE_NAME):$(VERSION)


defeult: build
