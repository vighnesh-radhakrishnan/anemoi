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

# Define the route for fetching session data
@app.get("/session")
async def get_session_data():
    try:
        # Hardcoded values for now
        year = 2020
        gp = "Austria"
        identifier = "Race"

        # Fetch the session
        session = fastf1.get_session(year, gp, identifier)

        if session is None:
            return JSONResponse(content={"error": "Session data unavailable"})

        # Load the session data (required to access timing/telemetry)
        session.load()
        results = session.results
        print(f"DATA: {results}")

        # Create a basic response with session details
        session_data = {
            "Year": year,
            "GrandPrix": gp,
            "Session": identifier,
            "Date": str(session.date),
            "Event": session.event['EventName'],
            "Location": session.event['Location'],
            # "Results": results,
        }

        return JSONResponse(content={"session": session_data})
    except Exception as e:
        print(f"Error fetching session data: {e}")
        return JSONResponse(content={"error": "Session data unavailable"})
