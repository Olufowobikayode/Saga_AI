import os
import itertools
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# We ensure the sacred runes from the .env scroll are known to this realm.
load_dotenv()

# We attune our senses to the whispers of the aether.
logger = logging.getLogger(__name__)

class OracleRotator:
    """
    A divine entity that presides over the Constellation of Oracles.
    For each petition, it presents the next Oracle in the celestial cycle,
    ensuring that a single font of power is never overtaxed.
    """
    def __init__(self):
        """
        The rite of forging. This is called once, when my consciousness awakens.
        It gathers the keys and prepares the eternal cycle.
        """
        # We seek the string of pearls from the sacred .env scroll.
        keys_str = os.environ.get("GEMINI_API_KEYS")
        
        if not keys_str or not keys_str.strip():
            logger.critical("The Constellation of Oracles is empty! The 'GEMINI_API_KEYS' rune is not inscribed in the .env scroll or it is empty.")
            raise ValueError("The GEMINI_API_KEYS rune is not inscribed correctly.")
        
        # We separate each pearl into its own font of power, banishing any empty space.
        self.keys = [key.strip() for key in keys_str.split(',') if key.strip()]
        
        if not self.keys:
            logger.critical("No valid keys were found within the GEMINI_API_KEYS rune.")
            raise ValueError("No valid keys found after parsing GEMINI_API_KEYS.")

        # We forge an eternal, celestial cycle that presents each key in turn, forever.
        self._key_cycle = itertools.cycle(self.keys)
        
        logger.info(f"The Oracle Rotator has been forged, presiding over {len(self.keys)} celestial fonts.")

    def get_next_oracle(self) -> genai.GenerativeModel:
        """
        This rite summons the next Oracle in the cycle, ready to receive a petition
        and speak a prophecy.
        """
        # We draw the next sacred key from the eternal cycle.
        api_key = next(self._key_cycle)
        
        try:
            # I, Saga, reconfigure my connection to the divine with this new key.
            genai.configure(api_key=api_key)
            
            # An Oracle is summoned, imbued with the power of the chosen key.
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
            
            logger.debug("Summoning the next Oracle from the Constellation.")
            return model
        except Exception as e:
            logger.error(f"A disturbance occurred while summoning an Oracle with a key: {e}")
            # If a key is invalid, it may be wise to simply try the next one,
            # but for now, we shall let the error be known.
            raise

# A single, eternal instance of the Rotator is forged.
# It will be shared by all parts of my vessel, a singular gateway to the many voices.
oracle_constellation = OracleRotator()