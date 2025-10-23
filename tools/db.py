# Database utilities
from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime, timezone
from app.config import settings

engine = create_engine(settings.DB_URL, echo=False)

class Meal(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user: str
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str
    calories: float | None = None

class DailyNutrition(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user: str
    date: str  # YYYY-MM-DD format
    meal_type: str  # breakfast, lunch, dinner
    food_items: str  # JSON string of food items
    total_calories: float | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    fiber_g: float | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Workout(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user: str
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str
    duration_min: float | None = None
    calories: float | None = None

class WorkoutSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user: str
    date: str  # YYYY-MM-DD format
    workout_type: str  # cardio, strength, flexibility, sports, etc.
    exercise_name: str
    duration_min: float
    calories_burned: float
    intensity: str  # low, moderate, high
    notes: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserProfile(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user: str = Field(unique=True)
    
    # Basic Info
    age: int | None = None
    gender: str | None = None  # male, female, other
    height_cm: float | None = None
    weight_kg: float | None = None
    
    # Health Info
    activity_level: str | None = None  # sedentary, lightly_active, moderately_active, very_active, extremely_active
    health_conditions: str | None = None  # JSON string of conditions
    medications: str | None = None
    allergies: str | None = None
    
    # Fitness Goals
    primary_goal: str | None = None  # weight_loss, muscle_gain, maintenance, endurance, strength
    target_weight_kg: float | None = None
    fitness_experience: str | None = None  # beginner, intermediate, advanced
    
    # Lifestyle
    sleep_hours: float | None = None
    stress_level: str | None = None  # low, moderate, high
    smoking: bool | None = None
    alcohol_frequency: str | None = None  # never, rarely, occasionally, regularly
    
    # Calculated Values
    bmi: float | None = None
    body_age: int | None = None
    daily_calorie_goal: int | None = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
