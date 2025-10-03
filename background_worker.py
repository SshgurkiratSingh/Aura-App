import threading
import logging
from job_manager import update_job, JobStatus, JobStage
from news_service import fetch_latest_news
from script_service import generate_script_with_perplexity, generate_questions_for_script
from tts_service import generate_podcast
import os
import json
from datetime import datetime
from config import TMP_DIR

logger = logging.getLogger(__name__)

def process_podcast_async(request_id, user_data, podcast_dir):
    """Process podcast generation in background thread."""
    try:
        logger.info(f"Background processing started for {request_id}")
        
        # Fetch news
        update_job(request_id, status=JobStatus.RUNNING, progress=20, stage=JobStage.NEWS_FETCH, eta_seconds=90)
        interests = user_data.get("interests", [])
        home_location = user_data.get("home_location")
        work_location = user_data.get("work_location")
        
        news_data = {}
        if interests or home_location or work_location:
            news_data = fetch_latest_news(interests, home_location, work_location)
        
        news_file = os.path.join(podcast_dir, f"{request_id}_news.json")
        with open(news_file, "w", encoding="utf-8") as f:
            json.dump(news_data, f, indent=2)
        
        # Generate script
        update_job(request_id, progress=40, stage=JobStage.SCRIPT_GEN, eta_seconds=60)
        user_data["news"] = news_data
        script = generate_script_with_perplexity(user_data)
        
        script_file = os.path.join(podcast_dir, f"{request_id}_script.txt")
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(script)
        
        # Generate audio
        update_job(request_id, progress=60, stage=JobStage.TTS_GEN, eta_seconds=45)
        audio_prefix = os.path.join(podcast_dir, request_id)
        audio_files = []
        try:
            audio_files = generate_podcast(script, output_prefix=audio_prefix)
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                logger.warning(f"Audio generation skipped: {str(e)}")
                audio_files = ["Audio generation unavailable - quota exceeded"]
            else:
                raise
        
        # Generate questions
        update_job(request_id, progress=80, stage=JobStage.PACKAGING, eta_seconds=10)
        questions = generate_questions_for_script(script)
        
        questions_file = os.path.join(podcast_dir, f"{request_id}_questions.json")
        with open(questions_file, "w", encoding="utf-8") as f:
            json.dump(questions, f, indent=2)
        
        # Calculate duration and topics
        from audio_service import get_audio_duration
        import glob
        
        total_duration = 0
        audio_segments = glob.glob(os.path.join(podcast_dir, f"{request_id}_seg*.wav"))
        for audio_file in audio_segments:
            try:
                total_duration += get_audio_duration(audio_file)
            except:
                pass
        
        # Extract topics from script
        topics = []
        if "news" in script.lower():
            topics.append("News")
        if "weather" in script.lower():
            topics.append("Weather")
        if "commute" in script.lower() or "traffic" in script.lower():
            topics.append("Commute")
        if interests:
            topics.extend(interests[:3])
        
        # Generate chapter markers (every 20 seconds)
        chapters = []
        words_per_minute = 150
        words = script.split()
        words_per_20s = int(words_per_minute * (20 / 60.0))
        
        for i in range(0, len(words), words_per_20s):
            timestamp_seconds = (i // words_per_20s) * 20
            m = timestamp_seconds // 60
            s = timestamp_seconds % 60
            segment_text = " ".join(words[i:i+50])  # First 50 words as preview
            chapters.append({
                "timestamp": f"{m:02d}:{s:02d}",
                "title": f"Segment {i // words_per_20s + 1}",
                "preview": segment_text[:100] + "..."
            })
        
        # Save metadata
        metadata = {
            "id": request_id,
            "created_at": datetime.utcnow().isoformat(),
            "duration": round(total_duration, 2),
            "topics": topics,
            "chapters": chapters,
            "sections": ["Weather", "Air Quality", "Commute", "Calendar", "News", "Lifestyle", "Recap"],
            "voices": ["Zephyr", "Puck"],
            "audio_format": "wav",
            "questions_count": len(questions),
            "word_count": len(words)
        }
        metadata_file = os.path.join(podcast_dir, f"{request_id}_metadata.json")
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        
        # Prepare result
        result = {
            "id": request_id,
            "script": f"/files/{request_id}/{request_id}_script.txt",
            "questions": f"/files/{request_id}/{request_id}_questions.json",
            "audio": [f"/files/{request_id}/{os.path.basename(f)}" for f in audio_files if isinstance(f, str) and f.endswith('.wav')],
            "metadata": f"/files/{request_id}/{request_id}_metadata.json",
            "news": f"/files/{request_id}/{request_id}_news.json"
        }
        
        update_job(request_id, status=JobStatus.COMPLETED, progress=100, stage="Done", eta_seconds=0, result=result)
        logger.info(f"Background processing completed for {request_id}")
        
    except Exception as e:
        logger.exception(f"Background processing failed for {request_id}")
        update_job(request_id, status=JobStatus.FAILED, error=str(e))

def start_podcast_generation(request_id, user_data, podcast_dir):
    """Start podcast generation in background thread."""
    thread = threading.Thread(
        target=process_podcast_async,
        args=(request_id, user_data, podcast_dir),
        daemon=True
    )
    thread.start()
    logger.info(f"Started background thread for {request_id}")
