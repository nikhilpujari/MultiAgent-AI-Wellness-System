# Nutrition specialist agent
from openai import OpenAI
from app.config import settings
from tools.db import Meal, get_session

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class NutritionAgent:
    """Logs meals and provides nutrition guidance."""

    def respond(self, user: str, message: str) -> str:
        # Get user profile for personalized advice
        from tools.db import get_session, UserProfile
        from sqlmodel import select
        
        profile_context = ""
        with get_session() as s:
            profile = s.exec(select(UserProfile).where(UserProfile.user == user)).first()
            if profile:
                profile_context = f"""
User Profile Context:
- Age: {profile.age}, Gender: {profile.gender}
- Weight: {profile.weight_kg}kg, Height: {profile.height_cm}cm
- Primary Goal: {profile.primary_goal}
- Activity Level: {profile.activity_level}
- Daily Calorie Goal: {profile.daily_calorie_goal}
- Allergies: {profile.allergies or 'none'}
- Health Conditions: {profile.health_conditions or 'none'}
"""
        
        # Retrieve relevant nutrition context
        from tools.rag import search
        context_docs = "\n".join(search(f"nutrition {message}"))
        
        prompt = (
            f"You are a nutrition coach. User says: '{message}'\n\n"
            f"{profile_context}\n"
            f"Context: {context_docs}\n\n"
            f"Give a concise, helpful response (2-3 sentences max). "
            f"Consider their calorie goals and dietary restrictions. "
            f"Be specific and actionable."
        )
        
        reply = client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content

        reply = f"🍎 *[Nutrition Coach]*\n{reply}"

        with get_session() as s:
            s.add(Meal(user=user, description=message.strip()))
            s.commit()

        return reply

