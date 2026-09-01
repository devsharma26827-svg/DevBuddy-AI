"""
Centralized Gemini Configuration and API Wrapper.
Handles API key loading, configured model overrides, and automatic model retries
and fallbacks (gemini-2.5-flash -> gemini-2.5-pro -> gemini-2.0-flash)
upon encountering model unavailability or API 404 errors.
"""

import os
import logging
from typing import Any, List, Optional
from google import genai
from google.genai import types

logger = logging.getLogger("ProjectPilot.GeminiConfig")

# Define fallback order for model availability
DEFAULT_MODEL_FALLBACKS: List[str] = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash"
]

def get_configured_model() -> str:
    """
    Retrieves the primary model configured in the .env file.
    Defaults to 'gemini-2.5-flash'.
    
    Returns:
        str: Configured Gemini model name.
    """
    try:
        import streamlit as st
        val = st.session_state.get("PERSIST_GEMINI_MODEL")
        if val:
            return val
    except Exception:
        pass
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def generate_gemini_content(
    api_key: str,
    prompt: str,
    response_schema: Optional[Any] = None,
    temperature: float = 0.2,
    logs_accumulator: Optional[List[str]] = None
) -> str:
    """
    Centralized helper for calling the Gemini API with automatic model retries,
    fallback lists, and logging indicators.
    
    Args:
        api_key (str): Gemini API Key for authentication.
        prompt (str): Prompt text to send.
        response_schema (Optional[Any]): Pydantic schema class for structured JSON formatting.
        temperature (float): Controls response randomness.
        logs_accumulator (Optional[List[str]]): List to accumulate logging messages for visual UI feedback.
        
    Returns:
        str: Generated content string (JSON formatted if schema is provided).
    """
    primary_model = get_configured_model()
    
    # Compile candidate list: primary model first, then the fallback defaults
    candidate_models = [primary_model]
    for model in DEFAULT_MODEL_FALLBACKS:
        if model not in candidate_models:
            candidate_models.append(model)
            
    client = genai.Client(api_key=api_key)
    last_exception = None
    
    for model_name in candidate_models:
        log_msg = f"Trying Gemini Model: {model_name}"
        if logs_accumulator is not None:
            logs_accumulator.append(log_msg)
        logger.info(log_msg)
        
        try:
            # Build API configuration options using latest Google GenAI SDK defaults
            config_args = {
                "temperature": temperature
            }
            if response_schema is not None:
                config_args["response_mime_type"] = "application/json"
                config_args["response_schema"] = response_schema
                
            config = types.GenerateContentConfig(**config_args)
            
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            
            success_msg = f"Connected successfully using model: {model_name}"
            if logs_accumulator is not None:
                logs_accumulator.append(success_msg)
            logger.info(success_msg)
            
            return response.text
            
        except Exception as e:
            err_msg = f"Model {model_name} unavailable: {str(e)}"
            if logs_accumulator is not None:
                logs_accumulator.append(f"Model unavailable... ({str(e)})")
            logger.warning(err_msg)
            last_exception = e
            continue
            
    # If all models failed, raise the last exception
    raise last_exception if last_exception else RuntimeError("All configured Gemini models failed.")
