import requests
import json
import os
from config import PPLX_API_KEY, TMP_DIR
from logger import get_logger

logger = get_logger(__name__)

def generate_answer(podcast_id, question, context=""):
    """Generate detailed answer for a question using Perplexity."""
    logger.info(f"Generating answer for question: {question[:100]}...")
    
    if not PPLX_API_KEY:
        logger.error("PPLX_API_KEY not found")
        raise RuntimeError("Missing PPLX_API_KEY environment variable")
    
    url = "https://api.perplexity.ai/chat/completions"
    
    # Build prompt with context
    prompt = f"""Based on the podcast content provided below, answer this question: {question}

Podcast Content:
{context}

Provide a detailed answer based primarily on the podcast content. If the podcast doesn't fully address the question, you may supplement with relevant general knowledge, but clearly indicate what comes from the podcast versus additional information."""
    
    payload = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "stream": False
    }
    headers = {
        "Authorization": f"Bearer {PPLX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        logger.info(f"Answer API response status: {r.status_code}")
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Answer generation request failed: {str(e)}")
        raise
    
    try:
        answer = data["choices"][0]["message"]["content"]
        logger.info(f"Successfully generated answer (length: {len(answer)})")
        return answer
    except Exception as e:
        logger.error(f"Failed to parse answer response: {str(e)}")
        raise RuntimeError("Failed to generate answer")

def save_answer(podcast_id, timestamp, question, answer):
    """Save answer to answers file."""
    answers_file = os.path.join(TMP_DIR, podcast_id, f"{podcast_id}_answers.json")
    
    # Load existing answers or create new
    if os.path.exists(answers_file):
        with open(answers_file, "r", encoding="utf-8") as f:
            answers = json.load(f)
    else:
        answers = []
    
    # Add new answer
    answers.append({
        "timestamp": timestamp,
        "question": question,
        "answer": answer,
        "answered_at": json.dumps({"time": "now"})
    })
    
    # Save back
    with open(answers_file, "w", encoding="utf-8") as f:
        json.dump(answers, f, indent=2)
    
    logger.info(f"Saved answer to {answers_file}")
    return answers_file
