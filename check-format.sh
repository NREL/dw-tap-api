#!/bin/bash
set -e

cd windwatts-ui

echo "Running ESLint..."
yarn lint --fix

echo "Running Prettier check..."
yarn format -w
