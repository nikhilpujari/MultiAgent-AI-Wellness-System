# API Tool Agent for external food database lookups
import requests
import json
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class APIToolAgent:
    """Agent that handles external API calls for food database lookups"""
    
    def __init__(self):
        # Using USDA FoodData Central API (free, no key required for basic usage)
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
        # For demo purposes, we'll use a mock response since we don't have API key
        self.use_mock = True
    
    def lookup_food(self, food_query: str) -> dict:
        """
        Look up food information from external database
        Returns structured food data with calories and macros
        """
        import streamlit as st
        st.write(f"🔍 API TOOL: Looking up food data for '{food_query}'")
        
        if self.use_mock:
            return self._mock_food_lookup(food_query)
        else:
            return self._real_food_lookup(food_query)
    
    def _mock_food_lookup(self, food_query: str) -> dict:
        """Mock food database lookup using LLM to simulate API response"""
        
        prompt = f"""
        You are a food database API. Return realistic nutrition data for: "{food_query}"
        
        Respond with this exact JSON format:
        {{
            "food_name": "standardized food name",
            "serving_size": "1 medium apple, 2 slices, etc.",
            "calories_per_serving": <number>,
            "protein_g": <number>,
            "carbs_g": <number>,
            "fat_g": <number>,
            "fiber_g": <number>,
            "source": "USDA Food Database"
        }}
        
        Use realistic nutrition values. For example:
        - 1 medium apple: 95 calories, 0.5g protein, 25g carbs, 0.3g fat, 4g fiber
        - 2 pizza slices: 570 calories, 24g protein, 72g carbs, 20g fat, 4g fiber
        """
        
        try:
            response = client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group()
            
            food_data = json.loads(result_text)
            
            import streamlit as st
            st.write(f"✅ API TOOL: Found data for {food_data.get('food_name', 'unknown food')}")
            
            return food_data
            
        except Exception as e:
            import streamlit as st
            st.write(f"❌ API TOOL: Lookup failed: {e}")
            
            # Return default data if lookup fails
            return {
                "food_name": food_query,
                "serving_size": "1 serving",
                "calories_per_serving": 0,
                "protein_g": 0,
                "carbs_g": 0,
                "fat_g": 0,
                "fiber_g": 0,
                "source": "Fallback data"
            }
    
    def _real_food_lookup(self, food_query: str) -> dict:
        """Real API lookup (requires API key)"""
        # This would implement actual USDA FoodData Central API calls
        # For now, falls back to mock
        return self._mock_food_lookup(food_query)
    
    def extract_food_items(self, message: str) -> str:
        """Extract food items from user message for API lookup"""
        
        prompt = f"""
        Extract the food items from this message for database lookup: "{message}"
        
        Return just the food items in a simple format, like:
        - "2 slices pizza"
        - "1 medium apple"
        - "chicken breast 6oz"
        
        If multiple items, separate with commas.
        """
        
        try:
            response = client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback: return original message
            return message
    
    def needs_food_lookup(self, message: str) -> bool:
        """Determine if message needs food database lookup"""
        
        # Keywords that suggest need for precise nutrition data
        lookup_keywords = [
            "how many calories", "calories in", "nutrition facts",
            "macros", "protein in", "carbs in", "fat in",
            "nutritional value", "nutrition info"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in lookup_keywords)