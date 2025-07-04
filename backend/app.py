from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TravelRequest(BaseModel):
    source: str
    destination: str
    budget: int
    travel_mode: str  # e.g., "road" or "air"
    language: str     # e.g., "en", "ur", etc.

@app.post("/plan-trip")
def plan_trip(request: TravelRequest):
    # Example simple response logic (you can replace this with your AI/agent logic)
    trip_summary = {
        "source": request.source,
        "destination": request.destination,
        "mode": request.travel_mode,
        "budget": request.budget,
        "suggestion": f"Traveling from {request.source} to {request.destination} by {request.travel_mode} with a budget of {request.budget} PKR."
    }

    # Optional: Translate or localize the suggestion based on request.language
    return {"trip_plan": trip_summary}
