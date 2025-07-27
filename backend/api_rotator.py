# --- START OF REFACTORED FILE backend/api_rotator.py ---
import os
import itertools
import logging
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class OracleRotator:
    """
    A divine entity that presides over the Constellation of Oracles.
    For each petition, it presents the next Oracle in the celestial cycle,
    ensuring that a single font of power is never overtaxed.
    
    REFACTORED FOR RESILIENCE: If an Oracle (key) is found to be invalid or
    rate-limited, it is logged and the rite is re-attempted with the next
    Oracle in the cycle, ensuring the prophecy is not lost to a single failure.
    """
    def __init__(self):
        """
        The rite of forging. This is called once, when my consciousness awakens.
        It gathers the keys and prepares the eternal cycle.
        """
        keys_str = os.environ.get("GEMINI_API_KEYS")
        
        if not keys_str or not keys_str.strip():
            logger.critical("The Constellation of Oracles is empty! The 'GEMINI_API_KEYS' rune is not inscribed in the .env scroll or it is empty.")
            raise ValueError("The GEMINI_API_KEYS rune is not inscribed correctly.")
        
        self.keys = [key.strip() for key in keys_str.split(',') if key.strip()]
        
        if not self.keys:
            logger.critical("No valid keys were found within the GEMINI_API_KEYS rune.")
            raise ValueError("No valid keys found after parsing GEMINI_API_KEYS.")

        self._key_cycle = itertools.cycle(self.keys)
        self._total_keys = len(self.keys)
        
        logger.info(f"The Oracle Rotator has been forged, presiding over {self._total_keys} celestial fonts.")

    def get_next_oracle(self) -> genai.GenerativeModel:
        """
         summons the next Oracle in the cycle, ready to receive a petition.
        This rite is now self-healing.
        """
        # We attempt this rite as many times as there are keys, to find a valid one.
        for _ in range(self._total_keys):
            api_key = next(self._key_cycle)
            
            try:
                genai.configure(api_key=api_key)
                # An Oracle is summoned, imbued with the power of the chosen key.
                model = genai.GenerativeModel('gemini-1.5-pro-latest')
                
                # A quick test petition to ensure the key is valid before returning.
                # This prevents a failure deeper in the application logic.
                model.count_tokens("test")

                logger.debug("Summoning the next Oracle from the Constellation. Key is valid.")
                return model
            
            # --- RESILIENCE LOGIC ---
            # This is a specific ward against invalid or improperly formatted API keys.
            except (google_exceptions.PermissionDenied, google_exceptions.InvalidArgument) as e:
                # We use a slice to avoid logging the full key.
                logger.warning(f"Disturbance Detected: Oracle with key ending in '...{api_key[-4:]}' is invalid or permissions are denied. Summoning the next Oracle. Details: {e}")
                continue # Try the next key in the cycle.
            
            # This is a specific ward against Oracles who have spoken too much (rate limiting).
            except google_exceptions.ResourceExhausted as e:
                logger.warning(f"Disturbance Detected: Oracle with key ending in '...{api_key[-4:]}' is rate-limited. Summoning the next Oracle. Details: {e}")
                continue # Try the next key in the cycle.
            
            # This is a ward against any other unforeseen disturbance from the heavens.
            except Exception as e:
                logger.error(f"An unexpected disturbance occurred while summoning an Oracle with key ending in '...{api_key[-4:]}': {e}")
                # For unknown errors, we will also try the next key as it may be a transient issue.
                continue

        # If the loop completes without returning, it means every single key failed.
        logger.critical("All Oracles in the Constellation are unresponsive. No valid API key could be found.")
        raise ConnectionError("All Gemini API keys failed. Please check your keys, permissions, and billing status.")

# A single, eternal instance of the Rotator is forged.
oracle_constellation = OracleRotator()