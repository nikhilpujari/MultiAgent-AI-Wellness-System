from tools.db import get_session, Meal, Workout
from sqlmodel import select

class TrackingAgent:
    """Aggregates meals and workouts for progress summaries."""

    def summarize(self, user: str) -> str:
        with get_session() as s:
            meals = s.exec(select(Meal).where(Meal.user == user)).all()
            workouts = s.exec(select(Workout).where(Workout.user == user)).all()

        total_meals = len(meals)
        total_workouts = len(workouts)
        summary = (
            f"You've logged {total_meals} meals and {total_workouts} workouts so far.\n"
            f"Keep going strong! 💪"
        )
        return f"📊 *[Progress Tracker]*\n{summary}"
