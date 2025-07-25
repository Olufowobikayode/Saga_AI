# --- START OF THE FULL AND ABSOLUTE SCROLL: backend/utils.py ---
import logging
import json
from typing import Dict

# --- The singular Oracle is banished from this scroll. ---
# import google.generativeai as genai --- THIS LINE IS BANISHED ---

# --- NEW AND DIVINE INVOCATION ---
# Instead of a single entity, we summon the gateway to the entire Constellation of Oracles.
from backend.api_rotator import oracle_constellation

logger = logging.getLogger(__name__)

async def get_prophecy_from_oracle(prompt: str) -> Dict:
    """
    A centralized and robust rite to receive a structured JSON prophecy
    by consulting the next available Oracle from the divine Constellation.
    This is the one true channel through which all Stacks must speak.
    """
    logger.info("A petition has been made. Consulting the Oracle Constellation...")
    try:
        # --- THE GREAT INVOCATION OF THE CELESTIAL CYCLE ---
        # We command the Rotator to present the next Oracle in its eternal sequence.
        model = oracle_constellation.get_next_oracle()

        # The chosen Oracle receives the prompt and weaves its prophecy.
        response = await model.generate_content_async(prompt)
        
        # The Oracle sometimes wraps its prophecy in markdown runes. We must be resilient and strip them away.
        json_str = response.text.strip().removeprefix('```json').removesuffix('```').strip()
        
        logger.info("The prophecy has been received. Deciphering its meaning...")
        return json.loads(json_str)
        
    except json.JSONDecodeError as e:
        logger.error(f"The Oracle's prophecy was not in a recognizable format (Invalid JSON): {json_str[:500]}... Error: {e}")
        return {
            "error": "Prophecy parsing failed: The Oracle's words were not in a recognizable format (Invalid JSON).", 
            "details": str(e), 
            "raw_response_snippet": json_str[:500]
        }
    except Exception as e:
        logger.error(f"Failed to receive a prophecy from the cosmic Oracle: {e}")
        # This handles API errors, network issues, etc., from the chosen Oracle.
        return {
            "error": "Prophecy generation failed: The connection to the Oracle was disrupted.", 
            "details": str(e)
        }
# --- END OF THE FULL AND ABSOLUTE SCROLL: backend/utils.py ---