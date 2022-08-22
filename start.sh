#!/usr/bin/env bash

set -e

set -a
source $PWD/.env
set +a

case "$1" in
--dev)
  echo "The development containers are running ..."
  docker compose -f docker/docker-compose.base.yml -f docker/docker-compose.dev.yml up --build
  ;;
*)
  echo "The production containers are running ..."
  docker compose -f docker/docker-compose.base.yml -f docker/docker-compose.prod.yml up -d --build
  ;;
esac