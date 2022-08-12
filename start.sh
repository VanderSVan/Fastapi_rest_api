#!/usr/bin/env bash

set -e

set -a
source $PWD/.env
set +a

case "$1" in
--dev)
  echo "The development container is building ..."
  docker compose -f docker/docker-compose.base.yml -f docker/docker-compose.dev.yml build
  echo "The development container is running ..."
  docker compose -f docker/docker-compose.base.yml -f docker/docker-compose.dev.yml up
  ;;
*)
  echo "The production container is building ..."
  docker compose -f docker/docker-compose.base.yml -f docker/docker-compose.prod.yml build
  echo "The production container is running ..."
  docker compose -f docker/docker-compose.base.yml -f docker/docker-compose.prod.yml up -d
  ;;
esac