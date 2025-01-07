from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import fastf1

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Define the route for fetching event schedule
@app.get("/events/{year}")
async def get_event_schedule(year: int):
    try:
        # Fetch the event schedule for the given year
        schedule = fastf1.get_event_schedule(year)

        if schedule is None or schedule.empty:
            return JSONResponse(content={"error": f"No schedule found for year {year}"})

        events = []
        for _, event in schedule.iterrows():
            events.append({
                "RoundNumber": event.get("RoundNumber", "N/A"),
                "Country": event.get("Country", "N/A"),
                "Location": event.get("Location", "N/A"),
                "EventName": event.get("EventName", "N/A"),
                "EventDate": str(event.get("EventDate", "N/A")),
                "EventFormat": event.get("EventFormat", "N/A"),
                "Qualifying": str(event.get("Session4DateUtc", "N/A")),
                "Race": str(event.get("Session5DateUtc", "N/A")),
            })

        return JSONResponse(content={"year": year, "events": events})
    except Exception as e:
        print(f"Error fetching event schedule: {e}")
        return JSONResponse(content={"error": "Data unavailable"})
