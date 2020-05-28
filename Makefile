IMAGE_NAMESPACE ?= genegatpure
IMAGE_NAME ?= pure-exporter
IMAGE_TAG ?= latest

RUN_PORT = 9491
TEST_PORT = 8123

default: build

.PHONY: all
all: build test

.PHONY: build
build: Dockerfile requirements.txt .dockerignore $(wildcard *.py)
	docker build . -f Dockerfile -t $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: test
test:
	(GUNICORN_CMD_ARGS="--bind=0.0.0.0:$(TEST_PORT) --workers=2 --access-logfile=- \
         --error-logfile=- --access-logformat=\"%(t)s %(h)s %(U)s %(l)s %(T)s %(B)s\"" \
         gunicorn pure_exporter:app)

.PHONY: test-docker
test-docker:
	(GUNICORN_CMD_ARGS="--bind=0.0.0.0:$(RUN_PORT) --workers=2 --access-logfile=- \
         --error-logfile=- --access-logformat=\"%(t)s %(h)s %(U)s %(l)s %(T)s %(B)s\"" \
        docker run --rm -p $(TEST_PORT):$(RUN_PORT) $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG))

.PHONY: release
release:
	@[ "$(VERSION)" ] || ( echo "$@ needs VERSION variable"; exit 1 )
	git tag "v$(VERSION)"
	git tag "$(IMAGE_TAG)" --force
	git push --force --tags
