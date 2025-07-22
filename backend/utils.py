--- START OF FILE backend/utils.py ---
import logging
import json
import google.generativeai as genai
from typing import Dict

logger = logging.getLogger(__name__)

async def generate_json_response(model: genai.GenerativeModel, prompt: str) -> Dict:
    """
    A centralized and robust helper to get a structured JSON response from the AI model.

    Args:
        model: An initialized instance of a genai.GenerativeModel.
        prompt: The complete, formatted prompt string to send to the model.

    Returns:
        A dictionary parsed from the AI's JSON response.
    """
    logger.info("Querying the AI oracle for wisdom...")
    try:
        response = await model.generate_content_async(prompt)
        # The AI can sometimes wrap the JSON in markdown backticks. We must be resilient.
        json_str = response.text.strip().removeprefix('```json').removesuffix('```').strip()
        logger.info("AI oracle has spoken. Parsing the prophecy...")
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"The AI's prophecy was not valid JSON: {json_str[:500]}... Error: {e}")
        return {
            "error": "AI response parsing failed: The prophecy was not in a recognizable format (Invalid JSON).", 
            "details": str(e), 
            "raw_response_snippet": json_str[:500]
        }
    except Exception as e:
        logger.error(f"Failed to generate a response from the AI oracle: {e}")
        # This handles API errors, network issues, etc.
        return {
            "error": "AI generation failed: The connection to the oracle was disrupted.", 
            "details": str(e)
        }
--- END OF FILE backend/utils.py ---