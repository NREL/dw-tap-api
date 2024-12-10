export PROJECT_HANDLE=tap
export APP_NAME=api
export MAKEFILE_PATH=./awscodebuild/Makefile
export APPFLEET_RELEASE_NAME=dev
export APPFLEET_DEPLOY_VERSION=0.0.12-1.0.0-alpine-3c676c3
export BASE_IMAGE_TAG=3-alpine

make -f "$MAKEFILE_PATH" V=1 release

