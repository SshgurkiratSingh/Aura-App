# Podcast Generation API

Personalized podcast generation with news, script, and audio using Perplexity and Gemini TTS.

## Setup

1. **Install dependencies:**
```bash
pip install flask requests google-genai
```

2. **Set environment variables:**
```bash
export PPLX_API_KEY="your_perplexity_api_key"
export GOOGLE_API_KEY="your_google_gemini_api_key"
```

Or create a `.env` file (copy from `.env.example`).

3. **Run the server:**
```bash
python app.py
```

## API Endpoints

### Core Endpoints

**1. Mini Podcast Test (4 lines - Fast)**
```bash
bash test_mini.sh
```

**2. Full Podcast Generation (Async)**
```bash
bash test_curl.sh
# Returns job ID immediately, then poll:
curl http://localhost:5000/status/{job_id}
```

**3. Fetch News Only**
```bash
bash test_news_only.sh
```

**4. Test Script Generation (No Audio)**
```bash
bash test_script_only.sh
```

### New Features

**5. Get Full Audio (Concatenated)**
```bash
curl http://localhost:5000/get-full-audio/{podcast_id} -o full.wav
```

**6. List All Podcasts**
```bash
curl http://localhost:5000/podcasts
```

**7. Delete Podcast**
```bash
curl -X DELETE http://localhost:5000/podcast/{podcast_id}
```

**8. Share Podcast**
```bash
curl -X POST http://localhost:5000/share/{podcast_id}
# Returns share token and URLs
```

**9. Access Shared Podcast**
```bash
curl http://localhost:5000/shared/{share_token}
curl http://localhost:5000/shared/{share_token}/audio -o audio.wav
curl http://localhost:5000/shared/{share_token}/download -o podcast.zip
```

## Output Files

All generated data is saved in `./tmp/{podcast_id}/` directory:
- `{id}_news.json` - News from interests, home, and work locations
- `{id}_script.txt` - Generated podcast script
- `{id}_questions.json` - Questions with timestamps (3 per 20-sec segment)
- `{id}_answers.json` - Answers to questions
- `{id}_request.json` - Complete request data
- `{id}_metadata.json` - Complete metadata with chapters and topics
- `{id}_seg{X}_{Y}.wav` - Audio segment files
- `{id}_full.wav` - Concatenated full audio (generated on request)
- `{id}_share.json` - Share token data (when shared)

## Async Processing

Full podcast generation runs in background:
1. POST `/generate-podcast` returns 202 with job ID
2. Poll GET `/status/{job_id}` for progress (0-100%)
3. GET `/get-podcast/{job_id}` for results
4. GET `/download-podcast/{job_id}` for zip download
5. GET `/get-full-audio/{job_id}` for concatenated audio

## Podcast Management

- **List podcasts**: `GET /podcasts` - View all generated podcasts
- **Delete podcast**: `DELETE /podcast/{id}` - Remove podcast and files
- **Share podcast**: `POST /share/{id}` - Generate shareable link
- **Access shared**: `GET /shared/{token}` - View shared podcast

## Metadata Features

Each podcast includes:
- **Duration**: Actual audio length in seconds
- **Topics**: Auto-extracted from content
- **Chapters**: 20-second segment markers with previews
- **Timestamps**: Question timestamps for navigation

## Logs

All logs are saved in `./logs/` directory with daily rotation.

## Current Issues

**401 Unauthorized Error:**
- Your PPLX_API_KEY is not set or invalid
- Set it with: `export PPLX_API_KEY="pplx-your-actual-key"`

**429 Quota Exceeded (Gemini):**
- Free tier quota exhausted
- Wait for quota reset or upgrade to paid tier
- The API will still generate script and questions without audio

## Quick Test

```bash
# Test all new features
bash test_features.sh
```

## Example Profiles

**Tech Professional:**
- Location: San Francisco, CA
- Interests: AI, startups, fitness
- Tone: Casual and friendly

**Student:**
- Location: Pune, India
- Interests: VLSI, robotics, gaming
- Tone: Energetic and motivational

**Healthcare Professional:**
- Location: Boston, MA
- Interests: Medical research, health tech, wellness
- Tone: Professional and informative
