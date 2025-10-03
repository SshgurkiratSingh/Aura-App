#!/bin/bash

# Test TTS service with a short script
curl -X POST http://localhost:5000/test-tts \
  -H "Content-Type: application/json" \
  -d '{
    "script": "Speaker 1: Good morning! Today we will discuss the latest developments in AI and technology.\n\nSpeaker 2: That sounds fascinating. The field of artificial intelligence has been evolving rapidly, with new breakthroughs happening almost every week.\n\nSpeaker 1: Absolutely. From large language models to computer vision, the progress has been remarkable.\n\nSpeaker 2: Indeed. Let us dive into the details and explore what this means for the future."
  }'
