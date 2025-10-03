from flask import Flask, request, jsonify, send_file
import logging
import os
import uuid
import json
import zipfile
import glob
from datetime import datetime
from config import TMP_DIR
from job_manager import create_job, update_job, get_job, get_job_result, JobStatus, JobStage
from answer_service import generate_answer, save_answer
from background_worker import start_podcast_generation
from audio_service import concatenate_audio_files, get_audio_duration

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/fetch-news', methods=['POST'])
def fetch_news_api():
    """Standalone API to fetch news only."""
    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({"error": "Request body must be JSON"}), 400

        interests = payload.get("interests", [])
        home_location = payload.get("home_location")
        work_location = payload.get("work_location")

        if not interests and not home_location and not work_location:
            return jsonify({"error": "At least one of interests, home_location, or work_location required"}), 400

        news_data = fetch_latest_news(interests, home_location, work_location)
        
        # Save news to file
        news_id = f"news-{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
        news_file = os.path.join(TMP_DIR, f"{news_id}.json")
        with open(news_file, "w", encoding="utf-8") as f:
            json.dump({"news": news_data, "metadata": {"interests": interests, "home_location": home_location, "work_location": work_location}}, f, indent=2)
        logging.info("Saved news to %s", news_file)
        
        return jsonify({
            "status": "success",
            "news": news_data,
            "news_file": news_file,
            "metadata": {
                "interests": interests,
                "home_location": home_location,
                "work_location": work_location
            }
        })
        
    except Exception as e:
        logging.exception("Error in fetch_news_api")
        return jsonify({"error": str(e)}), 500

@app.route('/test-news-script', methods=['POST'])
def test_news_script():
    """Test endpoint to check news fetching and script generation without audio."""
    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({"error": "Request body must be JSON"}), 400

        user_preferences = payload.get("user_preferences", {})
        weather_info = payload.get("weather_info", {})
        interests = payload.get("interests", [])
        home_location = payload.get("home_location")
        work_location = payload.get("work_location")
        extra = payload.get("extra", {})

        test_id = f"test-{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"

        # Fetch news separately
        news_data = {}
        if interests or home_location or work_location:
            try:
                news_data = fetch_latest_news(interests, home_location, work_location)
                logging.info("Fetched news successfully")
            except Exception as e:
                logging.exception("Failed to fetch news")
                return jsonify({"error": f"News fetch failed: {str(e)}"}), 500

        # Save news
        news_file = os.path.join(TMP_DIR, f"{test_id}_news.json")
        with open(news_file, "w", encoding="utf-8") as f:
            json.dump(news_data, f, indent=2)
        logging.info("Saved news to %s", news_file)

        # Generate script
        user_data = {
            "user_preferences": user_preferences,
            "weather_info": weather_info,
            "home_location": home_location,
            "work_location": work_location,
            "news": news_data,
            "extra": extra
        }
        
        script = generate_script_with_perplexity(user_data)
        
        # Save script
        script_file = os.path.join(TMP_DIR, f"{test_id}_script.txt")
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(script)
        logging.info("Saved script to %s", script_file)
        
        # Save request data
        request_file = os.path.join(TMP_DIR, f"{test_id}_request.json")
        with open(request_file, "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=2)
        logging.info("Saved request to %s", request_file)
        
        return jsonify({
            "status": "success",
            "test_id": test_id,
            "news": news_data,
            "news_file": news_file,
            "script": script,
            "script_file": script_file,
            "request_file": request_file
        })
        
    except Exception as e:
        logging.exception("Error in test_news_script")
        return jsonify({"error": str(e)}), 500

@app.route('/generate-podcast', methods=['POST'])
def generate_podcast_api():
    """Main endpoint to generate complete podcast with audio."""
    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({"error": "Request body must be JSON"}), 400

        user_preferences = payload.get("user_preferences", {})
        weather_info = payload.get("weather_info", {})
        interests = payload.get("interests", [])
        home_location = payload.get("home_location")
        work_location = payload.get("work_location")
        extra = payload.get("extra", {})

        # Fetch news separately for interests, home, and work
        news_data = {}
        if interests or home_location or work_location:
            try:
                news_data = fetch_latest_news(interests, home_location, work_location)
                logging.info("Fetched news for interests and locations")
            except Exception as e:
                logging.exception("Failed to fetch news")
                news_data = {"error": "News unavailable at this time."}

        # Compose user data
        user_data = {
            "user_preferences": user_preferences,
            "weather_info": weather_info,
            "home_location": home_location,
            "work_location": work_location,
            "news": news_data,
            "extra": extra
        }

        request_id = f"podcast-{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
        
        # Create job
        create_job(request_id, user_data)
        
        # Create podcast directory
        podcast_dir = os.path.join(TMP_DIR, request_id)
        os.makedirs(podcast_dir, exist_ok=True)
        
        # Save request data
        request_data_file = os.path.join(podcast_dir, f"{request_id}_request.json")
        with open(request_data_file, "w", encoding="utf-8") as f:
            json.dump(user_data, f, indent=2)
        
        logging.info("Created job %s, starting background processing", request_id)
        
        # Start background processing
        start_podcast_generation(request_id, user_data, podcast_dir)
        
        # Return immediately
        response = {
            "id": request_id,
            "status": "QUEUED",
            "message": "Podcast generation started",
            "status_url": f"/status/{request_id}",
            "result_url": f"/get-podcast/{request_id}",
            "download_url": f"/download-podcast/{request_id}"
        }
        
        return jsonify(response), 202
        
    except Exception as e:
        logging.exception("Error in generate_podcast_api")
        return jsonify({"error": str(e), "status": "failed"}), 500

@app.route('/test-tts', methods=['POST'])
def test_tts():
    """Test endpoint for TTS generation only."""
    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({"error": "Request body must be JSON"}), 400

        script = payload.get("script")
        if not script:
            return jsonify({"error": "script field required"}), 400

        test_id = f"tts-test-{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
        logging.info(f"Testing TTS with test_id={test_id}")

        # Generate audio
        try:
            audio_files = generate_podcast(script, output_prefix=test_id)
            logging.info(f"Generated {len(audio_files)} audio files")
            
            return jsonify({
                "status": "success",
                "test_id": test_id,
                "audio_files": audio_files,
                "total_files": len(audio_files)
            })
        except Exception as e:
            if "quota" in str(e).lower() or "429" in str(e):
                logging.warning(f"TTS quota exceeded: {str(e)}")
                return jsonify({
                    "status": "quota_exceeded",
                    "error": "Gemini API quota exceeded",
                    "message": str(e)
                }), 429
            else:
                raise
        
    except Exception as e:
        logging.exception("Error in test_tts")
        return jsonify({"error": str(e)}), 500

@app.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get job status."""
    job = get_job(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    
    response = {
        "id": job["id"],
        "status": job["status"],
        "progress": job["progress"],
        "stage": job["stage"],
        "eta_seconds": job["eta_seconds"]
    }
    
    if job["status"] == JobStatus.COMPLETED:
        response["result_url"] = f"/get-podcast/{job_id}"
    elif job["status"] == JobStatus.FAILED:
        response["error"] = job["error"]
    
    return jsonify(response)

@app.route('/get-podcast/<job_id>', methods=['GET'])
def get_podcast_result(job_id):
    """Get podcast result files."""
    result = get_job_result(job_id)
    if not result:
        return jsonify({"error": "Job not completed or not found"}), 404
    
    return jsonify(result)

@app.route('/download-podcast/<job_id>', methods=['GET'])
def download_podcast(job_id):
    """Download podcast as zip file."""
    result = get_job_result(job_id)
    if not result:
        return jsonify({"error": "Job not completed or not found"}), 404
    
    # Create zip file
    podcast_dir = os.path.join(TMP_DIR, job_id)
    zip_path = os.path.join(TMP_DIR, f"{job_id}_package.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(podcast_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, podcast_dir)
                zipf.write(file_path, arcname)
    
    return send_file(zip_path, as_attachment=True, download_name=f"{job_id}_package.zip")

@app.route('/answer-question', methods=['POST'])
def answer_question():
    """Answer a question from the podcast."""
    try:
        payload = request.get_json(force=True)
        if not payload:
            return jsonify({"error": "Request body must be JSON"}), 400
        
        podcast_id = payload.get("podcast_id")
        timestamp = payload.get("timestamp")
        question = payload.get("question")
        
        if not all([podcast_id, timestamp, question]):
            return jsonify({"error": "podcast_id, timestamp, and question required"}), 400
        
        # Load full script for context
        script_file = os.path.join(TMP_DIR, podcast_id, f"{podcast_id}_script.txt")
        context = ""
        if os.path.exists(script_file):
            with open(script_file, "r", encoding="utf-8") as f:
                context = f.read()  # Full script as context
        
        # Generate answer
        answer = generate_answer(podcast_id, question, context)
        
        # Save answer
        answers_file = save_answer(podcast_id, timestamp, question, answer)
        
        return jsonify({
            "status": "success",
            "answer": answer,
            "answers_file": answers_file
        })
        
    except Exception as e:
        logging.exception("Error in answer_question")
        return jsonify({"error": str(e)}), 500

@app.route('/test-mini-podcast', methods=['POST'])
def test_mini_podcast():
    """Minimal test endpoint - generates 4-line podcast to verify structure."""
    try:
        from news_service import fetch_latest_news
        from script_service import generate_script_with_perplexity
        from tts_service import generate_podcast
        
        test_id = f"mini-{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
        podcast_dir = os.path.join(TMP_DIR, test_id)
        os.makedirs(podcast_dir, exist_ok=True)
        
        # Minimal test data
        interests = ["AI"]
        
        # Fetch minimal news
        news_data = fetch_latest_news(interests, None, None)
        news_file = os.path.join(podcast_dir, f"{test_id}_news.json")
        with open(news_file, "w") as f:
            json.dump(news_data, f, indent=2)
        
        # Generate 4-line script
        user_data = {"news": news_data, "user_preferences": {"tone": "casual"}}
        full_script = generate_script_with_perplexity(user_data)
        mini_script = "\n".join(full_script.split("\n")[:4])  # Only 4 lines
        
        script_file = os.path.join(podcast_dir, f"{test_id}_script.txt")
        with open(script_file, "w") as f:
            f.write(mini_script)
        
        # Generate audio
        output_prefix = os.path.join(podcast_dir, test_id)
        audio_files = generate_podcast(mini_script, output_prefix)
        
        # Save metadata
        metadata = {
            "id": test_id,
            "news_file": news_file,
            "script_file": script_file,
            "audio_files": audio_files,
            "script_preview": mini_script
        }
        metadata_file = os.path.join(podcast_dir, f"{test_id}_metadata.json")
        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)
        
        return jsonify({
            "status": "success",
            "id": test_id,
            "directory": podcast_dir,
            "files": {
                "news": news_file,
                "script": script_file,
                "audio": audio_files,
                "metadata": metadata_file
            },
            "script_preview": mini_script
        })
        
    except Exception as e:
        logging.exception("Error in test_mini_podcast")
        return jsonify({"error": str(e)}), 500

@app.route('/get-full-audio/<podcast_id>', methods=['GET'])
def get_full_audio(podcast_id):
    """Get concatenated full audio file."""
    podcast_dir = os.path.join(TMP_DIR, podcast_id)
    full_audio_path = os.path.join(podcast_dir, f"{podcast_id}_full.wav")
    
    # Check if already exists
    if os.path.exists(full_audio_path):
        return send_file(full_audio_path, mimetype='audio/wav')
    
    # Find all segment files
    audio_files = sorted(glob.glob(os.path.join(podcast_dir, f"{podcast_id}_seg*.wav")))
    if not audio_files:
        return jsonify({"error": "No audio files found"}), 404
    
    # Concatenate
    try:
        concatenate_audio_files(audio_files, full_audio_path)
        return send_file(full_audio_path, mimetype='audio/wav')
    except Exception as e:
        logging.exception("Error concatenating audio")
        return jsonify({"error": str(e)}), 500

@app.route('/podcasts', methods=['GET'])
def list_podcasts():
    """List all podcasts."""
    try:
        podcast_dirs = sorted(glob.glob(os.path.join(TMP_DIR, "podcast-*")), reverse=True)
        podcasts = []
        
        for podcast_dir in podcast_dirs:
            podcast_id = os.path.basename(podcast_dir)
            metadata_file = os.path.join(podcast_dir, f"{podcast_id}_metadata.json")
            
            if os.path.exists(metadata_file):
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    podcasts.append({
                        "id": podcast_id,
                        "created_at": metadata.get("created_at"),
                        "duration": metadata.get("duration"),
                        "topics": metadata.get("topics", [])
                    })
            else:
                podcasts.append({
                    "id": podcast_id,
                    "created_at": None,
                    "duration": None,
                    "topics": []
                })
        
        return jsonify({"podcasts": podcasts, "total": len(podcasts)})
    except Exception as e:
        logging.exception("Error listing podcasts")
        return jsonify({"error": str(e)}), 500

@app.route('/podcast/<podcast_id>', methods=['DELETE'])
def delete_podcast(podcast_id):
    """Delete a podcast."""
    try:
        podcast_dir = os.path.join(TMP_DIR, podcast_id)
        if not os.path.exists(podcast_dir):
            return jsonify({"error": "Podcast not found"}), 404
        
        import shutil
        shutil.rmtree(podcast_dir)
        logging.info(f"Deleted podcast: {podcast_id}")
        
        return jsonify({"status": "success", "message": f"Deleted {podcast_id}"})
    except Exception as e:
        logging.exception("Error deleting podcast")
        return jsonify({"error": str(e)}), 500

@app.route('/share/<podcast_id>', methods=['POST'])
def share_podcast(podcast_id):
    """Generate shareable link for podcast."""
    try:
        podcast_dir = os.path.join(TMP_DIR, podcast_id)
        if not os.path.exists(podcast_dir):
            return jsonify({"error": "Podcast not found"}), 404
        
        # Generate share token
        share_token = uuid.uuid4().hex[:12]
        share_file = os.path.join(podcast_dir, f"{podcast_id}_share.json")
        
        share_data = {
            "token": share_token,
            "podcast_id": podcast_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": None  # No expiration for now
        }
        
        with open(share_file, 'w') as f:
            json.dump(share_data, f, indent=2)
        
        share_url = f"/shared/{share_token}"
        
        return jsonify({
            "status": "success",
            "share_token": share_token,
            "share_url": share_url,
            "download_url": f"{share_url}/download"
        })
    except Exception as e:
        logging.exception("Error creating share link")
        return jsonify({"error": str(e)}), 500

@app.route('/shared/<share_token>', methods=['GET'])
def get_shared_podcast(share_token):
    """Access shared podcast."""
    try:
        # Find podcast with this share token
        podcast_dirs = glob.glob(os.path.join(TMP_DIR, "podcast-*"))
        
        for podcast_dir in podcast_dirs:
            podcast_id = os.path.basename(podcast_dir)
            share_file = os.path.join(podcast_dir, f"{podcast_id}_share.json")
            
            if os.path.exists(share_file):
                with open(share_file, 'r') as f:
                    share_data = json.load(f)
                    if share_data["token"] == share_token:
                        # Return podcast info
                        metadata_file = os.path.join(podcast_dir, f"{podcast_id}_metadata.json")
                        if os.path.exists(metadata_file):
                            with open(metadata_file, 'r') as mf:
                                metadata = json.load(mf)
                        else:
                            metadata = {}
                        
                        return jsonify({
                            "podcast_id": podcast_id,
                            "metadata": metadata,
                            "audio_url": f"/shared/{share_token}/audio",
                            "download_url": f"/shared/{share_token}/download"
                        })
        
        return jsonify({"error": "Invalid share token"}), 404
    except Exception as e:
        logging.exception("Error accessing shared podcast")
        return jsonify({"error": str(e)}), 500

@app.route('/shared/<share_token>/audio', methods=['GET'])
def get_shared_audio(share_token):
    """Get audio for shared podcast."""
    try:
        podcast_dirs = glob.glob(os.path.join(TMP_DIR, "podcast-*"))
        
        for podcast_dir in podcast_dirs:
            podcast_id = os.path.basename(podcast_dir)
            share_file = os.path.join(podcast_dir, f"{podcast_id}_share.json")
            
            if os.path.exists(share_file):
                with open(share_file, 'r') as f:
                    share_data = json.load(f)
                    if share_data["token"] == share_token:
                        full_audio_path = os.path.join(podcast_dir, f"{podcast_id}_full.wav")
                        
                        if not os.path.exists(full_audio_path):
                            audio_files = sorted(glob.glob(os.path.join(podcast_dir, f"{podcast_id}_seg*.wav")))
                            if audio_files:
                                concatenate_audio_files(audio_files, full_audio_path)
                        
                        if os.path.exists(full_audio_path):
                            return send_file(full_audio_path, mimetype='audio/wav')
        
        return jsonify({"error": "Invalid share token"}), 404
    except Exception as e:
        logging.exception("Error getting shared audio")
        return jsonify({"error": str(e)}), 500

@app.route('/shared/<share_token>/download', methods=['GET'])
def download_shared_podcast(share_token):
    """Download shared podcast as zip."""
    try:
        podcast_dirs = glob.glob(os.path.join(TMP_DIR, "podcast-*"))
        
        for podcast_dir in podcast_dirs:
            podcast_id = os.path.basename(podcast_dir)
            share_file = os.path.join(podcast_dir, f"{podcast_id}_share.json")
            
            if os.path.exists(share_file):
                with open(share_file, 'r') as f:
                    share_data = json.load(f)
                    if share_data["token"] == share_token:
                        zip_path = os.path.join(TMP_DIR, f"{podcast_id}_shared.zip")
                        
                        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                            for root, dirs, files in os.walk(podcast_dir):
                                for file in files:
                                    if not file.endswith('_share.json'):
                                        file_path = os.path.join(root, file)
                                        arcname = os.path.relpath(file_path, podcast_dir)
                                        zipf.write(file_path, arcname)
                        
                        return send_file(zip_path, as_attachment=True, download_name=f"{podcast_id}.zip")
        
        return jsonify({"error": "Invalid share token"}), 404
    except Exception as e:
        logging.exception("Error downloading shared podcast")
        return jsonify({"error": str(e)}), 500

@app.route('/files/<path:filepath>', methods=['GET'])
def serve_file(filepath):
    """Serve generated files."""
    file_path = os.path.join(TMP_DIR, filepath)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "time": datetime.utcnow().isoformat()})

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
