import requests
import json
import os
from logger import get_logger
PPLX_API_KEY = os.environ.get("PPLX_API_KEY")
logger = get_logger(__name__)


def fetch_news_for_category(prompt):
    """Helper to fetch news from Perplexity."""
    logger.info(f"Starting news fetch with prompt: {prompt[:100]}...")

    if not PPLX_API_KEY:
        logger.error("PPLX_API_KEY not found in environment")
        raise RuntimeError("Missing PPLX_API_KEY environment variable")

    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "sonar",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "stream": False
    }
    headers = {
        "Authorization": f"Bearer {PPLX_API_KEY}",
        "Content-Type": "application/json"
    }

    logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=60)
        logger.info(f"API response status: {r.status_code}")
        r.raise_for_status()
        data = r.json()
        logger.debug(
            f"API response data: {json.dumps(data, indent=2)[:500]}...")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise

    try:
        content = data["choices"][0]["message"]["content"]
        logger.info(
            f"Successfully extracted news content (length: {len(content)})")
        return content
    except Exception as e:
        logger.warning(
            f"Failed to extract from choices, trying 'text' field: {str(e)}")
        if "text" in data:
            return data["text"]
        logger.error(f"Failed to parse API response: {str(e)}")
        raise RuntimeError("Failed to fetch news from Perplexity API")


def fetch_latest_news(interests=None, home_location=None, work_location=None):
    """
    Fetch latest news separately for interests, home location, and work location.
    Returns dict with separate news sections.
    """
    logger.info(
        f"Starting news fetch - interests: {interests}, home: {home_location}, work: {work_location}")
    news_data = {}

    # Fetch interest-based news
    if interests:
        logger.info(f"Fetching interest-based news for: {interests}")
        try:
            topics_str = ", ".join(interests) if isinstance(
                interests, list) else interests
            prompt = f"Provide latest news summary about: {topics_str}. Keep it concise and factual."
            news_data["interests"] = fetch_news_for_category(prompt)
            logger.info(
                f"Successfully fetched interest news (length: {len(news_data['interests'])})")
        except Exception as e:
            logger.exception(f"Failed to fetch interest news: {str(e)}")
            news_data["interests"] = "Interest news unavailable."

    # Fetch home location news
    if home_location:
        logger.info(f"Fetching home location news for: {home_location}")
        try:
            prompt = f"Provide latest local news and updates for {home_location}. Keep it concise and factual."
            news_data["home_location"] = fetch_news_for_category(prompt)
            logger.info(
                f"Successfully fetched home location news (length: {len(news_data['home_location'])})")
        except Exception as e:
            logger.exception(f"Failed to fetch home location news: {str(e)}")
            news_data["home_location"] = "Home location news unavailable."

    # Fetch work location news
    if work_location:
        logger.info(f"Fetching work location news for: {work_location}")
        try:
            prompt = f"Provide latest local news and updates for {work_location}. Keep it concise and factual."
            news_data["work_location"] = fetch_news_for_category(prompt)
            logger.info(
                f"Successfully fetched work location news (length: {len(news_data['work_location'])})")
        except Exception as e:
            logger.exception(f"Failed to fetch work location news: {str(e)}")
            news_data["work_location"] = "Work location news unavailable."

    logger.info(f"Completed news fetch with {len(news_data)} sections")
    return news_data
