#!/usr/bin/env bash
# Boot a preview for a freshly-built template + capture its screenshot.
#
# Phase 31 (2026-05-20) — running this after a template lands in
# `pebble/templates/<id>/` and the registry knows about it gives you:
#   1. An instantiated test build at output/<placeholder-slug>/
#   2. A `next dev` running at the given port
#   3. A screenshot saved to `ui/v3/public/templates-preview/<id>.png`
#
# Usage:
#   bash scripts/preview_new_template.sh <template_id> <port> <placeholder_business_name>
#
# Example:
#   bash scripts/preview_new_template.sh ink_studio 3064 "Vermilion Ink"
#
# Requirements: engine running on :8000, template registered in
# pebble/templates/registry.json, port available, npm + playwright.

set -e

TEMPLATE_ID="${1:?template_id required}"
PORT="${2:?port required}"
NAME="${3:?business_name required}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENGINE_URL="http://127.0.0.1:8000"

echo "[1/4] Instantiating $TEMPLATE_ID as \"$NAME\"..."
RESP=$(curl -sS -X POST -H "Content-Type: application/json" --data "$(cat <<EOF
{
  "template_id": "$TEMPLATE_ID",
  "brief": {
    "business_name": "$NAME"
  }
}
EOF
)" -m 300 "$ENGINE_URL/api/instantiate-template")
SLUG=$(echo "$RESP" | python -c "import sys, json; print(json.load(sys.stdin).get('slug', ''))" 2>/dev/null || echo "")

if [ -z "$SLUG" ]; then
  echo "FAIL: no slug in response. Engine response:"
  echo "$RESP"
  exit 1
fi
echo "      slug: $SLUG"

SITE_DIR="$REPO_ROOT/output/$SLUG/site"
if [ ! -d "$SITE_DIR" ]; then
  echo "FAIL: site dir not found at $SITE_DIR"
  exit 2
fi

echo "[2/4] npm install in $SITE_DIR..."
(cd "$SITE_DIR" && npm install --silent 2>&1 | tail -3) || {
  echo "FAIL: npm install"
  exit 3
}

echo "[3/4] Starting next dev on :$PORT (background)..."
LOG_FILE="/tmp/preview-$TEMPLATE_ID-$PORT.log"
(cd "$SITE_DIR" && nohup npx next dev -p "$PORT" > "$LOG_FILE" 2>&1 &)

echo "      waiting for ready..."
for _ in $(seq 1 60); do
  if grep -q "Ready in" "$LOG_FILE" 2>/dev/null; then
    break
  fi
  sleep 1
done

if ! curl -s -m 3 -o /dev/null "http://127.0.0.1:$PORT/"; then
  echo "FAIL: preview not responding"
  tail -10 "$LOG_FILE"
  exit 4
fi
echo "      ✓ preview live at http://127.0.0.1:$PORT/"

echo "[4/4] Capturing screenshot..."
python "$REPO_ROOT/scripts/capture_template_previews.py" "$TEMPLATE_ID=$PORT"

echo
echo "Done. Preview: http://127.0.0.1:$PORT/"
echo "       Slug: $SLUG"
echo "       Screenshot: ui/v3/public/templates-preview/$TEMPLATE_ID.png"
