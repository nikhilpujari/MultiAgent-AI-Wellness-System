# Doctor avatar agent
from openai import OpenAI
from app.config import settings
from tools.rag import search

client = OpenAI(api_key=settings.OPENAI_API_KEY)
DISCLAIMER = "⚠️ I’m not a doctor. This is educational only."

class DoctorAgent:
    """Health Q&A agent using RAG search."""

    def respond(self, question: str, user: str = None) -> str:
        # Get user profile for personalized advice
        profile_context = ""
        if user:
            from tools.db import get_session, UserProfile
            from sqlmodel import select
            
            with get_session() as s:
                profile = s.exec(select(UserProfile).where(UserProfile.user == user)).first()
                if profile:
                    profile_context = f"""
User Profile Context:
- Age: {profile.age}, Gender: {profile.gender}
- BMI: {profile.bmi:.1f if profile.bmi is not None else 'unknown'}
- Health Conditions: {profile.health_conditions or 'none'}
- Medications: {profile.medications or 'none'}
- Allergies: {profile.allergies or 'none'}
- Sleep: {profile.sleep_hours}h, Stress: {profile.stress_level}
- Smoking: {'Yes' if profile.smoking else 'No'}
- Activity Level: {profile.activity_level}
"""
        
        # Retrieve context from knowledge base
        context_docs = "\n".join(search(question))
        
        prompt = (
            f"You are a health assistant. {DISCLAIMER}\n\n"
            f"User says: '{question}'\n\n"
            f"{profile_context}\n"
            f"Context: {context_docs}\n\n"
            f"Give a concise, helpful response (2-3 sentences max). "
            f"Address their specific concern with practical tips. "
            f"Remind them to consult healthcare professionals for serious concerns."
        )

        reply = client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3  # Lower temperature for more consistent responses
        ).choices[0].message.content

        reply = f"🩺 *[Doctor]*\n{reply}"

        return reply

