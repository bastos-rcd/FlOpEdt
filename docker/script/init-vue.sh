#!/bin/sh

case $CONFIG in
"production")
  # Build Vue files on production
  export NODE_ENV=production && yarn build
  ;;
"development")
  # Serve on development
  export NODE_ENV=development && yarn dev
  ;;
*)
  echo "CONFIG must be set to either development or production"
  return 1
  ;;
esac

exec "$@"
