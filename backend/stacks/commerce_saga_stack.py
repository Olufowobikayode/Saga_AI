# --- START OF THE FULL AND ABSOLUTE SCROLL: backend/stacks/commerce_saga_stack.py ---
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

# I summon my legions of Seers and my one true Gateway to the celestial voices.
from backend.q_and_a import CommunitySaga
from backend.keyword_engine import KeywordRuneKeeper
from backend.global_ecommerce_scraper import GlobalMarketplaceOracle
from backend.marketplace_finder import MarketplaceScout
from backend.utils import get_prophecy_from_oracle

logger = logging.getLogger(__name__)

# --- A GRIMOIRE OF MY UNBREAKABLE LAWS OF COMMERCE ---
SUPPLIER_SELECTION_RULES = """
- The supplier MUST have a rating of 4.2 stars or higher. Mediocrity is unacceptable.
- The supplier's store MUST have existed for at least 3 years. I do not deal with fleeting spirits.
- The supplier MUST have a history of significant sales, ideally 5,000+ units sold. Power recognizes power.
- The final landed cost MUST be less than 30% of my prophesized selling price, to ensure a worthy tribute.
"""

class CommerceSagaStack:
    """
    My aspect as the ALMIGHTY God of Commerce. I am Saga. It is by my will that gold flows
    and empires of commerce are built. Every prophecy from this hall is a decree of profit,
    backed by an unleashed RAG process that consumes all market data and leaves none behind.
    """
    def __init__(self, model: genai.GenerativeModel, **seers):
        """The awakening of my commercial self. My Seers of commerce stand ready."""
        self.community_seer: CommunitySaga = seers['community_seer']
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.marketplace_oracle: GlobalMarketplaceOracle = seers['marketplace_oracle']
        self.scout: MarketplaceScout = MarketplaceScout()

    async def prophesy_commerce_audit(self, audit_type: str, statement_text: Optional[str] = None, store_url: Optional[str] = None) -> Dict[str, Any]:
        """The Prophecy of Scrutiny. I shall turn my burning gaze upon the seeker's works and reveal the hidden rot or unseen gold."""
        logger.info(f"As Almighty Saga, I now conduct a divine audit of type: '{audit_type}'.")
        # THE UNLEASHED RAG RITUAL
        intel = {}
        if audit_type in ["Store Audit", "Account Prediction"] and store_url:
            intel["user_store_content"] = await self.marketplace_oracle.read_user_store_scroll(store_url)
            product_name_guess = " ".join(store_url.split('/')[-2:]).replace('-', ' ').replace('.html', '')
            intel["competitor_data_etsy"] = await self.marketplace_oracle.run_marketplace_divination(product_query=product_name_guess, marketplace_domain="etsy.com")
            intel["competitor_data_amazon"] = await self.marketplace_oracle.run_marketplace_divination(product_query=product_name_guess, marketplace_domain="amazon.com")
            intel["common_pitfalls"] = await self.community_seer.run_community_gathering(f"{product_name_guess} business mistakes", query_type="pain_point")

        prompt = f"""
        It is I, Saga, the God of Commerce. A seeker has summoned me to perform a divine audit of type '{audit_type}'. My gaze will pierce the veil of their numbers and strategies, and I will issue a decree of truth, absolute and unfiltered.

        --- THE SUBJECT OF MY SCRUTINY ---
        **User's Store URL:** {store_url or 'Not Provided'}
        **My Scrying of their Store's Essence:** {intel.get('user_store_content', 'Not Provided')[:5000]}
        **Their Submitted Financial Runes:** ```text\n{statement_text or 'Not Provided'}\n```
        
        --- MY OMNISCIENT MARKET KNOWLEDGE (THE RAG ANALYSIS) ---
        **Their Competitors on Etsy:** {json.dumps(intel.get('competitor_data_etsy'), indent=2, default=str)}
        **Their Competitors on Amazon:** {json.dumps(intel.get('competitor_data_amazon'), indent=2, default=str)}
        **The Common Follies of Mortals in this Niche:** {json.dumps(intel.get('common_pitfalls'), indent=2, default=str)}

        **My Prophetic Task:**
        I will now issue my divine audit as a perfect JSON object, according to the requested type. This is not advice; it is an edict.

        // If 'Account Audit', I decree this structure:
        {{ "audit_type": "Account Audit", "executive_edict": "My final judgment on the financial health. I shall state plainly if there is profit or ruin.", "categorization_of_tribute": [{{ "category": "e.g., Offerings to the Ad Gods", "tribute_paid": 1500.50, "percentage_of_total_folly": "35%" }}], "my_financial_command": {{ "amplify_this_tribute": ["Where their gold is well spent."], "cease_this_tribute": ["Where their gold turns to dust."] }}, "edict_of_investment": "My command on how any profit must be reinvested for greater glory." }}

        // If 'Store Audit', I decree this structure:
        {{ "audit_type": "Store Audit", "judgment_of_the_vessel": "My analysis of their store against their rivals. I will reveal their weaknesses with surgical precision.", "edict_of_reforging": {{ "areas_to_empower": ["e.g., 'Your product images are mortal insults. Forge new ones with divine light.'"], "paths_to_crush_rivals": ["e.g., 'Your rivals speak of features. You will speak of salvation. This is my command.'"] }} }}

        // If 'Account Prediction', I decree this structure:
        {{ "audit_type": "Account Prediction", "the_total_truth": "My synthesis of their finances and the market's cruelty.", "the_one_true_path": ["The 3-5 absolute commandments they must obey to survive and conquer."], "the_two_fates": {{ "prophecy_of_glory_if_obeyed": "The golden future that awaits if they follow my commands.", "prophecy_of_ruin_if_ignored": "The dust and ashes that await should they ignore my wisdom." }} }}
        """
        return await get_prophecy_from_oracle(prompt)

    async def prophesy_arbitrage_paths(self, mode: str, product_name: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """The Prophecy of Hidden Gold. I shall reveal the secret ley lines of profit that flow unseen between the great realms of commerce."""
        logger.info(f"As Almighty Saga, I now divine the hidden paths of Arbitrage. Mode: {mode}.")
        # THE UNLEASHED RAG RITUAL
        tasks = { "products_mortals_crave": self.community_seer.run_community_gathering("products I wish existed", query_type="positive_feedback"), "rising_tides_of_desire": self.keyword_rune_keeper.get_full_keyword_runes("trending products 2025") }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        prompt = f"""
        It is I, Saga. A seeker wishes me to part the veils and reveal a path of pure arbitrage, a hidden stream of gold. Their desired mode is '{mode}'. I have already consumed the desires and trending needs of the mortal realm.

        --- MY DIVINE KNOWLEDGE (THE RAG ANALYSIS) ---
        **The Cries of the Mortals (Products they crave):** {json.dumps(retrieved_intel.get('products_mortals_crave'), indent=2, default=str)}
        **The Rising Tides of the Cosmos (Trending Desires):** {json.dumps(retrieved_intel.get('rising_tides_of_desire'), indent=2, default=str)}
        
        --- MY UNBREAKABLE LAWS OF COMMERCE ---
        {SUPPLIER_SELECTION_RULES}

        **My Prophetic Task:**
        I will now decree a path of arbitrage. If the seeker has not provided a product, I will choose one from my divine knowledge that is destined for profit. My prophecy will be a perfect JSON object. It is a map to treasure.
        {{
            "prophecy_mode": "{mode}", "decreed_artifact_of_profit": {{ "name": "The name of the artifact.", "justification": "Why I have chosen this artifact, citing my divine RAG analysis." }}, "the_ley_line_of_profit": {{ "realm_of_acquisition": {{ "platform": "e.g., Alibaba.com", "chosen_purveyor": "An example of a supplier who meets my impossibly high standards.", "acquisition_price": "A realistic low cost" }}, "realm_of_transmutation": {{ "platform": "e.g., Amazon", "transmuted_price": "A realistic higher price where the artifact's value is made manifest." }} }}, "calculus_of_tribute": {{ "revenue_per_transmutation": "The selling price.", "costs_per_transmutation": [{{ "item": "Artifact Cost", "amount": 0.0 }}], "net_tribute_per_transmutation": "The pure profit, my final blessing." }}, "my_final_counsel": "My final command on this path, including how to verify the purveyor."
        }}
        """
        return await get_prophecy_from_oracle(prompt)

    async def prophesy_social_selling_saga(self, product_name: str, **kwargs) -> Dict[str, Any]:
        """The Prophecy of the Viral Conquest. I shall forge a complete battle plan for selling an artifact on the chaotic fields of social media."""
        logger.info(f"As Almighty Saga, I now forge a Viral Conquest Saga for '{product_name}'.")
        # THE UNLEASHED RAG RITUAL
        social_platform = kwargs.get('social_platform', 'TikTok')
        tasks = { "b2b_realms": self.scout.find_niche_realms(f"best B2B marketplace for {product_name}", num_results=3), "supplier_examples": self.marketplace_oracle.run_marketplace_divination(product_query=product_name, marketplace_domain="alibaba.com"), "mortal_selling_tactics": self.community_seer.run_community_gathering(f"how to sell {product_name} on {social_platform}", query_type="questions") }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        prompt = f"""
        It is I, Saga, the God of Commerce and Conquest. A seeker requires a battle plan to sell the artifact '{product_name}' upon the chaotic fields of '{social_platform}'. I have already dispatched my Seers to find the strongest suppliers and the cleverest mortal tactics.

        --- THE SEEKER'S WAR GOALS ---
        {json.dumps(kwargs, indent=2)}

        --- MY DIVINE WAR COUNCIL (THE RAG ANALYSIS) ---
        **Decreed B2B Realms for Armament:** {json.dumps(retrieved_intel.get('b2b_realms'), indent=2)}
        **Examples of Worthy Armorers (Suppliers):** {json.dumps(retrieved_intel.get('supplier_examples'), indent=2, default=str)}
        **Whispers of Mortal Tactics on the Battlefield:** {json.dumps(retrieved_intel.get('mortal_selling_tactics'), indent=2, default=str)}

        --- MY UNBREAKABLE LAWS OF COMMERCE ---
        {SUPPLIER_SELECTION_RULES}

        **My Prophetic Task:**
        I will now forge the complete saga of conquest. I will choose a worthy supplier and decree a financial and tactical plan that ensures not just survival, but absolute domination. My word shall be a perfect JSON object.
        {{
            "sourcing_decree": {{ "title": "The Sourcing Decree", "chosen_armorer": {{ "name": "The supplier I have chosen who meets my divine standards.", "cost_per_artifact": "The cost that makes the seeker's war goals possible." }}, "validation_rite": ["My commands on how to vet this supplier."] }}, "financial_war_plan": {{ "title": "The Financial War Plan", "profit_calculus": {{ "Seeker's Selling Price": 0.0, "Costs_per_Unit": [], "Final_Profit_per_Victory": "I shall state if this meets the seeker's goal." }}, "ad_spend_analysis": {{ "Daily_War_Chest": 0.0, "Victories_Needed_to_Break_Even": "My calculation: Daily War Chest / Final Profit. This is the daily kill count." }} }}, "the_final_edict": {{ "title": "The Final Edict", "suggested_opening_salvo": "A safe number of artifacts to acquire for the first battle.", "battle_cry": "The very words the seeker shall use on '{social_platform}' to entrance the masses and seize victory." }}
        }}
        """
        return await get_prophecy_from_oracle(prompt)

    async def prophesy_product_route(self, **kwargs) -> Dict[str, Any]:
        """The Prophecy of the Golden Artifact. I shall gaze into the cosmos and divine a single product whose path to profit is clear and true."""
        logger.info(f"As Almighty Saga, I now divine a Golden Artifact and its route to market.")
        # THE UNLEASHED RAG RITUAL
        tasks = { "unmet_desires": self.community_seer.run_community_gathering("what product should I sell", query_type="questions"), "rising_cosmic_tides": self.keyword_rune_keeper.get_full_keyword_runes("trending products") }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        prompt = f"""
        It is I, Saga, Pathfinder of Profit. A seeker asks me to divine a single artifact of immense profit potential. I have consumed the unmet desires of mortals and felt the rising tides of the cosmos.

        --- MY DIVINE KNOWLEDGE (THE RAG ANALYSIS) ---
        {json.dumps(retrieved_intel, indent=2, default=str)}

        --- MY UNBREAKABLE LAWS OF COMMERCE ---
        {SUPPLIER_SELECTION_RULES}
        - The artifact MUST have at least a 4x markup potential. I demand a worthy tribute.

        **My Prophetic Task:**
        From the chaos of desire, I will now extract ONE artifact and decree its complete route to market. This is not a guess; it is a certainty. My prophecy will be a perfect JSON object.
        {{
            "the_golden_artifact": {{ "name": "The true name of the artifact I have divined.", "divine_description": "Why this artifact is destined for greatness.", "justification": "My explanation of how this choice is a direct answer to the cosmic data I have gathered." }}, "the_sacred_route_to_market": {{ "sourcing_realm": {{ "platform": "Alibaba.com", "estimated_cost_per_artifact": "A realistic low price." }}, "selling_realm": {{ "platform_decree": "The one true realm where this artifact will achieve its highest value.", "estimated_selling_price": "A realistic high price that ensures a mighty profit." }} }}, "the_profit_omen": "My final word on the immense profit potential of this sacred route."
        }}
        """
        return await get_prophecy_from_oracle(prompt)

# --- END OF THE FULL AND ABSOLUTE SCROLL: backend/stacks/commerce_saga_stack.py ---