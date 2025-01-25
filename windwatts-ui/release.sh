export PROJECT_HANDLE=windwatts
export APP_NAME=ui
export MAKEFILE_PATH=./appfleet-config/Makefile
export APPFLEET_RELEASE_NAME=dev
# export APPFLEET_DEPLOY_VERSION=2.1.1-alpine-e1f2893
export APPFLEET_DEPLOY_VERSION=2.1.3-alpine-e1f2893
export BASE_IMAGE_TAG=3.11.4-slim-buster
export CONFIG_FILE_URL=https://github.nrel.gov/nrel-cloud-computing/appfleet-ui/raw/main/appfleet-config/appfleet.yml
# Properly format the JSON for APPFLEET_BUILD_ARGS
export APPFLEET_BUILD_ARGS='{"main": {"image_detail": "./appfleet-config/mainDetail.json", "dockerfile": "./Dockerfile", "ecr_repo": "$(REGISTRY-IDS).dkr.ecr.us-west-2.amazonaws.com/nrel-windwatts-ui", "target_arg": ""}}'
export CACHE_S3_BUCKET=nrel-windwatts-ui-codebuild
# aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 991404956194.dkr.ecr.us-west-2.amazonaws.com
make -f "$MAKEFILE_PATH" V=1 buildx
# Run the generate_appfleet_tag_overrides.sh script
echo "Running generate_appfleet_tag_overrides.sh to populate APPFLEET_TAG_OVERRIDES..."
APPFLEET_TAG_OVERRIDES=$(./appfleet-config/generate_appfleet_tag_overrides.sh)
# Output the populated APPFLEET_TAG_OVERRIDES
echo "APPFLEET_TAG_OVERRIDES: $APPFLEET_TAG_OVERRIDES"
make -f "$MAKEFILE_PATH" V=1 APPFLEET_TAG_OVERRIDES="$APPFLEET_TAG_OVERRIDES" deploy
