#!/usr/bin/env bash

set -e

set -a
source $PWD/.env
set +a

case "$1" in
--dev)
  echo "The development containers are restarting ..."
  docker compose -f docker/docker-compose.base.yml -f docker/docker-compose.dev.yml restart
  ;;
*)
  echo "The production containers are restarting ..."
  docker compose -f docker/docker-compose.base.yml -f docker/docker-compose.prod.yml restart
  ;;
esac