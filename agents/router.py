# Agent router for directing user queries
from typing import Literal

class RouterAgent:
    """Classifies user input and routes it to the correct agent."""

    def classify(self, text: str) -> Literal["fitness", "nutrition", "health", "misc"]:
        from openai import OpenAI
        from app.config import settings
        
        import streamlit as st
        st.write(f"🔍 ROUTER: Classifying message: '{text}'")
        
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        classification_prompt = (
            f"Classify this user message into one of these categories:\n\n"
            f"User message: '{text}'\n\n"
            f"Categories:\n"
            f"- FITNESS: Exercise, workouts, physical activity, sports, training, gym, running, strength, cardio, muscle building\n"
            f"- NUTRITION: Food, meals, eating, diet, calories, hunger, snacks, cooking, meal planning, supplements\n"
            f"- HEALTH: Medical concerns, symptoms, pain, illness, mental health, anxiety, stress, sleep issues, headaches, body aches\n"
            f"- MISC: Everything else not related to fitness, nutrition, or health\n\n"
            f"Respond with ONLY one word: fitness, nutrition, health, or misc"
        )
        
        try:
            st.write("🤖 ROUTER: Using LLM for classification...")
            response = client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=[{"role": "user", "content": classification_prompt}],
                temperature=0.1  # Low temperature for consistent classification
            )
            
            classification = response.choices[0].message.content.strip().lower()
            st.write(f"✅ ROUTER: LLM classified as: '{classification}'")
            
            # Validate the response
            if classification in ["fitness", "nutrition", "health", "misc"]:
                st.write(f"🎯 ROUTER: Final classification: '{classification}'")
                return classification
            else:
                # Fallback to keyword matching if LLM gives unexpected response
                st.write(f"⚠️ ROUTER: Invalid LLM response '{classification}', falling back to keywords")
                return self._fallback_classify(text)
                
        except Exception as e:
            # Fallback to keyword matching if API fails
            st.write(f"❌ ROUTER: LLM classification failed: {e}")
            st.write("🔄 ROUTER: Falling back to keyword matching")
            return self._fallback_classify(text)
    
    def _fallback_classify(self, text: str) -> Literal["fitness", "nutrition", "health", "misc"]:
        """Fallback keyword-based classification"""
        import streamlit as st
        st.write("🔤 ROUTER: Using keyword-based fallback classification")
        import re
        t = text.lower()
        
        def has_word(text, words):
            for word in words:
                if word in text or re.search(r'\b' + re.escape(word) + r'\b', text):
                    return True
            return False
        
        fitness_keywords = ["workout", "working out", "exercise", "gym", "run", "running", "steps", "pushups", "training", "cardio", "strength", "muscle", "fitness", "active", "sport", "lift", "lifting"]
        if has_word(t, fitness_keywords):
            st.write("🏋️ ROUTER: Keyword match found for FITNESS")
            return "fitness"
        
        nutrition_keywords = ["meal", "eat", "eating", "breakfast", "lunch", "dinner", "snack", "calorie", "calories", "food", "hungry", "nutrition", "diet", "protein", "carbs", "fat"]
        if has_word(t, nutrition_keywords):
            st.write("🍎 ROUTER: Keyword match found for NUTRITION")
            return "nutrition"
        
        health_keywords = ["symptom", "pain", "doctor", "health", "medicine", "sick", "illness", "anxious", "anxiety", "stress", "depression", "mental", "mood", "sleep", "tired", "fatigue", "headache", "ache", "aching", "hurt", "sore"]
        if has_word(t, health_keywords):
            st.write("🩺 ROUTER: Keyword match found for HEALTH")
            return "health"
        
        st.write("🤖 ROUTER: No keyword matches, defaulting to MISC")
        return "misc"

    def route(self, text: str):
        return self.classify(text)
