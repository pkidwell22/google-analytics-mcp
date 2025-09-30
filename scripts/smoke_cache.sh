#!/usr/bin/env bash
set -euo pipefail
URL="${URL:-https://ga4-mcp-265267513550.us-central1.run.app}"

echo "→ tools/list"
curl -s -X POST "$URL/mcp" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}' | jq '.result | {count: (.tools|length)}'

echo "→ resolver first call (should be cached=false)"
curl -s -X POST "$URL/mcp" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"2","method":"tools/call","params":{"name":"find_ga4_property","arguments":{"query":"gatedepot.com"}}}' \
  | jq '{cached: .result.meta.cached, resolved: .result.rows[0]}'

echo "→ resolver second call (should be cached=true)"
curl -s -X POST "$URL/mcp" -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"3","method":"tools/call","params":{"name":"find_ga4_property","arguments":{"query":"gatedepot.com"}}}' \
  | jq '{cached: .result.meta.cached, resolved: .result.rows[0]}'
