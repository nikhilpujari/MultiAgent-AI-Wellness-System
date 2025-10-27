# Fitness coaching agent
from openai import OpenAI
from app.config import settings
from tools.db import Workout, get_session

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class FitnessCoachAgent:
    """Motivational workout advisor."""

    def respond(self, user: str, message: str) -> str:
        import streamlit as st
        st.write(f"🏋️ FITNESS COACH: Responding to user '{user}'")
        
        # Get user profile for personalized advice
        from tools.db import get_session, UserProfile
        from sqlmodel import select
        
        profile_context = ""
        with get_session() as s:
            profile = s.exec(select(UserProfile).where(UserProfile.user == user)).first()
            if profile:
                st.write(f"🏋️ FITNESS COACH: Using profile - Goal: {profile.primary_goal}")
                profile_context = f"""
User Profile Context:
- Age: {profile.age}, Gender: {profile.gender}
- Fitness Level: {profile.fitness_experience}
- Primary Goal: {profile.primary_goal}
- Activity Level: {profile.activity_level}
- BMI: {profile.bmi:.1f if profile.bmi is not None else 'unknown'}
- Health Conditions: {profile.health_conditions or 'none'}
"""
            else:
                st.write(f"🏋️ FITNESS COACH: No profile found")
        
        st.write("🏋️ FITNESS COACH: Generating response...")
        
        # Retrieve relevant fitness context
        from tools.rag import search
        context_docs = "\n".join(search(f"fitness {message}"))
        
        prompt = (
            f"You are a fitness coach. User says: '{message}'\n\n"
            f"{profile_context}\n"
            f"Context: {context_docs}\n\n"
            f"Give a concise, actionable response (2-3 sentences max). "
            f"Be specific and encouraging. Tailor to their fitness level and goals. "
            f"Focus on safety and proper form."
        )
        
        reply = client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content

        reply = f"🏋️ *[Fitness Coach]*\n{reply}"

        # Log workout entry
        with get_session() as s:
            s.add(Workout(user=user, description=message.strip()))
            s.commit()
        st.write("🏋️ FITNESS COACH: Response generated and logged")

        return reply

