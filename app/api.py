# API endpoints for AI Wellness
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "AI Wellness API"}