#!/usr/bin/env bash

set -e

set -a; source $PWD/.env; set +a

docker compose -f docker/docker-compose.yml build

docker compose -f docker/docker-compose.yml up -d