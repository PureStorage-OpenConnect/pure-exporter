IMAGE_NAMESPACE ?= quay.io/purestorage
IMAGE_NAME ?= pure-exporter
IMAGE_NAMESPACE ?= quay.io/purestorage
IMAGE_TAG ?= latest

FA_IMAGE_NAME ?= pure-fa-exporter
FA_IMAGE_TAG ?= latest

FB_IMAGE_NAME ?= pure-fb-exporter
FB_IMAGE_TAG ?= latest

RUN_PORT = 9491
TEST_PORT = 8123

default: build

.PHONY: all
all: build test

.PHONY: build
build: Dockerfile requirements.txt .dockerignore $(wildcard *.py)
	docker build . -f Dockerfile -t $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: build_fa
build_fa: Dockerfile.fa requirements.fa.txt .dockerignore $(wildcard *.py)
	docker build . -f Dockerfile.fa -t $(IMAGE_NAMESPACE)/$(FA_IMAGE_NAME):$(FA_IMAGE_TAG)

.PHONY: build_fb
build_fb: Dockerfile.fb requirements.fb.txt .dockerignore $(wildcard *.py)
	docker build . -f Dockerfile.fb -t $(IMAGE_NAMESPACE)/$(FB_IMAGE_NAME):$(FB_IMAGE_TAG)

.PHONY: test
test:
	(GUNICORN_CMD_ARGS="--bind=0.0.0.0:$(TEST_PORT) --workers=2 --access-logfile=- \
         --error-logfile=- --access-logformat=\"%(t)s %(h)s %(U)s %(l)s %(T)s %(B)s\"" \
         gunicorn pure_exporter:app)

.PHONY: test-fa
test-fa:
	(GUNICORN_CMD_ARGS="--bind=0.0.0.0:$(TEST_PORT) --workers=2 --access-logfile=- \
         --error-logfile=- --access-logformat=\"%(t)s %(h)s %(U)s %(l)s %(T)s %(B)s\"" \
         gunicorn pure_fa_exporter:app)

.PHONY: test-docker
test-docker:
	(GUNICORN_CMD_ARGS="--bind=0.0.0.0:$(RUN_PORT) --workers=2 --access-logfile=- \
         --error-logfile=- --access-logformat=\"%(t)s %(h)s %(U)s %(l)s %(T)s %(B)s\"" \
        docker run --rm -p $(TEST_PORT):$(RUN_PORT) $(IMAGE_NAMESPACE)/$(IMAGE_NAME):$(IMAGE_TAG))

.PHONY: test-fa-docker
test-fa-docker:
	(GUNICORN_CMD_ARGS="--bind=0.0.0.0:$(RUN_PORT) --workers=2 --access-logfile=- \
         --error-logfile=- --access-logformat=\"%(t)s %(h)s %(U)s %(l)s %(T)s %(B)s\"" \
        docker run --rm -p $(TEST_PORT):$(RUN_PORT) $(IMAGE_NAMESPACE)/$(FA_IMAGE_NAME):$(FA_IMAGE_TAG))

.PHONY: test-fb-docker
test-fb-docker:
	(GUNICORN_CMD_ARGS="--bind=0.0.0.0:$(RUN_PORT) --workers=2 --access-logfile=- \
         --error-logfile=- --access-logformat=\"%(t)s %(h)s %(U)s %(l)s %(T)s %(B)s\"" \
        docker run --rm -p $(TEST_PORT):$(RUN_PORT) $(IMAGE_NAMESPACE)/$(FB_IMAGE_NAME):$(FB_IMAGE_TAG))

.PHONY: release
release:
	@[ "$(VERSION)" ] || ( echo "$@ needs VERSION variable"; exit 1 )
	git tag "v$(VERSION)"
	git tag "$(IMAGE_TAG)" --force
	git push --force --tags
