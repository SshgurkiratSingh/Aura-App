# Podcast API - Test Examples

## Prerequisites

Start the Flask server with environment variables:

```bash
export PPLX_API_KEY="your_perplexity_api_key_here"
export GOOGLE_API_KEY="your_google_api_key_here"
python app.py
```

---

## 1. Mini Podcast Test (Fast - 4 Lines)

Quickest way to verify the entire pipeline works.

```bash
curl -X POST http://localhost:5000/test-mini-podcast \
  -H "Content-Type: application/json"
```

**Expected Response:**

```json
{
  "status": "success",
  "id": "mini-20251003T141718Z-1dfb65b1",
  "directory": "./tmp/mini-20251003T141718Z-1dfb65b1",
  "files": {
    "news": "./tmp/mini-20251003T141718Z-1dfb65b1/mini-20251003T141718Z-1dfb65b1_news.json",
    "script": "./tmp/mini-20251003T141718Z-1dfb65b1/mini-20251003T141718Z-1dfb65b1_script.txt",
    "audio": ["./tmp/mini-20251003T141718Z-1dfb65b1/mini-20251003T141718Z-1dfb65b1_seg0_0.wav"],
    "metadata": "./tmp/mini-20251003T141718Z-1dfb65b1/mini-20251003T141718Z-1dfb65b1_metadata.json"
  },
  "script_preview": "Speaker 1: Good morning...\nSpeaker 2: Hello...\nSpeaker 1: Today...\nSpeaker 2: Indeed..."
}
```

---

## 2. Full Podcast Generation (Async)

Generate a complete personalized podcast with all features.

### Example 1: Tech Professional

```bash
curl -X POST http://localhost:5000/generate-podcast \
  -H "Content-Type: application/json" \
  -d '{
    "user_preferences": {
      "name": "User",
      "tone": "Sherlock-like analytical and precise",
      "interests": ["LLM", "electronics", "PCB", "VLSI","Gate ece"],
      "medical_history": {
        "past": ["asthmatic"],
        "current": ["vitamin D deficient at 17.1 ng/mL"]
      },
      "occupation": "Electronics Engineer",
      "study_focus": "VLSI Design"
    },
    "weather_info": {
      "temperature": 24,
      "feels_like": 22,
      "humidity": 65,
      "conditions": "partly cloudy",
      "air_quality_index": 95,
      "air_quality_category": "moderate",
      "uv_index": 6,
      "wind_speed": 12,
      "visibility": 8,
      "pressure": 1013,
      "sunrise": "06:15 AM",
      "sunset": "06:45 PM"
    },
    "interests": ["LLM", "electronics", "PCB", "VLSI"],
    "home_location": "Kharar, Punjab, India",
    "work_location": "IT Park, Chandigarh, India",
    "extra": {
      "calendar_events": [
        {
          "time": "9:30  to 1:20PM",
          "title": "College",
          "duration": "4",
          "location": "CCET Chandigarh"
        },
        {
          "time": "5:00 PM to 8",
          "title": "Signal Class",
          "duration": "180 minutes",
          "location": "Sector 34 chandigarh"
        }
      ],
      "commute_info": {
        "route": "Kharar to IT Park Chandigarh",
        "distance": "28 km",
        "estimated_time": "35 minutes",
        "traffic_status": "moderate"
      },
      "health_reminders": [
        "Take Vitamin D supplement (2000 IU)",
        "Avoid outdoor activities during high AQI",
        "Keep inhaler accessible"
      ]
    }
  }'

```

### Example 2: Student

```bash
curl -X POST http://localhost:5000/generate-podcast \
  -H "Content-Type: application/json" \
  -d '{
    "user_preferences": {
      "name": "Priya",
      "tone": "energetic and motivational",
      "occupation": "Engineering Student"
    },
    "weather_info": {
      "temperature": 28,
      "humidity": 80,
      "conditions": "cloudy",
      "air_quality_index": 120
    },
    "interests": ["VLSI", "robotics", "gaming"],
    "home_location": "Pune, India",
    "work_location": "College of Engineering, Pune"
  }'
```

### Example 3: Healthcare Professional

```bash
curl -X POST http://localhost:5000/generate-podcast \
  -H "Content-Type: application/json" \
  -d '{
    "user_preferences": {
      "name": "Dr. Sarah",
      "tone": "professional and informative",
      "occupation": "Physician",
      "medical_history": {
        "interests": ["cardiology", "preventive care"]
      }
    },
    "weather_info": {
      "temperature": 18,
      "humidity": 60,
      "conditions": "rainy",
      "air_quality_index": 40
    },
    "interests": ["medical research", "health tech", "wellness"],
    "home_location": "Boston, MA",
    "work_location": "Massachusetts General Hospital"
  }'
```

**Expected Response (Immediate - 202 Status):**

```json
{
  "id": "podcast-20251003T141718Z-1dfb65b1",
  "status": "QUEUED",
  "message": "Podcast generation started",
  "status_url": "/status/podcast-20251003T141718Z-1dfb65b1",
  "result_url": "/get-podcast/podcast-20251003T141718Z-1dfb65b1",
  "download_url": "/download-podcast/podcast-20251003T141718Z-1dfb65b1"
}
```

---

## 3. Check Job Status

Monitor the progress of podcast generation.

```bash
# Replace with actual podcast ID from step 1
curl http://localhost:5000/status/podcast-20251003T141718Z-1dfb65b1
```

**Expected Response (In Progress):**

```json
{
  "id": "podcast-20251003T141718Z-1dfb65b1",
  "status": "RUNNING",
  "progress": 65,
  "stage": "TTS Generation",
  "eta_seconds": 45
}
```

**Expected Response (Completed):**

```json
{
  "id": "podcast-20251003T141718Z-1dfb65b1",
  "status": "COMPLETED",
  "progress": 100,
  "stage": "Done",
  "eta_seconds": 0,
  "result_url": "/get-podcast/podcast-20251003T141718Z-1dfb65b1"
}
```

---

## 4. Get Podcast Results

Retrieve all generated files.

```bash
curl http://localhost:5000/get-podcast/podcast-20251003T141718Z-1dfb65b1
```

**Expected Response:**

```json
{
  "id": "podcast-20251003T141718Z-1dfb65b1",
  "script": "/files/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_script.txt",
  "questions": "/files/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_questions.json",
  "audio": [
    "/files/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_seg0_0.wav"
  ],
  "metadata": "/files/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_metadata.json",
  "news": "/files/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_news.json"
}
```

---

## 5. Download Complete Package

Download all files as a ZIP archive.

```bash
curl http://localhost:5000/download-podcast/podcast-20251003T141718Z-1dfb65b1 \
  -o podcast.zip
```

**Verify download:**

```bash
unzip -l podcast.zip
```

---

## 6. Fetch News Only

Get news without generating a podcast.

```bash
curl -X POST http://localhost:5000/fetch-news \
  -H "Content-Type: application/json" \
  -d '{
    "interests": ["LLM", "electronics", "PCB", "VLSI"],
    "home_location": "Kharar, Punjab, India",
    "work_location": "IT Park, Chandigarh, India"
  }'
```

**Expected Response:**

```json
{
  "status": "success",
  "news": {
    "interests": "Latest news about LLM, electronics, PCB, VLSI...",
    "home_location": "Local news for Kharar, Punjab, India...",
    "work_location": "Local news for IT Park, Chandigarh, India..."
  },
  "news_file": "./tmp/news-20251003T142530Z-680f6c6a.json",
  "metadata": {
    "interests": ["LLM", "electronics", "PCB", "VLSI"],
    "home_location": "Kharar, Punjab, India",
    "work_location": "IT Park, Chandigarh, India"
  }
}
```

---

## 7. Test Script Generation (No Audio)

Generate script and questions without audio.

```bash
curl -X POST http://localhost:5000/test-news-script \
  -H "Content-Type: application/json" \
  -d '{
    "user_preferences": {
      "tone": "Sherlock-like analytical"
    },
    "weather_info": {
      "temperature": 24,
      "humidity": 65,
      "air_quality_index": 95
    },
    "interests": ["LLM", "AI"],
    "home_location": "Kharar, Punjab"
  }'
```

**Expected Response:**

```json
{
  "status": "success",
  "test_id": "test-20251003T142556Z-5127792b",
  "news": {
    "interests": "...",
    "home_location": "..."
  },
  "news_file": "./tmp/test-20251003T142556Z-5127792b_news.json",
  "script": "Speaker 1: Good morning...",
  "script_file": "./tmp/test-20251003T142556Z-5127792b_script.txt",
  "request_file": "./tmp/test-20251003T142556Z-5127792b_request.json"
}
```

---

## 8. Test TTS Only

Test audio generation with a custom script.

```bash
curl -X POST http://localhost:5000/test-tts \
  -H "Content-Type: application/json" \
  -d '{
    "script": "Speaker 1: Good morning! Today we will discuss the latest developments in AI and technology.\n\nSpeaker 2: That sounds fascinating. The field of artificial intelligence has been evolving rapidly.\n\nSpeaker 1: Absolutely. From large language models to computer vision, the progress has been remarkable.\n\nSpeaker 2: Indeed. Let us dive into the details."
  }'
```

**Expected Response:**

```json
{
  "status": "success",
  "test_id": "tts-test-20251003T145411Z-7920a8a5",
  "audio_files": [
    "./tmp/tts-test-20251003T145411Z-7920a8a5_seg0_0.wav"
  ],
  "total_files": 1
}
```

---

## 9. Answer a Question

Get a detailed answer for a specific question.

```bash
curl -X POST http://localhost:5000/answer-question \
  -H "Content-Type: application/json" \
  -d '{
    "podcast_id": "podcast-20251003T141718Z-1dfb65b1",
    "timestamp": "00:20",
    "question": "How does air quality affect people with asthma?"
  }'
```

**Expected Response:**

```json
{
  "status": "success",
  "answer": "Air quality significantly impacts people with asthma because fine particulate matter (PM2.5) and other pollutants can trigger airway inflammation, bronchospasm, and increased mucus production. When AQI levels are elevated, especially above 100, individuals with asthma may experience worsened symptoms including wheezing, shortness of breath, chest tightness, and coughing. It's recommended to limit outdoor activities, use air purifiers indoors, and keep rescue inhalers accessible during poor air quality days.",
  "answers_file": "./tmp/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_answers.json"
}
```

---

## 10. Health Check

Verify the API is running.

```bash
curl http://localhost:5000/health
```

**Expected Response:**

```json
{
  "status": "ok",
  "time": "2025-10-03T14:17:18.123456"
}
```

---

## 11. Get Full Audio (Concatenated)

Get single concatenated audio file instead of segments.

```bash
curl http://localhost:5000/get-full-audio/podcast-20251003T141718Z-1dfb65b1 \
  -o full_audio.wav
```

**Response:** WAV audio file

---

## 12. List All Podcasts

Get list of all generated podcasts.

```bash
curl http://localhost:5000/podcasts
```

**Expected Response:**

```json
{
  "podcasts": [
    {
      "id": "podcast-20251003T141718Z-1dfb65b1",
      "created_at": "2025-10-03T14:17:18.123456",
      "duration": 287.5,
      "topics": ["AI", "startups", "fitness", "News", "Weather"]
    },
    {
      "id": "podcast-20251003T120000Z-abc123",
      "created_at": "2025-10-03T12:00:00.000000",
      "duration": 305.2,
      "topics": ["VLSI", "robotics", "News"]
    }
  ],
  "total": 2
}
```

---

## 13. Delete Podcast

Delete a podcast and all its files.

```bash
curl -X DELETE http://localhost:5000/podcast/podcast-20251003T141718Z-1dfb65b1
```

**Expected Response:**

```json
{
  "status": "success",
  "message": "Deleted podcast-20251003T141718Z-1dfb65b1"
}
```

---

## 14. Share Podcast

Generate a shareable link for a podcast.

```bash
curl -X POST http://localhost:5000/share/podcast-20251003T141718Z-1dfb65b1
```

**Expected Response:**

```json
{
  "status": "success",
  "share_token": "a1b2c3d4e5f6",
  "share_url": "/shared/a1b2c3d4e5f6",
  "download_url": "/shared/a1b2c3d4e5f6/download"
}
```

---

## 15. Access Shared Podcast

Access a podcast using share token.

```bash
curl http://localhost:5000/shared/a1b2c3d4e5f6
```

**Expected Response:**

```json
{
  "podcast_id": "podcast-20251003T141718Z-1dfb65b1",
  "metadata": {
    "id": "podcast-20251003T141718Z-1dfb65b1",
    "created_at": "2025-10-03T14:17:18.123456",
    "duration": 287.5,
    "topics": ["AI", "startups", "fitness"],
    "chapters": [
      {"timestamp": "00:00", "title": "Segment 1", "preview": "Good morning..."}
    ]
  },
  "audio_url": "/shared/a1b2c3d4e5f6/audio",
  "download_url": "/shared/a1b2c3d4e5f6/download"
}
```

---

## 16. Get Shared Audio

Download audio from shared podcast.

```bash
curl http://localhost:5000/shared/a1b2c3d4e5f6/audio -o shared_audio.wav
```

**Response:** WAV audio file

---

## 17. Download Shared Podcast

Download complete shared podcast as zip.

```bash
curl http://localhost:5000/shared/a1b2c3d4e5f6/download -o shared_podcast.zip
```

**Response:** ZIP file with all podcast files

---

## Using Test Scripts

### Quick Tests

```bash
# Mini test (fastest - 4 lines)
bash test_mini.sh

# Test news fetching
bash test_news_only.sh

# Test script generation
bash test_script_only.sh

# Full async pipeline test
bash test_curl.sh

# Test new features (audio, sharing, management)
bash test_features.sh
```

### Full Async Pipeline Test Script

The `test_curl.sh` automatically:

1. Generates a podcast (returns immediately with job ID)
2. Polls status endpoint until completion
3. Gets results when ready
4. Shows download command

```bash
bash test_curl.sh
```

---

## Viewing Generated Files

```bash
# List all generated podcasts
ls -la ./tmp/podcast-*/

# View a specific podcast's files
ls -la ./tmp/podcast-20251003T141718Z-1dfb65b1/

# Read the script
cat ./tmp/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_script.txt

# View questions
cat ./tmp/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_questions.json | jq

# View metadata
cat ./tmp/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_metadata.json | jq

# Play audio (requires audio player)
ffplay ./tmp/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_seg0_0.wav
```

---

## Checking Logs

```bash
# View today's logs
tail -f ./logs/app_$(date +%Y%m%d).log

# Search for errors
grep ERROR ./logs/app_$(date +%Y%m%d).log

# View specific podcast generation logs
grep "podcast-20251003T141718Z-1dfb65b1" ./logs/app_$(date +%Y%m%d).log
```

---

## Common Issues

### 1. Connection Refused

**Problem:** `curl: (7) Failed to connect to localhost port 5000`

**Solution:** Start the Flask server:

```bash
python app.py
```

### 2. 401 Unauthorized

**Problem:** Perplexity API returns 401

**Solution:** Set the API key:

```bash
export PPLX_API_KEY="your_actual_key"
```

### 3. 429 Quota Exceeded

**Problem:** Gemini TTS quota exceeded

**Solution:** Wait for quota reset or use a different API key. The system will still generate script and questions.

### 4. Job Not Found

**Problem:** `{"error": "Job not found"}`

**Solution:** Use the correct podcast ID from the generation response.

---

## Performance Tips

1. **Mini test** takes ~10-20 seconds (fastest verification)
2. **News fetching** takes ~5-10 seconds
3. **Script generation** takes ~10-15 seconds
4. **Question generation** takes ~10-15 seconds (single LLM call for all questions)
5. **TTS generation** takes ~30-60 seconds depending on script length
6. **Total time** for full podcast: ~1-2 minutes (async background processing)
7. **Question answering** takes ~5-10 seconds per question
8. **Audio concatenation** takes ~1-2 seconds
9. **ZIP packaging** takes ~1-2 seconds
10. **Share link generation** is instant

---

## Sample Test Data

### Minimal Request

```json
{
  "interests": ["AI"],
  "home_location": "Bangalore"
}
```

### Complete Request

See examples in section 2 (Tech Professional, Student, Healthcare Professional).

### Custom Script for TTS

```json
{
  "script": "Speaker 1: Hello.\n\nSpeaker 2: Hi there.\n\nSpeaker 1: How are you?\n\nSpeaker 2: I'm doing well, thank you."
}
```

### Metadata Structure

Each podcast includes rich metadata:

```json
{
  "id": "podcast-20251003T141718Z-1dfb65b1",
  "created_at": "2025-10-03T14:17:18.123456",
  "duration": 287.5,
  "topics": ["AI", "startups", "fitness", "News", "Weather"],
  "chapters": [
    {
      "timestamp": "00:00",
      "title": "Segment 1",
      "preview": "Good morning! Today we'll discuss..."
    },
    {
      "timestamp": "00:20",
      "title": "Segment 2",
      "preview": "Moving on to the latest developments..."
    }
  ],
  "voices": ["Zephyr", "Puck"],
  "audio_format": "wav",
  "questions_count": 45,
  "word_count": 750
}
```

---

## Follow-Up Workflow Examples

### Scenario 1: Quick Test → Verify Structure

**Step 1: Run mini test**

```bash
RESPONSE=$(curl -s -X POST http://localhost:5000/test-mini-podcast \
  -H "Content-Type: application/json")

MINI_ID=$(echo "$RESPONSE" | jq -r '.id')
echo "Mini Podcast ID: $MINI_ID"
```

**Step 2: Verify files created**

```bash
ls -la ./tmp/$MINI_ID/
cat ./tmp/$MINI_ID/${MINI_ID}_script.txt
```

**Step 3: Play audio**

```bash
ffplay ./tmp/$MINI_ID/${MINI_ID}_seg0_0.wav
```

---

### Scenario 2: Generate → Check Status → Download (Async)

**Step 1: Generate podcast (returns immediately)**

```bash
RESPONSE=$(curl -s -X POST http://localhost:5000/generate-podcast \
  -H "Content-Type: application/json" \
  -d '{"interests": ["AI"], "home_location": "Bangalore"}')

PODCAST_ID=$(echo "$RESPONSE" | jq -r '.id')
echo "Podcast ID: $PODCAST_ID (processing in background)"
```

**Step 2: Poll status until complete**

```bash
while true; do
  RESPONSE=$(curl -s http://localhost:5000/status/$PODCAST_ID)
  STATUS=$(echo "$RESPONSE" | jq -r '.status')
  PROGRESS=$(echo "$RESPONSE" | jq -r '.progress')
  STAGE=$(echo "$RESPONSE" | jq -r '.stage')
  echo "Status: $STATUS | Progress: $PROGRESS% | Stage: $STAGE"
  if [ "$STATUS" = "COMPLETED" ]; then
    break
  fi
  sleep 5
done
```

**Step 3: Download package**

```bash
curl http://localhost:5000/download-podcast/$PODCAST_ID -o podcast.zip
echo "Downloaded podcast.zip"
```

---

### Scenario 3: Generate → Ask Questions → Get Answers

**Step 1: Generate podcast**

```bash
PODCAST_ID="podcast-20251003T141718Z-1dfb65b1"  # From generation
```

**Step 2: View questions**

```bash
curl -s http://localhost:5000/get-podcast/$PODCAST_ID | \
  jq -r '.questions' | \
  xargs -I {} curl -s {} | \
  jq '.[] | "[\(.timestamp)] \(.question)"'
```

**Step 3: Ask follow-up question 1**

```bash
curl -X POST http://localhost:5000/answer-question \
  -H "Content-Type: application/json" \
  -d "{
    \"podcast_id\": \"$PODCAST_ID\",
    \"timestamp\": \"00:20\",
    \"question\": \"How does air quality affect people with asthma?\"
  }"
```

**Step 4: Ask follow-up question 2**

```bash
curl -X POST http://localhost:5000/answer-question \
  -H "Content-Type: application/json" \
  -d "{
    \"podcast_id\": \"$PODCAST_ID\",
    \"timestamp\": \"00:40\",
    \"question\": \"What are the latest developments in LLM technology?\"
  }"
```

**Step 5: View all answers**

```bash
cat ./tmp/$PODCAST_ID/${PODCAST_ID}_answers.json | jq
```

---

### Scenario 4: Test Individual Components

**Step 1: Test news fetching**

```bash
NEWS_RESPONSE=$(curl -s -X POST http://localhost:5000/fetch-news \
  -H "Content-Type: application/json" \
  -d '{"interests": ["AI"], "home_location": "Bangalore"}')

echo "$NEWS_RESPONSE" | jq '.news.interests'
```

**Step 2: Test script generation (no audio)**

```bash
SCRIPT_RESPONSE=$(curl -s -X POST http://localhost:5000/test-news-script \
  -H "Content-Type: application/json" \
  -d '{"interests": ["AI"], "home_location": "Bangalore"}')

TEST_ID=$(echo "$SCRIPT_RESPONSE" | jq -r '.test_id')
cat ./tmp/${TEST_ID}_script.txt
```

**Step 3: Test TTS with generated script**

```bash
SCRIPT=$(cat ./tmp/${TEST_ID}_script.txt)

curl -X POST http://localhost:5000/test-tts \
  -H "Content-Type: application/json" \
  -d "{\"script\": \"$SCRIPT\"}"
```

---

### Scenario 5: Batch Processing Multiple Podcasts (Async)

**Generate multiple podcasts**

```bash
#!/bin/bash

LOCATIONS=("Bangalore" "Mumbai" "Delhi")
INTERESTS=("AI" "Technology" "Health")

PODCAST_IDS=()

# Start all jobs (async)
for i in "${!LOCATIONS[@]}"; do
  RESPONSE=$(curl -s -X POST http://localhost:5000/generate-podcast \
    -H "Content-Type: application/json" \
    -d "{
      \"interests\": [\"${INTERESTS[$i]}\"],
      \"home_location\": \"${LOCATIONS[$i]}\"
    }")
  
  PODCAST_ID=$(echo "$RESPONSE" | jq -r '.id')
  PODCAST_IDS+=($PODCAST_ID)
  echo "Started podcast $PODCAST_ID for ${LOCATIONS[$i]}"
done

# Wait for all to complete
for i in "${!PODCAST_IDS[@]}"; do
  PODCAST_ID=${PODCAST_IDS[$i]}
  echo "Waiting for $PODCAST_ID..."
  
  while true; do
    STATUS=$(curl -s http://localhost:5000/status/$PODCAST_ID | jq -r '.status')
    if [ "$STATUS" = "COMPLETED" ]; then
      break
    fi
    sleep 5
  done
  
  # Download
  curl -s http://localhost:5000/download-podcast/$PODCAST_ID \
    -o "podcast_${LOCATIONS[$i]}.zip"
  echo "Downloaded podcast for ${LOCATIONS[$i]}"
done
```

---

### Scenario 6: Interactive Q&A Session

**Complete interactive workflow**

```bash
#!/bin/bash

# 1. Generate podcast (async)
echo "Starting podcast generation..."
RESPONSE=$(curl -s -X POST http://localhost:5000/generate-podcast \
  -H "Content-Type: application/json" \
  -d @request.json)

PODCAST_ID=$(echo "$RESPONSE" | jq -r '.id')
echo "Podcast ID: $PODCAST_ID (processing in background)"

# 2. Poll for completion
echo "Polling for completion..."
while true; do
  RESPONSE=$(curl -s http://localhost:5000/status/$PODCAST_ID)
  STATUS=$(echo "$RESPONSE" | jq -r '.status')
  PROGRESS=$(echo "$RESPONSE" | jq -r '.progress')
  STAGE=$(echo "$RESPONSE" | jq -r '.stage')
  echo "Progress: $PROGRESS% | Stage: $STAGE"
  if [ "$STATUS" = "COMPLETED" ]; then
    break
  fi
  sleep 5
done

# 3. Get questions
echo "\nGenerated Questions:"
curl -s http://localhost:5000/get-podcast/$PODCAST_ID | \
  jq -r '.questions' | \
  xargs -I {} curl -s {} | \
  jq -r '.[] | "[\(.timestamp)] \(.id): \(.question)"'

# 4. Interactive Q&A
echo "\nEnter questions (or 'quit' to exit):"
while true; do
  read -p "Question: " QUESTION
  if [ "$QUESTION" = "quit" ]; then
    break
  fi
  
  read -p "Timestamp (mm:ss): " TIMESTAMP
  
  ANSWER=$(curl -s -X POST http://localhost:5000/answer-question \
    -H "Content-Type: application/json" \
    -d "{
      \"podcast_id\": \"$PODCAST_ID\",
      \"timestamp\": \"$TIMESTAMP\",
      \"question\": \"$QUESTION\"
    }" | jq -r '.answer')
  
  echo "\nAnswer: $ANSWER\n"
done

# 5. Download final package
echo "\nDownloading complete package..."
curl -s http://localhost:5000/download-podcast/$PODCAST_ID -o podcast.zip
echo "Done! Package saved as podcast.zip"
```

---

### Scenario 7: Monitoring and Debugging

**Monitor active jobs**

```bash
# List all podcast directories
ls -lt ./tmp/podcast-* | head -10

# Check latest podcast status
LATEST=$(ls -t ./tmp/podcast-* -d | head -1 | xargs basename)
echo "Latest podcast: $LATEST"
curl http://localhost:5000/status/$LATEST | jq
```

**Debug failed jobs**

```bash
# Check logs for errors
grep ERROR ./logs/app_$(date +%Y%m%d).log | tail -20

# Check specific podcast logs
PODCAST_ID="podcast-20251003T141718Z-1dfb65b1"
grep "$PODCAST_ID" ./logs/app_$(date +%Y%m%d).log

# Check job status
curl http://localhost:5000/status/$PODCAST_ID | jq
```

**Cleanup old podcasts**

```bash
# Remove podcasts older than 7 days
find ./tmp/podcast-* -type d -mtime +7 -exec rm -rf {} \;

# Remove test files
rm -rf ./tmp/test-* ./tmp/tts-test-* ./tmp/news-*
```
