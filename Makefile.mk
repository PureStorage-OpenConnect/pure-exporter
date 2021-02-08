IMAGE_NAMESPACE ?= quay.io/purestorage
IMAGE_NAME ?= pure-exporter
IMAGE_TAG ?= latest
EXPORTER ?= pure_exporter
REQUIREMENTS ?= requirements.txt
DOCKERFILE ?= Dockerfile
RUN_PORT ?= 9491
TEST_PORT ?= 8123
TIMEO ?= 30
WORKERS ?= 2

default: build

.PHONY: all
all: build test

.PHONY: build
build: $(DOCKERFILE) $(REQUIREMENTS) .dockerignore $(wildcard *.py)
	docker build . -f $(DOCKERFILE) -t $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: test
test:
	(GUNICORN_CMD_ARGS="--bind=0.0.0.0:$(TEST_PORT) --workers=2 --access-logfile=- \
         --timeout $(TIMEO) --workers $(WORKERS) \
         --error-logfile=- --access-logformat=\"%(t)s %(h)s %(U)s %(l)s %(T)s %(B)s\"" \
         gunicorn $(EXPORTER):app)

.PHONY: test-fa-docker
test-docker:
	(GUNICORN_CMD_ARGS="--bind=0.0.0.0:$(RUN_PORT) --workers=2 --access-logfile=- \
         --timeout $(TIMEO) --workers $(WORKERS) \
         --error-logfile=- --access-logformat=\"%(t)s %(h)s %(U)s %(l)s %(T)s %(B)s\"" \
        docker run --rm -p $(TEST_PORT):$(RUN_PORT) $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG))
