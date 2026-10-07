"""
CodeSecure AI — Safe JSON Extraction & Parsing Utility
Robustly parses and normalizes JSON responses from local LLMs.
"""

import json
import re
from typing import Any, Dict, Optional
from app.utils.logging_utils import get_logger

logger = get_logger("json_utils")


def extract_json_from_llm(raw_text: str) -> Optional[Dict[str, Any]]:
    """
    Extracts and parses JSON object or array from LLM textual output.
    Handles markdown fences (```json ... ```), preamble text, and common formatting anomalies.
    """
    if not raw_text or not raw_text.strip():
        logger.warning("Empty LLM output provided for JSON parsing.")
        return None

    cleaned = raw_text.strip()

    # 1. Try direct JSON parsing
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            return {"findings": data}
    except Exception:
        pass

    # 2. Extract content from markdown fenced code blocks: ```json ... ``` or ``` ... ```
    fence_pattern = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
    matches = fence_pattern.findall(cleaned)
    for block in matches:
        try:
            data = json.loads(block.strip())
            if isinstance(data, dict):
                return data
            if isinstance(data, list):
                return {"findings": data}
        except Exception:
            continue

    # 3. Find outermost curly braces { ... }
    start_brace = cleaned.find("{")
    end_brace = cleaned.rfind("}")
    if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
        candidate = cleaned[start_brace : end_brace + 1]
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return data
        except Exception:
            # 4. Attempt simple cleanup for common syntax errors: trailing commas before } or ]
            cleaned_candidate = re.sub(r",\s*([\]}])", r"\1", candidate)
            try:
                data = json.loads(cleaned_candidate)
                if isinstance(data, dict):
                    return data
            except Exception as e:
                logger.warning(f"Failed parsing braced substring: {str(e)[:100]}")

    # 5. Find outermost square brackets [ ... ]
    start_bracket = cleaned.find("[")
    end_bracket = cleaned.rfind("]")
    if start_bracket != -1 and end_bracket != -1 and end_bracket > start_bracket:
        candidate = cleaned[start_bracket : end_bracket + 1]
        try:
            data = json.loads(candidate)
            if isinstance(data, list):
                return {"findings": data}
        except Exception:
            cleaned_candidate = re.sub(r",\s*([\]}])", r"\1", candidate)
            try:
                data = json.loads(cleaned_candidate)
                if isinstance(data, list):
                    return {"findings": data}
            except Exception:
                pass

    logger.error("All JSON extraction strategies failed for LLM response.")
    return None
