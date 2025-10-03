import requests
import json
from config import PPLX_API_KEY, SYSTEM_PROMPT
from logger import get_logger

logger = get_logger(__name__)

def generate_script_with_perplexity(user_data):
    """
    Use Perplexity to generate the podcast script.
    Returns the generated script string.
    """
    logger.info("Starting script generation")
    logger.debug(f"User data: {json.dumps(user_data, indent=2)}")
    
    if not PPLX_API_KEY:
        logger.error("PPLX_API_KEY not found")
        raise RuntimeError("Missing PPLX_API_KEY environment variable")
    
    url = "https://api.perplexity.ai/chat/completions"
    prompt = f"{SYSTEM_PROMPT}\n\nUser Data: {json.dumps(user_data)}"
    logger.debug(f"Generated prompt (length: {len(prompt)})")
    
    payload = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "top_p": 0.9,
        "stream": False
    }
    headers = {
        "Authorization": f"Bearer {PPLX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    logger.info("Sending script generation request to Perplexity")
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        logger.info(f"Script API response status: {r.status_code}")
        r.raise_for_status()
        data = r.json()
        logger.debug(f"Script API response: {json.dumps(data, indent=2)[:500]}...")
    except requests.exceptions.RequestException as e:
        logger.error(f"Script generation request failed: {str(e)}")
        raise
    
    try:
        script = data["choices"][0]["message"]["content"]
        logger.info(f"Successfully generated script (length: {len(script)} chars, {len(script.split())} words)")
        return script
    except Exception as e:
        logger.warning(f"Failed to extract from choices: {str(e)}")
        if "text" in data:
            return data["text"]
        logger.error("Failed to parse script response")
        raise RuntimeError("Unexpected response from Perplexity API")

def generate_question_from_content(content):
    """Generate one question from content."""
    logger.debug(f"Generating question for content: {content[:100]}...")
    
    if not PPLX_API_KEY:
        logger.error("PPLX_API_KEY not found")
        raise RuntimeError("Missing PPLX_API_KEY environment variable")
    
    url = "https://api.perplexity.ai/chat/completions"
    prompt = f"Generate a relevant question based on this podcast content (return only the question): {content.strip()[:500]}"
    payload = {
        "model": "sonar",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "stream": False
    }
    headers = {
        "Authorization": f"Bearer {PPLX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        logger.debug(f"Question API response status: {r.status_code}")
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Question generation request failed: {str(e)}")
        raise
    
    try:
        question = data["choices"][0]["message"]["content"].strip()
        logger.debug(f"Generated question: {question}")
        return question
    except Exception as e:
        logger.warning(f"Failed to extract question: {str(e)}")
        if "text" in data:
            return data["text"].strip()
        logger.error("Failed to parse question response")
        raise RuntimeError("Failed to generate question")

def generate_multiple_questions_from_content(content, num_questions=3):
    """Generate multiple questions from content."""
    logger.debug(f"Generating {num_questions} questions for content: {content[:100]}...")
    
    if not PPLX_API_KEY:
        logger.error("PPLX_API_KEY not found")
        raise RuntimeError("Missing PPLX_API_KEY environment variable")
    
    url = "https://api.perplexity.ai/chat/completions"
    prompt = f"Generate {num_questions} different relevant questions based on this podcast content. Return only the questions, one per line, numbered 1-{num_questions}: {content.strip()[:500]}"
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
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        logger.debug(f"Multiple questions API response status: {r.status_code}")
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Multiple questions generation request failed: {str(e)}")
        raise
    
    try:
        response_text = data["choices"][0]["message"]["content"].strip()
        # Parse numbered questions
        import re
        questions = re.findall(r'\d+\.\s*(.+?)(?=\n\d+\.|$)', response_text, re.DOTALL)
        questions = [q.strip() for q in questions if q.strip()]
        logger.debug(f"Generated {len(questions)} questions: {questions}")
        return questions[:num_questions]  # Ensure we return exactly num_questions
    except Exception as e:
        logger.warning(f"Failed to parse multiple questions: {str(e)}")
        # Fallback: return generic questions
        return ["Would you like to hear more about this topic?"] * num_questions

def generate_questions_for_script(script, words_per_minute=150, questions_per_segment=3):
    """Generate all questions in a single LLM call."""
    logger.info(f"Starting question generation for script ({questions_per_segment} questions per segment)")
    target_seconds = 20
    words_per_20s = int(words_per_minute * (target_seconds / 60.0))
    all_words = script.split()
    num_segments = (len(all_words) + words_per_20s - 1) // words_per_20s
    total_questions = num_segments * questions_per_segment
    logger.info(f"Script has {len(all_words)} words, {num_segments} segments, generating {total_questions} questions in single call")
    
    if not PPLX_API_KEY:
        raise RuntimeError("Missing PPLX_API_KEY environment variable")
    
    # Build segment info for prompt
    segments_info = []
    idx = 0
    for seg_idx in range(num_segments):
        segment_words = all_words[idx: idx + words_per_20s]
        content = " ".join(segment_words)
        timestamp_seconds = seg_idx * target_seconds
        m = timestamp_seconds // 60
        s = timestamp_seconds % 60
        segments_info.append({
            "segment": seg_idx + 1,
            "timestamp": f"{m:02d}:{s:02d}",
            "content": content[:300]
        })
        idx += words_per_20s
    
    prompt = f"""Generate {questions_per_segment} relevant questions for each of the {num_segments} podcast segments below.

Return ONLY a JSON array with this exact format:
[
  {{"segment": 1, "timestamp": "00:00", "questions": ["question1", "question2", "question3"]}},
  {{"segment": 2, "timestamp": "00:20", "questions": ["question1", "question2", "question3"]}}
]

Segments:
{json.dumps(segments_info, indent=2)}

Return ONLY the JSON array, no other text."""
    
    url = "https://api.perplexity.ai/chat/completions"
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
        r = requests.post(url, json=payload, headers=headers, timeout=90)
        r.raise_for_status()
        data = r.json()
        response_text = data["choices"][0]["message"]["content"].strip()
        
        # Extract JSON from response
        import re
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            segments_data = json.loads(json_match.group())
        else:
            segments_data = json.loads(response_text)
        
        # Format questions
        questions = []
        for seg_data in segments_data:
            seg_num = seg_data["segment"]
            timestamp = seg_data["timestamp"]
            for q_idx, q_text in enumerate(seg_data["questions"][:questions_per_segment]):
                questions.append({
                    "id": f"q{seg_num}_{q_idx+1}",
                    "timestamp": timestamp,
                    "question": q_text
                })
        
        logger.info(f"Generated {len(questions)} questions in single call")
        return questions
        
    except Exception as e:
        logger.exception(f"Single-call question generation failed: {str(e)}")
        # Fallback to generic questions
        questions = []
        for seg_idx in range(num_segments):
            timestamp_seconds = seg_idx * target_seconds
            m = timestamp_seconds // 60
            s = timestamp_seconds % 60
            for q_idx in range(questions_per_segment):
                questions.append({
                    "id": f"q{seg_idx+1}_{q_idx+1}",
                    "timestamp": f"{m:02d}:{s:02d}",
                    "question": "Would you like to hear more about this topic?"
                })
        return questions
