import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from agents.run_graph import run_agent
from tools.db import get_session, Meal, Workout, DailyNutrition, WorkoutSession, UserProfile, init_db
from sqlmodel import select

# Initialize database on startup
init_db()

st.set_page_config(page_title="AI Wellness Assistant", page_icon="💪", layout="wide")

# Custom CSS for better chat appearance
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    
    .stChatMessage[data-testid="chat-message-user"] {
        background-color: #e3f2fd;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] {
        background-color: #f5f5f5;
    }
    
    .chat-input {
        position: sticky;
        bottom: 0;
        background: white;
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🏋️ Wellness Menu")
page = st.sidebar.radio("Navigate", ["Chat", "Profile", "Meal Logger", "Workout Logger", "Dashboard"])

user = st.text_input("Your name", value="Nikhil")

# --- CHAT PAGE ---
if page == "Chat":
    st.title("💬 AI Wellness Chat")
    st.markdown("*Ask me about fitness, nutrition, or health - I'm here to help!*")
    
    # Add example prompts and clear button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Try asking:** *I want to start working out*, *I'm feeling anxious*, *What's a healthy breakfast?*")
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat = []
            st.rerun()

    if "chat" not in st.session_state:
        st.session_state.chat = []

    # Display chat messages with proper formatting
    for who, txt in st.session_state.chat:
        if who == "You":
            with st.chat_message("user"):
                st.write(txt)
        else:
            with st.chat_message("assistant"):
                st.write(txt)

    # Chat input at the bottom
    msg = st.chat_input("Ask about workouts, meals, or health...")
    if msg:
        # Add user message immediately
        with st.chat_message("user"):
            st.write(msg)
        
        # Get AI response
        with st.spinner("Thinking..."):
            ans = run_agent(user, msg)
        
        # Add AI response
        with st.chat_message("assistant"):
            st.write(ans)
        
        # Store in session state
        st.session_state.chat.append(("You", msg))
        st.session_state.chat.append(("AI", ans))
        
        # Rerun to update the display
        st.rerun()

# --- PROFILE PAGE ---
elif page == "Profile":
    st.title("👤 User Profile")
    st.markdown("*Complete your profile to get personalized AI recommendations*")
    
    from tools.db import UserProfile
    from tools.profile_analyzer import profile_analyzer
    from datetime import datetime, timezone
    
    # Get existing profile
    with get_session() as s:
        profile = s.exec(select(UserProfile).where(UserProfile.user == user)).first()
    
    # Create tabs for different sections
    basic_tab, health_tab, goals_tab, analysis_tab = st.tabs(["📋 Basic Info", "🏥 Health Info", "🎯 Goals", "📊 Analysis"])
    
    # Initialize profile data
    if not profile:
        profile = UserProfile(user=user)
    
    # Basic Info Tab
    with basic_tab:
        st.subheader("Basic Information")
        
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("Age", min_value=13, max_value=120, value=int(profile.age or 25), key="age")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                index=["male", "female", "other"].index(profile.gender or "male"), key="gender")
            height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, 
                                      value=float(profile.height_cm or 170), key="height")
        
        with col2:
            weight_kg = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, 
                                      value=float(profile.weight_kg or 70), key="weight")
            activity_level = st.selectbox("Activity Level", 
                                        ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extremely Active"],
                                        index=["sedentary", "lightly_active", "moderately_active", "very_active", "extremely_active"].index(profile.activity_level or "moderately_active"),
                                        key="activity")
            sleep_hours = st.number_input("Average Sleep (hours)", min_value=3.0, max_value=12.0, 
                                        value=float(profile.sleep_hours or 7.5), step=0.5, key="sleep")
    
    # Health Info Tab
    with health_tab:
        st.subheader("Health Information")
        
        col1, col2 = st.columns(2)
        with col1:
            health_conditions = st.text_area("Health Conditions (if any)", 
                                           value=profile.health_conditions or "",
                                           placeholder="e.g., diabetes, hypertension, asthma",
                                           key="conditions")
            medications = st.text_area("Current Medications", 
                                     value=profile.medications or "",
                                     placeholder="List any medications you're taking",
                                     key="medications")
        
        with col2:
            allergies = st.text_area("Allergies", 
                                   value=profile.allergies or "",
                                   placeholder="Food allergies, environmental allergies, etc.",
                                   key="allergies")
            stress_level = st.selectbox("Stress Level", ["Low", "Moderate", "High"],
                                      index=["low", "moderate", "high"].index(profile.stress_level or "moderate"),
                                      key="stress")
        
        col3, col4 = st.columns(2)
        with col3:
            smoking = st.selectbox("Do you smoke?", ["No", "Yes"], 
                                 index=1 if profile.smoking else 0, key="smoking")
        with col4:
            alcohol = st.selectbox("Alcohol Consumption", ["Never", "Rarely", "Occasionally", "Regularly"],
                                 index=["never", "rarely", "occasionally", "regularly"].index(profile.alcohol_frequency or "rarely"),
                                 key="alcohol")
    
    # Goals Tab
    with goals_tab:
        st.subheader("Fitness Goals")
        
        col1, col2 = st.columns(2)
        with col1:
            primary_goal = st.selectbox("Primary Goal", 
                                      ["Weight Loss", "Muscle Gain", "Maintenance", "Endurance", "Strength"],
                                      index=["weight_loss", "muscle_gain", "maintenance", "endurance", "strength"].index(profile.primary_goal or "maintenance"),
                                      key="goal")
            target_weight = st.number_input("Target Weight (kg)", min_value=30.0, max_value=300.0,
                                          value=float(profile.target_weight_kg or weight_kg), key="target_weight")
        
        with col2:
            fitness_experience = st.selectbox("Fitness Experience", ["Beginner", "Intermediate", "Advanced"],
                                            index=["beginner", "intermediate", "advanced"].index(profile.fitness_experience or "beginner"),
                                            key="experience")
    
    # Save Profile Button
    if st.button("💾 Save Profile", type="primary"):
        # Update profile with form data
        profile.age = age
        profile.gender = gender.lower()
        profile.height_cm = height_cm
        profile.weight_kg = weight_kg
        profile.activity_level = activity_level.lower().replace(" ", "_")
        profile.sleep_hours = sleep_hours
        profile.health_conditions = health_conditions if health_conditions.strip() else None
        profile.medications = medications if medications.strip() else None
        profile.allergies = allergies if allergies.strip() else None
        profile.stress_level = stress_level.lower()
        profile.smoking = smoking == "Yes"
        profile.alcohol_frequency = alcohol.lower()
        profile.primary_goal = primary_goal.lower().replace(" ", "_")
        profile.target_weight_kg = target_weight
        profile.fitness_experience = fitness_experience.lower()
        profile.updated_at = datetime.now(timezone.utc)
        
        # Calculate BMI
        profile.bmi = profile_analyzer.calculate_bmi(weight_kg, height_cm)
        
        # Calculate daily calorie goal
        profile_dict = {
            'age': age, 'weight_kg': weight_kg, 'height_cm': height_cm,
            'gender': gender.lower(), 'activity_level': activity_level.lower().replace(" ", "_"),
            'primary_goal': primary_goal.lower().replace(" ", "_")
        }
        profile.daily_calorie_goal = profile_analyzer.calculate_daily_calories(profile_dict)
        
        # Save to database
        with get_session() as s:
            existing = s.exec(select(UserProfile).where(UserProfile.user == user)).first()
            if existing:
                # Update existing profile
                for key, value in profile.model_dump(exclude={'id', 'user', 'created_at'}).items():
                    setattr(existing, key, value)
                s.add(existing)
            else:
                # Create new profile
                s.add(profile)
            s.commit()
        
        st.success("✅ Profile saved successfully!")
        st.balloons()
        st.rerun()
    
    # Analysis Tab
    with analysis_tab:
        if profile.age and profile.height_cm and profile.weight_kg:
            st.subheader("📊 Health Analysis")
            
            # BMI Analysis
            bmi = profile_analyzer.calculate_bmi(profile.weight_kg, profile.height_cm)
            bmi_category = profile_analyzer.get_bmi_category(bmi)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("BMI", f"{bmi:.1f}")
                st.write(f"**Category:** {bmi_category}")
            
            with col2:
                if profile.daily_calorie_goal:
                    st.metric("Daily Calorie Goal", f"{profile.daily_calorie_goal}")
                else:
                    st.metric("Daily Calorie Goal", "Not calculated")
            
            with col3:
                weight_diff = (profile.target_weight_kg or profile.weight_kg) - profile.weight_kg
                st.metric("Weight to Goal", f"{weight_diff:+.1f} kg")
            
            # Body Age Analysis
            if st.button("🧬 Analyze Body Age & Health", type="secondary"):
                with st.spinner("Analyzing your health profile..."):
                    profile_dict = {
                        'age': profile.age,
                        'bmi': bmi,
                        'activity_level': profile.activity_level,
                        'sleep_hours': profile.sleep_hours,
                        'stress_level': profile.stress_level,
                        'smoking': profile.smoking,
                        'alcohol_frequency': profile.alcohol_frequency,
                        'health_conditions': profile.health_conditions
                    }
                    
                    analysis = profile_analyzer.estimate_body_age(profile_dict)
                    
                    # Update profile with body age
                    with get_session() as s:
                        existing = s.exec(select(UserProfile).where(UserProfile.user == user)).first()
                        if existing:
                            existing.body_age = analysis["body_age"]
                            s.add(existing)
                            s.commit()
                    
                    st.subheader("🎯 Health Analysis Results")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Body Age", f"{analysis['body_age']} years")
                    with col2:
                        age_diff = analysis['age_difference']
                        st.metric("vs Chronological Age", f"{age_diff:+} years")
                    with col3:
                        st.metric("Health Score", f"{analysis['health_score']}/100")
                    
                    # Key factors
                    st.subheader("🔍 Key Health Factors")
                    for factor in analysis['key_factors']:
                        st.write(f"• {factor}")
                    
                    # Recommendations
                    st.subheader("💡 Personalized Recommendations")
                    for rec in analysis['recommendations']:
                        st.write(f"• {rec}")
        else:
            st.info("Complete your basic information to see health analysis.")

# --- MEAL LOGGER PAGE ---
elif page == "Meal Logger":
    st.title("🍽️ Daily Meal Logger")
    st.markdown("*Log your daily meals and get automatic nutrition analysis*")
    
    from datetime import date
    from tools.nutrition_calculator import nutrition_calculator
    from tools.db import DailyNutrition
    import json
    
    # Date selector
    selected_date = st.date_input("Select Date", value=date.today())
    date_str = selected_date.strftime("%Y-%m-%d")
    
    # Create tabs for different meals
    breakfast_tab, lunch_tab, dinner_tab = st.tabs(["🌅 Breakfast", "☀️ Lunch", "🌙 Dinner"])
    
    def log_meal(meal_type: str, tab_container):
        with tab_container:
            st.subheader(f"{meal_type.title()} for {selected_date}")
            
            # Check if meal already logged for this date
            with get_session() as s:
                existing_meal = s.exec(
                    select(DailyNutrition).where(
                        DailyNutrition.user == user,
                        DailyNutrition.date == date_str,
                        DailyNutrition.meal_type == meal_type
                    )
                ).first()
            
            if existing_meal:
                st.success(f"✅ {meal_type.title()} already logged!")
                st.write(f"**Food items:** {existing_meal.food_items}")
                st.write(f"**Calories:** {existing_meal.total_calories:.0f}")
                st.write(f"**Protein:** {existing_meal.protein_g:.1f}g | **Carbs:** {existing_meal.carbs_g:.1f}g | **Fat:** {existing_meal.fat_g:.1f}g")
                
                if st.button(f"Update {meal_type.title()}", key=f"update_{meal_type}"):
                    with get_session() as s:
                        s.delete(existing_meal)
                        s.commit()
                    st.rerun()
            else:
                # Input form for new meal
                food_input = st.text_area(
                    f"What did you eat for {meal_type}?",
                    placeholder="e.g., 2 eggs, 1 slice whole wheat toast, 1 cup orange juice",
                    key=f"{meal_type}_input"
                )
                
                if st.button(f"Log {meal_type.title()}", key=f"log_{meal_type}"):
                    if food_input.strip():
                        with st.spinner("Calculating nutrition..."):
                            # Calculate nutrition
                            nutrition = nutrition_calculator.calculate_nutrition(food_input)
                            
                            # Save to database
                            with get_session() as s:
                                daily_nutrition = DailyNutrition(
                                    user=user,
                                    date=date_str,
                                    meal_type=meal_type,
                                    food_items=food_input,
                                    total_calories=nutrition["total_calories"],
                                    protein_g=nutrition["protein_g"],
                                    carbs_g=nutrition["carbs_g"],
                                    fat_g=nutrition["fat_g"],
                                    fiber_g=nutrition["fiber_g"]
                                )
                                s.add(daily_nutrition)
                                s.commit()
                        
                        st.success(f"✅ {meal_type.title()} logged successfully!")
                        st.write(f"**Calories:** {nutrition['total_calories']:.0f}")
                        st.write(f"**Protein:** {nutrition['protein_g']:.1f}g | **Carbs:** {nutrition['carbs_g']:.1f}g | **Fat:** {nutrition['fat_g']:.1f}g")
                        
                        # Show breakdown if available
                        if nutrition.get("breakdown"):
                            with st.expander("See detailed breakdown"):
                                for item in nutrition["breakdown"]:
                                    st.write(f"• {item['item']}: {item['calories']} cal")
                        
                        st.rerun()
                    else:
                        st.error("Please enter what you ate!")
    
    # Log meals for each tab
    log_meal("breakfast", breakfast_tab)
    log_meal("lunch", lunch_tab)
    log_meal("dinner", dinner_tab)
    
    # Daily summary
    st.subheader("📊 Daily Summary")
    with get_session() as s:
        daily_meals = s.exec(
            select(DailyNutrition).where(
                DailyNutrition.user == user,
                DailyNutrition.date == date_str
            )
        ).all()
    
    if daily_meals:
        total_calories = sum(meal.total_calories or 0 for meal in daily_meals)
        total_protein = sum(meal.protein_g or 0 for meal in daily_meals)
        total_carbs = sum(meal.carbs_g or 0 for meal in daily_meals)
        total_fat = sum(meal.fat_g or 0 for meal in daily_meals)
        total_fiber = sum(meal.fiber_g or 0 for meal in daily_meals)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Calories", f"{total_calories:.0f}")
        with col2:
            st.metric("Protein", f"{total_protein:.1f}g")
        with col3:
            st.metric("Carbs", f"{total_carbs:.1f}g")
        with col4:
            st.metric("Fat", f"{total_fat:.1f}g")
        
        # Macro breakdown chart
        if total_calories > 0:
            protein_cal = total_protein * 4
            carbs_cal = total_carbs * 4
            fat_cal = total_fat * 9
            
            macro_data = {
                "Macronutrient": ["Protein", "Carbs", "Fat"],
                "Calories": [protein_cal, carbs_cal, fat_cal],
                "Percentage": [
                    (protein_cal/total_calories)*100,
                    (carbs_cal/total_calories)*100,
                    (fat_cal/total_calories)*100
                ]
            }
            
            st.subheader("🥧 Macro Distribution")
            st.bar_chart(pd.DataFrame(macro_data).set_index("Macronutrient")["Percentage"])
    else:
        st.info("No meals logged for this date yet.")

# --- WORKOUT LOGGER PAGE ---
elif page == "Workout Logger":
    st.title("🏋️ Workout Logger")
    st.markdown("*Log your workouts and calories burned from your fitness watch*")
    
    from datetime import date
    from tools.db import WorkoutSession
    
    # Date selector
    selected_date = st.date_input("Workout Date", value=date.today(), key="workout_date")
    date_str = selected_date.strftime("%Y-%m-%d")
    
    # Workout input form
    st.subheader("📝 Log New Workout")
    
    col1, col2 = st.columns(2)
    
    with col1:
        workout_type = st.selectbox(
            "Workout Type",
            ["Cardio", "Strength Training", "Flexibility/Yoga", "Sports", "HIIT", "Walking/Running", "Cycling", "Swimming", "Other"],
            key="workout_type"
        )
        
        exercise_name = st.text_input(
            "Exercise/Activity Name",
            placeholder="e.g., Morning Run, Chest & Triceps, Yoga Flow",
            key="exercise_name"
        )
        
        duration_min = st.number_input(
            "Duration (minutes)",
            min_value=1,
            max_value=300,
            value=30,
            key="duration"
        )
    
    with col2:
        calories_burned = st.number_input(
            "Calories Burned (from fitness watch)",
            min_value=1,
            max_value=2000,
            value=200,
            key="calories"
        )
        
        intensity = st.selectbox(
            "Intensity Level",
            ["Low", "Moderate", "High"],
            index=1,
            key="intensity"
        )
        
        notes = st.text_area(
            "Notes (optional)",
            placeholder="How did you feel? Any achievements or observations?",
            key="notes"
        )
    
    if st.button("🏃‍♂️ Log Workout", type="primary"):
        if exercise_name.strip():
            with get_session() as s:
                workout_session = WorkoutSession(
                    user=user,
                    date=date_str,
                    workout_type=workout_type.lower(),
                    exercise_name=exercise_name,
                    duration_min=duration_min,
                    calories_burned=calories_burned,
                    intensity=intensity.lower(),
                    notes=notes if notes.strip() else None
                )
                s.add(workout_session)
                s.commit()
            
            st.success(f"✅ Workout logged successfully!")
            st.balloons()
            st.rerun()
        else:
            st.error("Please enter an exercise/activity name!")
    
    # Display today's workouts
    st.subheader(f"📅 Workouts for {selected_date}")
    
    with get_session() as s:
        todays_workouts = s.exec(
            select(WorkoutSession).where(
                WorkoutSession.user == user,
                WorkoutSession.date == date_str
            ).order_by(WorkoutSession.created_at.desc())
        ).all()
    
    if todays_workouts:
        for workout in todays_workouts:
            with st.expander(f"🏃‍♂️ {workout.exercise_name} - {workout.calories_burned} cal"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Type:** {workout.workout_type.title()}")
                    st.write(f"**Duration:** {workout.duration_min} min")
                with col2:
                    st.write(f"**Calories:** {workout.calories_burned}")
                    st.write(f"**Intensity:** {workout.intensity.title()}")
                with col3:
                    st.write(f"**Time:** {workout.created_at.strftime('%H:%M')}")
                    if workout.notes:
                        st.write(f"**Notes:** {workout.notes}")
                
                # Delete button
                if st.button(f"🗑️ Delete", key=f"delete_{workout.id}"):
                    with get_session() as s:
                        s.delete(workout)
                        s.commit()
                    st.success("Workout deleted!")
                    st.rerun()
        
        # Daily summary
        total_duration = sum(w.duration_min for w in todays_workouts)
        total_calories = sum(w.calories_burned for w in todays_workouts)
        
        st.subheader("📊 Daily Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Workouts", len(todays_workouts))
        with col2:
            st.metric("Total Duration", f"{total_duration} min")
        with col3:
            st.metric("Total Calories Burned", f"{total_calories}")
    else:
        st.info("No workouts logged for this date yet.")
    
    # Recent workouts (last 7 days)
    st.subheader("📈 Recent Activity")
    
    from datetime import timedelta
    week_ago = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    with get_session() as s:
        recent_workouts = s.exec(
            select(WorkoutSession).where(
                WorkoutSession.user == user,
                WorkoutSession.date >= week_ago
            ).order_by(WorkoutSession.date.desc(), WorkoutSession.created_at.desc())
        ).all()
    
    if recent_workouts:
        # Group by date
        workouts_by_date = {}
        for workout in recent_workouts:
            if workout.date not in workouts_by_date:
                workouts_by_date[workout.date] = []
            workouts_by_date[workout.date].append(workout)
        
        for workout_date, workouts in workouts_by_date.items():
            daily_calories = sum(w.calories_burned for w in workouts)
            daily_duration = sum(w.duration_min for w in workouts)
            
            st.write(f"**{workout_date}** - {len(workouts)} workout(s), {daily_duration} min, {daily_calories} cal")
            
            for workout in workouts:
                st.write(f"  • {workout.exercise_name} ({workout.workout_type}) - {workout.duration_min}min, {workout.calories_burned} cal")
    else:
        st.info("No recent workouts found.")

# --- DASHBOARD PAGE ---
else:
    st.title("📊 Progress Dashboard")

    from tools.db import DailyNutrition
    from datetime import date, timedelta
    
    with get_session() as s:
        workouts = s.exec(select(Workout).where(Workout.user == user)).all()
        meals = s.exec(select(Meal).where(Meal.user == user)).all()
        
        # Get nutrition data for last 7 days
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        nutrition_data = s.exec(
            select(DailyNutrition).where(
                DailyNutrition.user == user,
                DailyNutrition.date >= start_date.strftime("%Y-%m-%d"),
                DailyNutrition.date <= end_date.strftime("%Y-%m-%d")
            )
        ).all()

    st.subheader(f"👤 {user}'s Wellness Summary")

    # Get workout data for today's summary
    today_str = end_date.strftime("%Y-%m-%d")
    with get_session() as s:
        todays_workouts = s.exec(
            select(WorkoutSession).where(
                WorkoutSession.user == user,
                WorkoutSession.date == today_str
            )
        ).all()
        
        todays_meals = s.exec(
            select(DailyNutrition).where(
                DailyNutrition.user == user,
                DailyNutrition.date == today_str
            )
        ).all()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Workouts", len(workouts))
    with col2:
        st.metric("Total Meals", len(meals))
    with col3:
        unique_days = len(set(n.date for n in nutrition_data))
        st.metric("Days Tracked", unique_days)
    with col4:
        # Today's calories in
        todays_calories_in = sum(m.total_calories or 0 for m in todays_meals)
        st.metric("Today: Calories In", f"{todays_calories_in:.0f}")
    with col5:
        # Today's calories out
        todays_calories_out = sum(w.calories_burned or 0 for w in todays_workouts)
        st.metric("Today: Calories Out", f"{todays_calories_out:.0f}")



    # Nutrition Analytics
    st.subheader("📈 Nutrition Analytics (Last 7 Days)")
    if nutrition_data:
        # Group by date for daily totals
        daily_totals = {}
        for n in nutrition_data:
            if n.date not in daily_totals:
                daily_totals[n.date] = {
                    "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0
                }
            daily_totals[n.date]["calories"] += n.total_calories or 0
            daily_totals[n.date]["protein"] += n.protein_g or 0
            daily_totals[n.date]["carbs"] += n.carbs_g or 0
            daily_totals[n.date]["fat"] += n.fat_g or 0
            daily_totals[n.date]["fiber"] += n.fiber_g or 0
        
        # Create charts
        if daily_totals:
            dates = list(daily_totals.keys())
            calories = [daily_totals[d]["calories"] for d in dates]
            
            # Daily calories chart
            st.subheader("🔥 Daily Calories")
            chart_data = pd.DataFrame({
                "Date": dates,
                "Calories": calories
            })
            st.line_chart(chart_data.set_index("Date"))
            
            # Macro trends
            st.subheader("🥗 Macro Trends")
            macro_data = pd.DataFrame({
                "Date": dates,
                "Protein (g)": [daily_totals[d]["protein"] for d in dates],
                "Carbs (g)": [daily_totals[d]["carbs"] for d in dates],
                "Fat (g)": [daily_totals[d]["fat"] for d in dates]
            })
            st.line_chart(macro_data.set_index("Date"))
            
            # Weekly averages
            st.subheader("📊 Weekly Averages")
            avg_calories = sum(calories) / len(calories)
            avg_protein = sum(daily_totals[d]["protein"] for d in dates) / len(dates)
            avg_carbs = sum(daily_totals[d]["carbs"] for d in dates) / len(dates)
            avg_fat = sum(daily_totals[d]["fat"] for d in dates) / len(dates)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Calories", f"{avg_calories:.0f}")
            with col2:
                st.metric("Avg Protein", f"{avg_protein:.1f}g")
            with col3:
                st.metric("Avg Carbs", f"{avg_carbs:.1f}g")
            with col4:
                st.metric("Avg Fat", f"{avg_fat:.1f}g")
    else:
        st.info("Start logging meals to see nutrition analytics!")

    # Calorie Balance Analysis
    st.subheader("⚖️ Calorie Balance (Last 7 Days)")
    
    # Get workout data for calorie balance
    with get_session() as s:
        workout_data = s.exec(
            select(WorkoutSession).where(
                WorkoutSession.user == user,
                WorkoutSession.date >= start_date.strftime("%Y-%m-%d"),
                WorkoutSession.date <= end_date.strftime("%Y-%m-%d")
            )
        ).all()
    
    if nutrition_data or workout_data:
        # Create daily calorie balance
        daily_balance = {}
        
        # Initialize all dates in range
        for i in range(8):  # Last 7 days + today
            date_key = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
            daily_balance[date_key] = {
                "calories_in": 0,
                "calories_out": 0,
                "net_calories": 0
            }
        
        # Add nutrition data (calories in)
        for n in nutrition_data:
            if n.date in daily_balance:
                daily_balance[n.date]["calories_in"] += n.total_calories or 0
        
        # Add workout data (calories out)
        for w in workout_data:
            if w.date in daily_balance:
                daily_balance[w.date]["calories_out"] += w.calories_burned or 0
        
        # Calculate net calories
        for date_key in daily_balance:
            daily_balance[date_key]["net_calories"] = (
                daily_balance[date_key]["calories_in"] - daily_balance[date_key]["calories_out"]
            )
        
        # Sort dates
        sorted_dates = sorted(daily_balance.keys())
        
        if any(daily_balance[d]["calories_in"] > 0 or daily_balance[d]["calories_out"] > 0 for d in sorted_dates):
            # Create balance chart
            balance_data = pd.DataFrame({
                "Date": sorted_dates,
                "Calories In": [daily_balance[d]["calories_in"] for d in sorted_dates],
                "Calories Out": [daily_balance[d]["calories_out"] for d in sorted_dates],
                "Net Calories": [daily_balance[d]["net_calories"] for d in sorted_dates]
            })
            
            st.subheader("📊 Daily Calorie Balance")
            
            # Show metrics for today
            today_str = end_date.strftime("%Y-%m-%d")
            if today_str in daily_balance:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Today: Calories In", f"{daily_balance[today_str]['calories_in']:.0f}")
                with col2:
                    st.metric("Today: Calories Out", f"{daily_balance[today_str]['calories_out']:.0f}")
                with col3:
                    net_today = daily_balance[today_str]['net_calories']
                    st.metric("Today: Net Calories", f"{net_today:+.0f}")
                with col4:
                    # Get user's daily calorie goal from profile
                    with get_session() as s:
                        profile = s.exec(select(UserProfile).where(UserProfile.user == user)).first()
                        if profile and profile.daily_calorie_goal:
                            goal_diff = daily_balance[today_str]['calories_in'] - profile.daily_calorie_goal
                            st.metric("vs Goal", f"{goal_diff:+.0f}")
                        else:
                            st.metric("Daily Goal", "Not set")
            
            # Calorie In vs Out Chart
            st.subheader("🔥 Calories In vs Out")
            chart_data = balance_data.set_index("Date")[["Calories In", "Calories Out"]]
            st.bar_chart(chart_data)
            
            # Net Calorie Trend
            st.subheader("📈 Net Calorie Trend")
            net_chart = balance_data.set_index("Date")[["Net Calories"]]
            st.line_chart(net_chart)
            
            # Weekly summary
            total_in = sum(daily_balance[d]["calories_in"] for d in sorted_dates)
            total_out = sum(daily_balance[d]["calories_out"] for d in sorted_dates)
            avg_in = total_in / len([d for d in sorted_dates if daily_balance[d]["calories_in"] > 0]) if any(daily_balance[d]["calories_in"] > 0 for d in sorted_dates) else 0
            avg_out = total_out / len([d for d in sorted_dates if daily_balance[d]["calories_out"] > 0]) if any(daily_balance[d]["calories_out"] > 0 for d in sorted_dates) else 0
            
            st.subheader("📊 Weekly Summary")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Calories In", f"{total_in:.0f}")
            with col2:
                st.metric("Total Calories Out", f"{total_out:.0f}")
            with col3:
                st.metric("Net Weekly", f"{total_in - total_out:+.0f}")
            with col4:
                # Estimated weight change (3500 cal = 1 lb)
                weight_change_lbs = (total_in - total_out) / 3500
                st.metric("Est. Weight Change", f"{weight_change_lbs:+.2f} lbs")
            
            # Daily breakdown table
            st.subheader("📅 Daily Breakdown")
            
            # Create a more detailed table
            detailed_data = []
            for date_key in sorted_dates:
                detailed_data.append({
                    "Date": date_key,
                    "Calories In": f"{daily_balance[date_key]['calories_in']:.0f}",
                    "Calories Out": f"{daily_balance[date_key]['calories_out']:.0f}",
                    "Net": f"{daily_balance[date_key]['net_calories']:+.0f}",
                    "Status": "Surplus" if daily_balance[date_key]['net_calories'] > 0 else "Deficit" if daily_balance[date_key]['net_calories'] < 0 else "Balanced"
                })
            
            df_balance = pd.DataFrame(detailed_data)
            st.dataframe(df_balance, width='stretch')
            
        else:
            st.info("Start logging meals and workouts to see calorie balance analysis!")
    else:
        st.info("No data available for calorie balance analysis. Start logging meals and workouts!")
