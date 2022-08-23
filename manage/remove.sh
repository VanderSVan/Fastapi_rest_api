#!/usr/bin/env bash

set -e

cd ..

set -a
source $PWD/.env
set +a

case "$1" in
--dev)
  export COMPOSE_PROJECT_NAME=restaurant_dev
  echo "The development containers data are removing ..."
  docker rmi restaurant_dev_api
  docker volume rm restaurant_dev_restaurant-db
  ;;
*)
  export COMPOSE_PROJECT_NAME=restaurant
  echo "The production containers data are removing ..."
  docker rmi restaurant_api
  docker volume rm restaurant_restaurant-api restaurant_restaurant-db
  ;;
esac