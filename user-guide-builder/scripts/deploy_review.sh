#!/usr/bin/env bash
# Publish a built guide page to an nginx review container over ssh (replaces the folder's contents in place).
# Usage: scripts/deploy_review.sh --page <guide.html> --host <user@host> --dir <remote folder> [--port <n>] [--lang vi] [--dry-run]
# The page is an Artifact-style fragment with no doctype or charset, so a document head is prepended; without it
# nginx serves it without a charset and Vietnamese text shows as mojibake.
# First time on a host (container serving the folder read-only, survives reboots):
#   ssh <user@host> 'docker run -d --name <name> --restart unless-stopped -p <port>:80 -v <dir>:/usr/share/nginx/html:ro nginx:1.27-alpine'
set -euo pipefail
PAGE= HOST= DIR= PORT= LANG_ATTR=vi DRY=0
while [ $# -gt 0 ]; do case "$1" in
  --page) PAGE=$2; shift 2;; --host) HOST=$2; shift 2;; --dir) DIR=$2; shift 2;; --port) PORT=$2; shift 2;;
  --lang) LANG_ATTR=$2; shift 2;; --dry-run) DRY=1; shift;; -h|--help) sed -n '2,8p' "$0"; exit 0;;
  *) echo "unknown argument: $1" >&2; exit 2;; esac; done
[ -f "$PAGE" ] && [ -n "$HOST" ] && [ -n "$DIR" ] || { echo "need --page <file> --host <user@host> --dir <remote folder>" >&2; exit 2; }
SRC=$(cd "$(dirname "$PAGE")" && pwd); STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT
{ printf '<!doctype html><html lang="%s"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n' "$LANG_ATTR"; cat "$PAGE"; } > "$STAGE/index.html"
[ -d "$SRC/assets" ] && cp -r "$SRC/assets" "$STAGE/"
echo "staged $(du -sh "$STAGE" | cut -f1) -> $HOST:$DIR" >&2
if [ $DRY = 1 ]; then ls "$STAGE" >&2; exit 0; fi
(cd "$STAGE" && tar cf - .) | ssh -o BatchMode=yes "$HOST" "mkdir -p '$DIR' && cd '$DIR' && find . -mindepth 1 -delete && tar xf -"
if [ -n "$PORT" ]; then
  H=${HOST#*@}; code=$(curl -s -o /dev/null -w '%{http_code}' "http://$H:$PORT/")
  echo "{\"url\": \"http://$H:$PORT/\", \"status\": $code}"; [ "$code" = 200 ] || exit 1
fi
