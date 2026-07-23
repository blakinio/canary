#!/usr/bin/env bash
set -euo pipefail

: "${REHEARSAL_AUTH_URL_FILE:?REHEARSAL_AUTH_URL_FILE is required}"
if [[ "$#" -ne 1 ]]; then
  exit 2
fi
case "$1" in
  https://platform.oteryn.test/oauth/authorize\?*) ;;
  *) exit 3 ;;
esac
printf '%s' "$1" > "${REHEARSAL_AUTH_URL_FILE}"
