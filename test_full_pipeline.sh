#!/bin/bash

echo "=== Testing Full Podcast Generation Pipeline ==="
echo ""

# 1. Generate podcast
echo "1. Generating podcast..."
RESPONSE=$(curl -s -X POST http://localhost:5000/generate-podcast \
  -H "Content-Type: application/json" \
  -d '{
    "user_preferences": {
      "tone": "Sherlock-like analytical",
      "medical_history": {
        "past": ["asthmatic"],
        "current": ["vitamin D deficient at 17.1 ng/mL"]
      }
    },
    "weather_info": {
      "temperature": 24,
      "humidity": 65,
      "air_quality_index": 95
    },
    "interests": ["LLM", "electronics"],
    "home_location": "Kharar, Punjab",
    "work_location": "IT Park, Chandigarh"
  }')

echo "$RESPONSE" | python3 -m json.tool
PODCAST_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -z "$PODCAST_ID" ]; then
    echo "Failed to get podcast ID"
    exit 1
fi

echo ""
echo "Podcast ID: $PODCAST_ID"
echo ""

# 2. Check status
echo "2. Checking status..."
curl -s http://localhost:5000/status/$PODCAST_ID | python3 -m json.tool
echo ""

# 3. Get results
echo "3. Getting results..."
curl -s http://localhost:5000/get-podcast/$PODCAST_ID | python3 -m json.tool
echo ""

# 4. Test question answering
echo "4. Testing question answering..."
curl -s -X POST http://localhost:5000/answer-question \
  -H "Content-Type: application/json" \
  -d "{
    \"podcast_id\": \"$PODCAST_ID\",
    \"timestamp\": \"00:20\",
    \"question\": \"How does air quality affect people with asthma?\"
  }" | python3 -m json.tool
echo ""

echo "=== Test Complete ==="
echo "Download package: curl http://localhost:5000/download-podcast/$PODCAST_ID -o podcast.zip"
