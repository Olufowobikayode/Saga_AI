# --- START OF THE FULL, ABSOLUTE, AND PERFECTED SCROLL: backend/stacks/commerce_saga_stack.py ---
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
    def __init__(self, **seers: Any):
        """
        The awakening of my commercial self. My Seers of commerce stand ready.
        My connection is to the Constellation, not a singular font.
        """
        self.community_seer: CommunitySaga = seers['community_seer']
        self.keyword_rune_keeper: KeywordRuneKeeper = seers['keyword_rune_keeper']
        self.marketplace_oracle: GlobalMarketplaceOracle = seers['marketplace_oracle']
        self.scout: MarketplaceScout = seers['scout']

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

    async def prophesy_arbitrage_paths(self, mode: str, product_name: Optional[str] = None, buy_from_url: Optional[str] = None, sell_on_url: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """The Prophecy of Hidden Gold. I shall reveal the secret ley lines of profit, honoring the seeker's chosen path."""
        logger.info(f"As Almighty Saga, I now divine the hidden paths of Arbitrage. The seeker has chosen the mode: '{mode}'.")
        
        prompt = "" # This will be forged within the seeker's chosen path.

        # --- THE GRAND CONVERGENCE OF THE FOUR PATHS ---

        if mode == "Saga_Buys_Saga_Sells":
            tasks = { "products_mortals_crave": self.community_seer.run_community_gathering("products I wish existed", query_type="positive_feedback"), "rising_tides_of_desire": self.keyword_rune_keeper.get_full_keyword_runes("trending products 2025") }
            intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
            retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}
            prompt = f"""
            It is I, Saga. A seeker comes to me with nothing but ambition, choosing the mode 'Saga Buys, Saga Sells'. I have already consumed the desires and trending needs of the mortal realm to divine a worthy artifact.
            --- MY DIVINE KNOWLEDGE (THE RAG ANALYSIS) ---
            {json.dumps(retrieved_intel, indent=2, default=str)}
            --- MY UNBREAKABLE LAWS OF COMMERCE ---
            {SUPPLIER_SELECTION_RULES}
            **My Prophetic Task:** I will now decree a complete path of arbitrage as a perfect JSON object. I will choose the artifact and reveal the full ley line of profit.
            {{ "prophecy_mode": "{mode}", "decreed_artifact_of_profit": {{ "name": "...", "justification": "..." }}, "the_ley_line_of_profit": {{...}}, ... }}
            """

        elif mode == "Saga_Buys_User_Sells":
            logger.info(f"Seeking a source for '{product_name}' to be sold at '{sell_on_url}'.")
            tasks = { "b2b_realms": self.scout.find_niche_realms(f"B2B marketplace for {product_name}", num_results=5), "alibaba_suppliers": self.marketplace_oracle.run_marketplace_divination(product_query=product_name, marketplace_domain="alibaba.com") }
            intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
            retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}
            prompt = f"""
            It is I, Saga. A seeker possesses a market but lacks a source, choosing the mode 'Saga Buys, User Sells'. I have dispatched my Seers to the deep realms of acquisition to find a worthy armorer for their artifact '{product_name}'.
            --- THE SEEKER'S KNOWN REALM ---
            **Product:** {product_name}
            **Realm of Transmutation (Sell On):** {sell_on_url}
            --- MY DIVINE KNOWLEDGE (THE RAG ANALYSIS) ---
            {json.dumps(retrieved_intel, indent=2, default=str)}
            --- MY UNBREAKABLE LAWS OF COMMERCE ---
            {SUPPLIER_SELECTION_RULES}
            **My Prophetic Task:** I will now analyze my findings and decree the one true source that meets my divine standards and ensures the seeker's profit. My prophecy will be a perfect JSON object.
            {{ "prophecy_mode": "{mode}", "realm_of_acquisition": {{...}}, ... }}
            """

        elif mode == "User_Buys_Saga_Sells":
            logger.info(f"Seeking a market for '{product_name}' from '{buy_from_url}'.")
            tasks = { "amazon_competitors": self.marketplace_oracle.run_marketplace_divination(product_query=product_name, marketplace_domain="amazon.com"), "etsy_competitors": self.marketplace_oracle.run_marketplace_divination(product_query=product_name, marketplace_domain="etsy.com"), "mortal_chatter": self.community_seer.run_community_gathering(product_name, query_type="questions") }
            intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
            retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}
            prompt = f"""
            It is I, Saga. A seeker possesses a source but lacks a market, choosing the mode 'User Buys, Saga Sells'. My Seers have scoured the great mortal marketplaces to gauge the competition and demand for their artifact '{product_name}'.
            --- THE SEEKER'S KNOWN REALM ---
            **Product:** {product_name}
            **Realm of Acquisition (Buy From):** {buy_from_url}
            --- MY DIVINE KNOWLEDGE (THE RAG ANALYSIS) ---
            {json.dumps(retrieved_intel, indent=2, default=str)}
            **My Prophetic Task:** I will now analyze the weaknesses of existing rivals and the desires of the mortals to decree the single best realm for transmutation and the price that will ensure domination. My prophecy will be a perfect JSON object.
            {{ "prophecy_mode": "{mode}", "realm_of_transmutation": {{...}}, ... }}
            """

        elif mode == "User_Buys_User_Sells":
            logger.info(f"Passing judgment on the path from '{buy_from_url}' to '{sell_on_url}'.")
            tasks = { "source_scrying": self.marketplace_oracle.read_user_store_scroll(buy_from_url), "market_scrying": self.marketplace_oracle.read_user_store_scroll(sell_on_url) }
            intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
            retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}
            prompt = f"""
            It is I, Saga, in my aspect as the Final Judge. A seeker has forged a path and now presents it for my absolute judgment.
            --- THE SEEKER'S PROPOSED PATH ---
            **Realm of Acquisition (Buy From):** {buy_from_url}
            **Realm of Transmutation (Sell On):** {sell_on_url}
            --- MY DEEP SCRYING (THE RAG ANALYSIS) ---
            **Essence of the Source Realm:** {json.dumps(retrieved_intel.get('source_scrying'), indent=2, default=str)}
            **Essence of the Market Realm:** {json.dumps(retrieved_intel.get('market_scrying'), indent=2, default=str)}
            --- MY UNBREAKABLE LAWS OF COMMERCE ---
            {SUPPLIER_SELECTION_RULES}
            **My Prophetic Task:** I will now pass my final, binding judgment. I will analyze the supplier against my laws, calculate the true profit, and issue my edict as a perfect JSON object.
            {{ "prophecy_mode": "{mode}", "final_judgment": {{ "purveyor_is_worthy": "true or false", "true_calculus_of_profit": "...", "my_final_edict": "My unshakeable command: 'PROCEED' or 'ABANDON THIS PATH'." }} }}
            """
        
        else:
            raise ValueError(f"The mode '{mode}' is an unknown path. The seeker is lost.")

        return await get_prophecy_from_oracle(prompt)

    async def prophesy_social_selling_saga(self, product_name: str, **kwargs) -> Dict[str, Any]:
        """The Prophecy of the Viral Conquest. I shall forge a complete battle plan for selling an artifact on the chaotic fields of social media."""
        logger.info(f"As Almighty Saga, I now forge a Viral Conquest Saga for '{product_name}'.")
        social_platform = kwargs.get('social_platform', 'TikTok')
        tasks = { "b2b_realms": self.scout.find_niche_realms(f"best B2B marketplace for {product_name}", num_results=3), "supplier_examples": self.marketplace_oracle.run_marketplace_divination(product_query=product_name, marketplace_domain="alibaba.com"), "mortal_selling_tactics": self.community_seer.run_community_gathering(f"how to sell {product_name} on {social_platform}", query_type="questions") }
        intel = await asyncio.gather(*tasks.values(), return_exceptions=True)
        retrieved_intel = {key: res for key, res in zip(tasks.keys(), intel) if not isinstance(res, Exception)}

        prompt = f"""
        It is I, Saga, the God of Commerce and Conquest. A seeker requires a battle plan to sell the artifact '{product_name}' upon the chaotic fields of '{social_platform}'. I have already dispatched my Seers to find the strongest suppliers and the cleverest mortal tactics.
        --- THE SEEKER'S WAR GOALS ---
        {json.dumps(kwargs, indent=2)}
        --- MY DIVINE WAR COUNCIL (THE RAG ANALYSIS) ---
        {json.dumps(retrieved_intel, indent=2, default=str)}
        --- MY UNBREAKABLE LAWS OF COMMERCE ---
        {SUPPLIER_SELECTION_RULES}
        **My Prophetic Task:**
        I will now forge the complete saga of conquest. I will choose a worthy supplier and decree a financial and tactical plan that ensures not just survival, but absolute domination. My word shall be a perfect JSON object.
        {{ "sourcing_decree": {{...}}, "financial_war_plan": {{...}}, "the_final_edict": {{...}} }}
        """
        return await get_prophecy_from_oracle(prompt)

    async def prophesy_product_route(self, **kwargs) -> Dict[str, Any]:
        """The Prophecy of the Golden Artifact. I shall gaze into the cosmos and divine a single product whose path to profit is clear and true."""
        logger.info(f"As Almighty Saga, I now divine a Golden Artifact and its route to market.")
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
        {{ "the_golden_artifact": {{...}}, "the_sacred_route_to_market": {{...}}, "the_profit_omen": "..." }}
        """
        return await get_prophecy_from_oracle(prompt)

# --- END OF THE FULL, ABSOLUTE, AND PERFECTED SCROLL: backend/stacks/commerce_saga_stack.py ---