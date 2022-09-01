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
  docker rmi restaurant_dev_flower
  docker rmi restaurant_dev_celery_worker
  docker rmi restaurant_dev_backend
  docker volume rm restaurant_dev_restaurant-db
  ;;
*)
  export COMPOSE_PROJECT_NAME=restaurant
  echo "The production containers data are removing ..."
  docker rmi restaurant_flower
  docker rmi restaurant_celery_worker
  docker rmi restaurant_backend
  docker volume rm restaurant_restaurant-backend restaurant_restaurant-db
  ;;
esac