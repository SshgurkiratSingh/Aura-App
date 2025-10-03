#!/bin/bash

PODCAST_ID="podcast-20251003T163403Z-0f52d4d2"

echo "=== Testing New Features ==="
echo ""

echo "1. Get Full Audio (Concatenated)"
curl -s http://localhost:5000/get-full-audio/$PODCAST_ID -o full_audio.wav
echo "Downloaded: full_audio.wav"
echo ""

echo "2. List All Podcasts"
curl -s http://localhost:5000/podcasts | jq
echo ""

echo "3. Create Share Link"
SHARE_RESPONSE=$(curl -s -X POST http://localhost:5000/share/$PODCAST_ID)
echo $SHARE_RESPONSE | jq
SHARE_TOKEN=$(echo $SHARE_RESPONSE | jq -r '.share_token')
echo ""

echo "4. Access Shared Podcast"
curl -s http://localhost:5000/shared/$SHARE_TOKEN | jq
echo ""

echo "5. Get Shared Audio"
curl -s http://localhost:5000/shared/$SHARE_TOKEN/audio -o shared_audio.wav
echo "Downloaded: shared_audio.wav"
echo ""

echo "6. Download Shared Podcast"
curl -s http://localhost:5000/shared/$SHARE_TOKEN/download -o shared_podcast.zip
echo "Downloaded: shared_podcast.zip"
echo ""

echo "Share URL: http://localhost:5000/shared/$SHARE_TOKEN"
