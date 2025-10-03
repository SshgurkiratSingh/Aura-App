# Podcast Generation API Documentation

## Base URL
```
http://localhost:5000
```

## Authentication
Set environment variables before starting the server:
```bash
export PPLX_API_KEY="your_perplexity_api_key"
export GOOGLE_API_KEY="your_google_gemini_api_key"
```

---

## Endpoints

### 1. Generate Podcast (Full Pipeline)

**Endpoint:** `POST /generate-podcast`

**Description:** Generates a complete personalized podcast with news, script, questions, and audio.

**Request Body:**
```json
{
  "user_preferences": {
    "name": "User",
    "tone": "Sherlock-like analytical",
    "interests": ["LLM", "electronics", "PCB", "VLSI"],
    "medical_history": {
      "past": ["asthmatic"],
      "current": ["vitamin D deficient at 17.1 ng/mL"]
    },
    "occupation": "Electronics Engineer"
  },
  "weather_info": {
    "temperature": 24,
    "feels_like": 22,
    "humidity": 65,
    "conditions": "partly cloudy",
    "air_quality_index": 95,
    "air_quality_category": "moderate"
  },
  "interests": ["LLM", "electronics", "PCB", "VLSI"],
  "home_location": "Kharar, Punjab, India",
  "work_location": "IT Park, Chandigarh, India",
  "extra": {
    "calendar_events": [
      {
        "time": "09:00 AM",
        "title": "VLSI Design Review"
      }
    ]
  }
}
```

**Response:**
```json
{
  "id": "podcast-20251003T141718Z-1dfb65b1",
  "status": "COMPLETED",
  "result_url": "/get-podcast/podcast-20251003T141718Z-1dfb65b1",
  "download_url": "/download-podcast/podcast-20251003T141718Z-1dfb65b1"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/generate-podcast \
  -H "Content-Type: application/json" \
  -d @request.json
```

---

### 2. Check Job Status

**Endpoint:** `GET /status/{job_id}`

**Description:** Check the progress of a podcast generation job.

**Response:**
```json
{
  "id": "podcast-20251003T141718Z-1dfb65b1",
  "status": "RUNNING",
  "progress": 65,
  "stage": "TTS Generation",
  "eta_seconds": 45
}
```

**Status Values:**
- `QUEUED` - Job is queued
- `RUNNING` - Job is in progress
- `COMPLETED` - Job finished successfully
- `FAILED` - Job failed

**Stages:**
- News Fetch (20%)
- Script Generation (40%)
- Question Generation (60%)
- TTS Generation (80%)
- Packaging (100%)

**cURL Example:**
```bash
curl http://localhost:5000/status/podcast-20251003T141718Z-1dfb65b1
```

---

### 3. Get Podcast Results

**Endpoint:** `GET /get-podcast/{job_id}`

**Description:** Retrieve all generated files for a completed podcast.

**Response:**
```json
{
  "id": "podcast-20251003T141718Z-1dfb65b1",
  "script": "/files/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_script.txt",
  "questions": "/files/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_questions.json",
  "audio": [
    "/files/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_seg0_0.wav",
    "/files/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_seg1_0.wav"
  ],
  "metadata": "/files/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_metadata.json",
  "news": "/files/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_news.json"
}
```

**cURL Example:**
```bash
curl http://localhost:5000/get-podcast/podcast-20251003T141718Z-1dfb65b1
```

---

### 4. Download Podcast Package

**Endpoint:** `GET /download-podcast/{job_id}`

**Description:** Download all podcast files as a single ZIP archive.

**Response:** Binary ZIP file

**cURL Example:**
```bash
curl http://localhost:5000/download-podcast/podcast-20251003T141718Z-1dfb65b1 \
  -o podcast.zip
```

---

### 5. Answer Question

**Endpoint:** `POST /answer-question`

**Description:** Generate a detailed answer for a specific question from the podcast.

**Request Body:**
```json
{
  "podcast_id": "podcast-20251003T141718Z-1dfb65b1",
  "timestamp": "00:20",
  "question": "How does air quality affect people with asthma?"
}
```

**Response:**
```json
{
  "status": "success",
  "answer": "Air quality significantly impacts people with asthma because fine particulate matter (PM2.5) and other pollutants can trigger airway inflammation...",
  "answers_file": "./tmp/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_answers.json"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/answer-question \
  -H "Content-Type: application/json" \
  -d '{
    "podcast_id": "podcast-20251003T141718Z-1dfb65b1",
    "timestamp": "00:20",
    "question": "How does air quality affect people with asthma?"
  }'
```

---

### 6. Fetch News Only

**Endpoint:** `POST /fetch-news`

**Description:** Fetch news separately for interests, home location, and work location.

**Request Body:**
```json
{
  "interests": ["LLM", "electronics", "PCB", "VLSI"],
  "home_location": "Kharar, Punjab, India",
  "work_location": "IT Park, Chandigarh, India"
}
```

**Response:**
```json
{
  "status": "success",
  "news": {
    "interests": "Latest news about LLM, electronics...",
    "home_location": "Local news for Kharar, Punjab...",
    "work_location": "Local news for IT Park, Chandigarh..."
  },
  "news_file": "./tmp/news-20251003T142530Z-680f6c6a.json",
  "metadata": {
    "interests": ["LLM", "electronics", "PCB", "VLSI"],
    "home_location": "Kharar, Punjab, India",
    "work_location": "IT Park, Chandigarh, India"
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/fetch-news \
  -H "Content-Type: application/json" \
  -d '{
    "interests": ["LLM", "electronics"],
    "home_location": "Kharar, Punjab",
    "work_location": "IT Park, Chandigarh"
  }'
```

---

### 7. Test Script Generation (No Audio)

**Endpoint:** `POST /test-news-script`

**Description:** Test news fetching and script generation without audio generation.

**Request Body:** Same as `/generate-podcast`

**Response:**
```json
{
  "status": "success",
  "test_id": "test-20251003T142556Z-5127792b",
  "news": {
    "interests": "...",
    "home_location": "...",
    "work_location": "..."
  },
  "news_file": "./tmp/test-20251003T142556Z-5127792b_news.json",
  "script": "Speaker 1: Good morning...",
  "script_file": "./tmp/test-20251003T142556Z-5127792b_script.txt",
  "request_file": "./tmp/test-20251003T142556Z-5127792b_request.json"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/test-news-script \
  -H "Content-Type: application/json" \
  -d @request.json
```

---

### 8. Test TTS Only

**Endpoint:** `POST /test-tts`

**Description:** Test text-to-speech generation with a custom script.

**Request Body:**
```json
{
  "script": "Speaker 1: Good morning! Today we will discuss AI.\n\nSpeaker 2: That sounds fascinating."
}
```

**Response:**
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

**cURL Example:**
```bash
curl -X POST http://localhost:5000/test-tts \
  -H "Content-Type: application/json" \
  -d '{
    "script": "Speaker 1: Hello.\n\nSpeaker 2: Hi there."
  }'
```

---

### 9. Health Check

**Endpoint:** `GET /health`

**Description:** Check if the API is running.

**Response:**
```json
{
  "status": "ok",
  "time": "2025-10-03T14:17:18.123456"
}
```

**cURL Example:**
```bash
curl http://localhost:5000/health
```

---

### 10. Get Full Audio (Concatenated)

**Endpoint:** `GET /get-full-audio/{podcast_id}`

**Description:** Get single concatenated audio file instead of segments.

**Response:** Binary WAV file

**cURL Example:**
```bash
curl http://localhost:5000/get-full-audio/podcast-20251003T141718Z-1dfb65b1 \
  -o full_audio.wav
```

---

### 11. List All Podcasts

**Endpoint:** `GET /podcasts`

**Description:** Get list of all generated podcasts.

**Response:**
```json
{
  "podcasts": [
    {
      "id": "podcast-20251003T141718Z-1dfb65b1",
      "created_at": "2025-10-03T14:17:18.123456",
      "duration": 287.5,
      "topics": ["AI", "startups", "fitness", "News", "Weather"]
    }
  ],
  "total": 1
}
```

**cURL Example:**
```bash
curl http://localhost:5000/podcasts
```

---

### 12. Delete Podcast

**Endpoint:** `DELETE /podcast/{podcast_id}`

**Description:** Delete a podcast and all its files.

**Response:**
```json
{
  "status": "success",
  "message": "Deleted podcast-20251003T141718Z-1dfb65b1"
}
```

**cURL Example:**
```bash
curl -X DELETE http://localhost:5000/podcast/podcast-20251003T141718Z-1dfb65b1
```

---

### 13. Share Podcast

**Endpoint:** `POST /share/{podcast_id}`

**Description:** Generate a shareable link for a podcast.

**Response:**
```json
{
  "status": "success",
  "share_token": "a1b2c3d4e5f6",
  "share_url": "/shared/a1b2c3d4e5f6",
  "download_url": "/shared/a1b2c3d4e5f6/download"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/share/podcast-20251003T141718Z-1dfb65b1
```

---

### 14. Access Shared Podcast

**Endpoint:** `GET /shared/{share_token}`

**Description:** Access a podcast using share token.

**Response:**
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

**cURL Example:**
```bash
curl http://localhost:5000/shared/a1b2c3d4e5f6
```

---

### 15. Get Shared Audio

**Endpoint:** `GET /shared/{share_token}/audio`

**Description:** Download audio from shared podcast.

**Response:** Binary WAV file

**cURL Example:**
```bash
curl http://localhost:5000/shared/a1b2c3d4e5f6/audio -o shared_audio.wav
```

---

### 16. Download Shared Podcast

**Endpoint:** `GET /shared/{share_token}/download`

**Description:** Download complete shared podcast as zip.

**Response:** Binary ZIP file

**cURL Example:**
```bash
curl http://localhost:5000/shared/a1b2c3d4e5f6/download -o shared_podcast.zip
```

---

### 17. Serve Files

**Endpoint:** `GET /files/{filepath}`

**Description:** Serve generated files directly.

**Response:** File content

**cURL Example:**
```bash
curl http://localhost:5000/files/podcast-20251003T141718Z-1dfb65b1/podcast-20251003T141718Z-1dfb65b1_script.txt
```

---

## File Structure

Each podcast generates the following files in `./tmp/{podcast_id}/`:

```
podcast-20251003T141718Z-1dfb65b1/
├── podcast-20251003T141718Z-1dfb65b1_news.json          # News from all sources
├── podcast-20251003T141718Z-1dfb65b1_script.txt         # Generated script
├── podcast-20251003T141718Z-1dfb65b1_questions.json     # Questions with timestamps
├── podcast-20251003T141718Z-1dfb65b1_answers.json       # Answers to questions
├── podcast-20251003T141718Z-1dfb65b1_metadata.json      # Podcast metadata with chapters
├── podcast-20251003T141718Z-1dfb65b1_request.json       # Original request data
├── podcast-20251003T141718Z-1dfb65b1_seg0_0.wav         # Audio segment 1
├── podcast-20251003T141718Z-1dfb65b1_seg1_0.wav         # Audio segment 2
├── podcast-20251003T141718Z-1dfb65b1_full.wav           # Concatenated audio (on request)
└── podcast-20251003T141718Z-1dfb65b1_share.json         # Share token (when shared)
```

---

## Questions Format

Questions are generated every 20 seconds (3 questions per segment):

```json
[
  {
    "id": "q1_1",
    "timestamp": "00:00",
    "question": "What's the weather like today?"
  },
  {
    "id": "q1_2",
    "timestamp": "00:00",
    "question": "How does humidity affect health?"
  },
  {
    "id": "q1_3",
    "timestamp": "00:00",
    "question": "What is the air quality index?"
  },
  {
    "id": "q2_1",
    "timestamp": "00:20",
    "question": "What time is the study session?"
  }
]
```

---

## Metadata Format

```json
{
  "id": "podcast-20251003T141718Z-1dfb65b1",
  "created_at": "2025-10-03T14:17:18.123456Z",
  "duration": 287.5,
  "topics": ["AI", "startups", "fitness", "News", "Weather"],
  "chapters": [
    {
      "timestamp": "00:00",
      "title": "Segment 1",
      "preview": "Good morning! Today we'll discuss the latest developments in AI..."
    },
    {
      "timestamp": "00:20",
      "title": "Segment 2",
      "preview": "Moving on to startup news, several companies have announced..."
    }
  ],
  "sections": [
    "Weather",
    "Air Quality",
    "Commute",
    "Calendar",
    "News",
    "Lifestyle",
    "Recap"
  ],
  "voices": ["Zephyr", "Puck"],
  "audio_format": "wav",
  "questions_count": 45,
  "word_count": 750
}
```

---

## Error Responses

**400 Bad Request:**
```json
{
  "error": "Request body must be JSON"
}
```

**404 Not Found:**
```json
{
  "error": "Job not found"
}
```

**429 Quota Exceeded:**
```json
{
  "status": "quota_exceeded",
  "error": "Gemini API quota exceeded",
  "message": "429 RESOURCE_EXHAUSTED..."
}
```

**500 Internal Server Error:**
```json
{
  "error": "Error message",
  "status": "failed"
}
```

---

## Test Scripts

Run the provided test scripts:

```bash
# Mini test (fastest - 4 lines)
bash test_mini.sh

# Test news only
bash test_news_only.sh

# Test script generation (no audio)
bash test_script_only.sh

# Complete podcast generation (async)
bash test_curl.sh

# Test new features (audio, sharing, management)
bash test_features.sh
```

---

## Logs

All operations are logged to `./logs/app_YYYYMMDD.log` with detailed information about:
- API requests and responses
- News fetching
- Script generation
- Question generation
- TTS processing
- File operations
- Errors and exceptions
