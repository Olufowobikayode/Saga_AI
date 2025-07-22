--- START OF FILE backend/utils.py ---
import logging
import json
import google.generativeai as genai
from typing import Dict

logger = logging.getLogger(__name__)

async def get_prophecy_from_oracle(model: genai.GenerativeModel, prompt: str) -> Dict:
    """
    A centralized and robust rite to receive a structured JSON prophecy from the AI oracle.

    Args:
        model: An initialized instance of a genai.GenerativeModel, representing the connection to the oracle.
        prompt: The complete, formatted incantation (prompt) to send to the oracle.

    Returns:
        A dictionary parsed from the AI's JSON-formatted prophecy.
    """
    logger.info("Consulting the cosmic oracle for a prophecy...")
    try:
        response = await model.generate_content_async(prompt)
        # The oracle sometimes wraps its prophecy in markdown runes. We must be resilient and strip them away.
        json_str = response.text.strip().removeprefix('```json').removesuffix('```').strip()
        logger.info("The prophecy has been received. Deciphering its meaning...")
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"The oracle's prophecy was not in a recognizable format (Invalid JSON): {json_str[:500]}... Error: {e}")
        return {
            "error": "Prophecy parsing failed: The oracle's words were not in a recognizable format (Invalid JSON).", 
            "details": str(e), 
            "raw_response_snippet": json_str[:500]
        }
    except Exception as e:
        logger.error(f"Failed to receive a prophecy from the cosmic oracle: {e}")
        # This handles API errors, network issues, etc.
        return {
            "error": "Prophecy generation failed: The connection to the oracle was disrupted.", 
            "details": str(e)
        }
--- END OF FILE backend/utils.py ---