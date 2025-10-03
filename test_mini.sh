#!/bin/bash

echo "Testing Mini Podcast Generation (4 lines only)..."
echo "================================================"

curl -X POST http://localhost:5000/test-mini-podcast \
  -H "Content-Type: application/json" \
  | jq .

echo ""
echo "Test complete! Check ./tmp/mini-* directory for output files."
