IMAGE_NAMESPACE ?= quay.io/purestorage
IMAGE_NAME ?= pure-exporter
IMAGE_TAG ?= latest
REQUIREMENTS ?= requirements.txt
DOCKERFILE ?= Dockerfile
RUN_PORT ?= 9491
TEST_PORT ?= 8123
TIMEO ?= 30

default: build

.PHONY: all
all: build test

.PHONY: build
build: $(DOCKERFILE) $(REQUIREMENTS) .dockerignore $(wildcard *.py)
	docker build . -f $(DOCKERFILE) -t $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: test-fa
test:
	(GUNICORN_CMD_ARGS="--bind=0.0.0.0:$(TEST_PORT) --workers=2 --access-logfile=- \
         --timeout $(TIMEO) \
         --error-logfile=- --access-logformat=\"%(t)s %(h)s %(U)s %(l)s %(T)s %(B)s\"" \
         gunicorn pure_fa_exporter:app)

.PHONY: test-fa-docker
test-docker:
	(GUNICORN_CMD_ARGS="--bind=0.0.0.0:$(RUN_PORT) --workers=2 --access-logfile=- \
         --timeout $(TIMEO) \
         --error-logfile=- --access-logformat=\"%(t)s %(h)s %(U)s %(l)s %(T)s %(B)s\"" \
        docker run --rm -p $(TEST_PORT):$(RUN_PORT) $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG))
