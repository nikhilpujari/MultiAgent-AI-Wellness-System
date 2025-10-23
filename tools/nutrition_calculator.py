# Nutrition calculator using LLM to estimate calories and macros
from openai import OpenAI
from app.config import settings
import json
import re

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class NutritionCalculator:
    """Calculates calories and macros for food items using LLM"""
    
    def calculate_nutrition(self, food_items: str) -> dict:
        """
        Calculate nutrition for a list of food items
        Returns: {calories, protein_g, carbs_g, fat_g, fiber_g}
        """
        prompt = f"""
        You are a nutrition expert. Calculate the approximate nutrition values for these food items:
        
        Food items: {food_items}
        
        Assume average serving sizes for each item. Provide your response in this exact JSON format:
        {{
            "total_calories": <number>,
            "protein_g": <number>,
            "carbs_g": <number>,
            "fat_g": <number>,
            "fiber_g": <number>,
            "breakdown": [
                {{"item": "food name", "calories": <number>, "protein": <number>, "carbs": <number>, "fat": <number>}}
            ]
        }}
        
        Be realistic with portions. For example:
        - 1 medium apple = ~80 calories
        - 1 cup oatmeal = ~150 calories  
        - 1 chicken breast (6oz) = ~280 calories
        - 1 cup rice = ~200 calories
        
        Only respond with the JSON, no other text.
        """
        
        try:
            response = client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group()
            
            nutrition_data = json.loads(result_text)
            
            return {
                "total_calories": float(nutrition_data.get("total_calories", 0)),
                "protein_g": float(nutrition_data.get("protein_g", 0)),
                "carbs_g": float(nutrition_data.get("carbs_g", 0)),
                "fat_g": float(nutrition_data.get("fat_g", 0)),
                "fiber_g": float(nutrition_data.get("fiber_g", 0)),
                "breakdown": nutrition_data.get("breakdown", [])
            }
            
        except Exception as e:
            print(f"Nutrition calculation error: {e}")
            # Return default values if calculation fails
            return {
                "total_calories": 0,
                "protein_g": 0,
                "carbs_g": 0,
                "fat_g": 0,
                "fiber_g": 0,
                "breakdown": []
            }

nutrition_calculator = NutritionCalculator()