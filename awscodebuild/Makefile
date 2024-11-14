-include env_make

# Required environment variables check
REQUIRED_VARS := PROJECT_HANDLE APP_NAME MAKEFILE_PATH APPFLEET_RELEASE_NAME APPFLEET_DEPLOY_VERSION BASE_IMAGE_TAG
$(foreach var,$(REQUIRED_VARS),$(if $(value $(var)),,$(error Environment variable $(var) is not set)))

# Environment variables (can be overridden by command-line arguments)
PROJECT_NAME = $(PROJECT_HANDLE)-$(APP_NAME)
WORKDIR ?= $(or $(dir $(MAKEFILE_PATH)), $(CURDIR))

# Display the WORKDIR value
$(info Using WORKDIR: $(WORKDIR))

# Validate that WORKDIR is an existing directory
ifeq ("$(wildcard $(WORKDIR))","")
    $(error Error: WORKDIR '$(WORKDIR)' does not exist or is not accessible.)
endif

REGISTRY-IDS = 991404956194
REPO = $(REGISTRY-IDS).dkr.ecr.us-west-2.amazonaws.com/nrel-$(PROJECT_NAME)
NAME = $(PROJECT_NAME)

ifdef RELEASE_SHA2
  HEAD_VER=$(RELEASE_SHA2)
else ifdef RELEASE_SHA1
  HEAD_VER=$(RELEASE_SHA1)
else
	HEAD_VER=$(shell git log -1 --pretty=tformat:%h)
endif

$(info HEAD_VER="$(HEAD_VER)")

ifdef BRANCH_NAME2
	BRANCH_NAME=$(BRANCH_NAME2)
else ifdef BRANCH_NAME1
	BRANCH_NAME=$(BRANCH_NAME1)
else
	BRANCH_NAME ?= $(shell git rev-parse --abbrev-ref HEAD)
endif

# Normalize branch name for Docker tag compatibility
BRANCH_NAME_SAFE = $(subst /,-,$(BRANCH_NAME))

$(info BRANCH_NAME_SAFE="$(BRANCH_NAME_SAFE)")

# Use CodeBuild build number if present, otherwise fallback to timestamp for uniqueness
ifdef CODEBUILD_BUILD_NUMBER
  UNIQUE_ID=$(CODEBUILD_BUILD_NUMBER)
  $(info Using CODEBUILD_BUILD_NUMBER: $(CODEBUILD_BUILD_NUMBER))
else
  UNIQUE_ID=$(shell date +%Y%m%d%H%M%S)
  $(info Using UNIQUE_ID generated from timestamp: $(UNIQUE_ID))
endif

$(info UNIQUE_ID="$(UNIQUE_ID)")

# git release version - use for rollbacks
TAG ?= $(BASE_IMAGE_TAG)-$(APPFLEET_RELEASE_NAME)-$(BRANCH_NAME_SAFE)-$(HEAD_VER)-$(UNIQUE_ID)

$(info TAG="$(TAG)")

default: release

# Optional build targets
TARGET_ARG := $(if $(BUILD_TARGET),--target $(BUILD_TARGET),)

# Updated build target with optional BUILD_TARGET
build:
	$(info Running Docker build command:)
	$(info docker build -t $(REPO):$(TAG) --platform linux/amd64 --build-arg BASE_IMAGE_TAG=$(BASE_IMAGE_TAG) $(TARGET_ARG) $(WORKDIR))
	docker build -t $(REPO):$(TAG) \
		--platform linux/amd64 \
		--build-arg BASE_IMAGE_TAG=$(BASE_IMAGE_TAG) \
		.
	@echo "Writing image definitions file..."
	@printf '{"ImageURI":"%s"}' "$(REPO):$(TAG)" > $(WORKDIR)/imageDetail.json
	@echo "Image definitions file created: $(WORKDIR)/imageDetail.json"

prebuild:
	aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin $(REGISTRY-IDS).dkr.ecr.us-west-2.amazonaws.com
	docker buildx create --use --name mybuilder --driver docker-container

buildx:
	@echo "Starting Docker Buildx process..."
	docker buildx build --builder mybuilder \
			--cache-from type=registry,ref=$(REPO):cache \
			--cache-to mode=max,image-manifest=true,oci-mediatypes=true,type=registry,ref=$(REPO):cache \
			--platform linux/amd64 \
			--build-arg BASE_IMAGE_TAG=$(BASE_IMAGE_TAG) \
			--push --provenance=false \
			$(TARGET_ARG) \
			--tag $(REPO):$(TAG) \
			$(WORKDIR)
	@echo "Docker image built and pushed to ECR with tag: $(TAG)"
	@echo "Writing image definitions file..."
	@printf '{"ImageURI":"%s"}' "$(REPO):$(TAG)" > $(WORKDIR)/imageDetail.json
	@echo "Image definitions file created: $(WORKDIR)/imageDetail.json"

test:
	echo "Reading IMAGE_URI from $(WORKDIR)/imageDetail.json..."
	IMAGE_URI=$$(jq -r '.ImageURI' $(WORKDIR)/imageDetail.json); \
	echo "Extracting TAG from IMAGE_URI..."; \
	TAG=$$(echo $$IMAGE_URI | sed 's/.*://'); \
	echo "Testing with TAG: $$TAG"; \
	cd ./tests/basic && IMAGE=$(REPO):$$TAG ./run.sh

push:
	@echo "Reading image details from $(WORKDIR)/imageDetail.json..."
	@IMAGE_URI=$$(jq -r '.ImageURI' $(WORKDIR)/imageDetail.json); \
	if aws ecr describe-images --repository-name nrel-$(PROJECT_NAME) --image-ids imageTag=$$(basename $$IMAGE_URI) >/dev/null 2>&1; then \
		echo "Image $$IMAGE_URI already exists in ECR. Skipping push."; \
	else \
		echo "Pushing Docker image $$IMAGE_URI..."; \
		docker push $$IMAGE_URI; \
	fi

deploy:
	echo "Reading IMAGE_URI from $(WORKDIR)/imageDetail.json..."
	IMAGE_URI=$$(jq -r '.ImageURI' $(WORKDIR)/imageDetail.json); \
	echo "Extracting TAG from IMAGE_URI..."; \
	TAG=$$(echo $$IMAGE_URI | sed 's/.*://'); \
	echo "Deploying with TAG: $$TAG"; \
	echo "Running create-credentials script..."; \
	WORKDIR=$(WORKDIR) $(WORKDIR)/create-credentials.sh; \
	echo "Deploying containers for $(PROJECT_NAME)..."; \
	echo "IMAGE_URI: $$IMAGE_URI"; \
	echo "TAG: $$TAG"; \
	echo "PROJECT_HANDLE: $(PROJECT_HANDLE)"; \
	echo "SERVICE_HANDLE: $(APP_NAME)"; \
	echo "DEPLOY_ENVIRONMENT: $(APPFLEET_RELEASE_NAME)"; \
	DOCKER_TAG1=$$TAG \
	PROJECT_HANDLE=$(PROJECT_HANDLE) \
	SERVICE_HANDLE=$(APP_NAME) \
	DEPLOY_ENVIRONMENT=$(APPFLEET_RELEASE_NAME) \
	docker-compose -f $(WORKDIR)/docker-compose.deploy.yaml up --quiet-pull

run:
	docker run --rm --name $(PROJECT_NAME) $(PORTS) $(VOLUMES) $(ENV) $(REPO):$(TAG) $(CMD)

clean:
	-docker rm -f $(PROJECT_NAME)

release: build push deploy

SELF_DIR := $(dir $(lastword $(MAKEFILE_LIST)))
include $(SELF_DIR)docker.mk
