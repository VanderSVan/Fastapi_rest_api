#!/usr/bin/env bash

set -e

case "$1" in
--dev)
  echo "The development container is stopping ..."
  docker compose -f docker/docker-compose.base.yml -f docker/docker-compose.dev.yml stop
  echo "The development container is removing ..."
  docker compose -f docker/docker-compose.base.yml -f docker/docker-compose.dev.yml down
  ;;
*)
  echo "The production container is stopping ..."
  docker compose -f docker/docker-compose.base.yml -f docker/docker-compose.prod.yml stop
  echo "The production container is removing ..."
  docker compose -f docker/docker-compose.base.yml -f docker/docker-compose.prod.yml down
esac