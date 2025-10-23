# General agent for out-of-domain queries
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class GeneralAgent:
    """Handles queries outside fitness, nutrition, and health domains."""

    def respond(self, message: str) -> str:
        # First, analyze if this might actually belong to one of our domains
        analysis_prompt = (
            f"Analyze this user message: '{message}'\n\n"
            "Could this message be related to:\n"
            "- FITNESS (workouts, exercise, physical activity, sports, training)\n"
            "- NUTRITION (food, meals, eating, diet, calories, hunger)\n" 
            "- HEALTH (medical concerns, symptoms, mental health, anxiety, stress, sleep)\n\n"
            "If YES, respond with just the domain name (FITNESS, NUTRITION, or HEALTH).\n"
            "If NO, respond with 'OUT_OF_DOMAIN'."
        )
        
        analysis = client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[{"role": "user", "content": analysis_prompt}]
        ).choices[0].message.content.strip()

        if analysis in ["FITNESS", "NUTRITION", "HEALTH"]:
            domain_map = {
                "FITNESS": "🏋️ fitness",
                "NUTRITION": "🍎 nutrition", 
                "HEALTH": "🩺 health"
            }
            reply = (
                f"I think your question might actually be related to {domain_map[analysis]}! "
                f"Let me redirect you to the right specialist for better help with: '{message}'"
            )
            # Note: In a real implementation, you'd want to re-route here
            # For now, we'll just suggest the correct domain
        else:
            reply = (
                f"I'm specialized in fitness 🏋️, nutrition 🍎, and health 🩺 topics. "
                f"Your question about '{message}' seems to be outside these areas. "
                f"Could you ask me something related to workouts, meals, or health instead? "
                f"I'd be happy to help with those topics!"
            )
        
        return f"🤖 *[Domain Helper]*\n{reply}"