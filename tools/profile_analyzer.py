# Profile analyzer for BMI, body age, and goal setting
from openai import OpenAI
from app.config import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class ProfileAnalyzer:
    """Analyzes user profile to calculate BMI, body age, and set goals"""
    
    def calculate_bmi(self, weight_kg: float, height_cm: float) -> float:
        """Calculate BMI"""
        height_m = height_cm / 100
        return weight_kg / (height_m ** 2)
    
    def get_bmi_category(self, bmi: float) -> str:
        """Get BMI category"""
        if bmi < 18.5:
            return "Underweight"
        elif bmi < 25:
            return "Normal weight"
        elif bmi < 30:
            return "Overweight"
        else:
            return "Obese"
    
    def estimate_body_age(self, profile_data: dict) -> dict:
        """Estimate body age using AI analysis"""
        prompt = f"""
        You are a health expert. Based on this user profile, estimate their biological/body age and provide health insights.
        
        Profile:
        - Age: {profile_data.get('age')} years
        - BMI: {profile_data.get('bmi', 0):.1f}
        - Activity Level: {profile_data.get('activity_level', 'unknown')}
        - Sleep Hours: {profile_data.get('sleep_hours', 'unknown')} per night
        - Stress Level: {profile_data.get('stress_level', 'unknown')}
        - Smoking: {profile_data.get('smoking', 'unknown')}
        - Alcohol: {profile_data.get('alcohol_frequency', 'unknown')}
        - Health Conditions: {profile_data.get('health_conditions', 'none')}
        
        Provide response in this exact JSON format:
        {{
            "body_age": <estimated_age_number>,
            "age_difference": <body_age_minus_chronological_age>,
            "health_score": <score_out_of_100>,
            "key_factors": ["factor1", "factor2", "factor3"],
            "recommendations": ["recommendation1", "recommendation2", "recommendation3"]
        }}
        
        Consider factors like:
        - BMI (normal range is healthier)
        - Activity level (more active = younger body age)
        - Sleep quality (7-9 hours ideal)
        - Stress levels (high stress ages body)
        - Smoking (significantly ages body)
        - Alcohol consumption
        - Existing health conditions
        
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
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result_text = json_match.group()
            
            analysis = json.loads(result_text)
            
            return {
                "body_age": int(analysis.get("body_age", profile_data.get('age', 30))),
                "age_difference": int(analysis.get("age_difference", 0)),
                "health_score": int(analysis.get("health_score", 70)),
                "key_factors": analysis.get("key_factors", []),
                "recommendations": analysis.get("recommendations", [])
            }
            
        except Exception as e:
            print(f"Body age estimation error: {e}")
            # Return default values if calculation fails
            return {
                "body_age": profile_data.get('age', 30),
                "age_difference": 0,
                "health_score": 70,
                "key_factors": ["Unable to analyze"],
                "recommendations": ["Complete your profile for better analysis"]
            }
    
    def calculate_daily_calories(self, profile_data: dict) -> int:
        """Calculate daily calorie needs using Mifflin-St Jeor equation"""
        try:
            age = profile_data.get('age', 30)
            weight = profile_data.get('weight_kg', 70)
            height = profile_data.get('height_cm', 170)
            gender = profile_data.get('gender', 'male')
            activity_level = profile_data.get('activity_level', 'moderately_active')
            goal = profile_data.get('primary_goal', 'maintenance')
            
            # Base Metabolic Rate (BMR)
            if gender.lower() == 'male':
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161
            
            # Activity multipliers
            activity_multipliers = {
                'sedentary': 1.2,
                'lightly_active': 1.375,
                'moderately_active': 1.55,
                'very_active': 1.725,
                'extremely_active': 1.9
            }
            
            multiplier = activity_multipliers.get(activity_level, 1.55)
            maintenance_calories = bmr * multiplier
            
            # Adjust for goals
            if goal == 'weight_loss':
                return int(maintenance_calories - 500)  # 1 lb per week loss
            elif goal == 'muscle_gain':
                return int(maintenance_calories + 300)  # Moderate surplus
            else:
                return int(maintenance_calories)
                
        except Exception as e:
            print(f"Calorie calculation error: {e}")
            return 2000  # Default value

profile_analyzer = ProfileAnalyzer()