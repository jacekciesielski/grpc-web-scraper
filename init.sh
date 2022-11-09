#!/bin/bash

set -e

while [[ $# -gt 0 ]]; do
  case $1 in
    -d|--dev)
      readonly DEV="true"
      shift # past argument
      ;;
  esac
done

if [[ -n "$DEV" ]]; then

  cd playground/web-client
  npm ci
  cd -

  cd playground
  ./generate_proto.sh
  cd -

fi

cd scraper/node_execution_env
npm ci
cd -
