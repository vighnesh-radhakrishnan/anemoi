from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import fastf1
import asyncio
import pandas as pd
from datetime import datetime
app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
def read_root():
    return {"message": "Hello, Welcome to Anemoi!"}

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

# Enable caching for fastf1 to improve performance
fastf1.Cache.enable_cache('cache_directory')

# In-memory session store
session_store = {}

# Function to load only required session data asynchronously
async def fetch_session_data(year, gp, identifier):
    # Check if session data is already cached
    if (year, gp, identifier) in session_store:
        return session_store[(year, gp, identifier)]

    try:
        # Use fastf1 to fetch minimal session data
        event = fastf1.get_event(year, gp)
        session = event.get_session(identifier)
        session.load_results()  # Only load results table

        # Process results only if they exist
        results = None
        if session.results is not None and not session.results.empty:
            # Process only required columns
            results = session.results[['Position', 'HeadshotUrl', 'BroadcastName', 'FullName', 'TeamName', 'Time', 'Status', 'Points']]
            results = results.apply(lambda row: {
                'Position': row['Position'],
                'HeadshotUrl': row['HeadshotUrl'],
                'BroadcastName': row['BroadcastName'],
                'FullName': row['FullName'],
                'TeamName': row['TeamName'],
                'Time': str(row['Time']) if pd.notna(row['Time']) else None,
                'Status': row['Status'],
                'Points': row['Points']
            }, axis=1).tolist()

        # Structure session data
        session_data = {
            "Year": year,
            "GrandPrix": gp,
            "Session": identifier,
            "Date": str(session.date),
            "Event": session.event['EventName'],
            "Location": session.event['Location'],
            "Results": results if results else []
        }

        # Cache the session data
        session_store[(year, gp, identifier)] = session_data
        return session_data

    except Exception as e:
        print(f"Error fetching session data: {e}")
        return None

@app.get("/session")
async def get_session_data(year: int, gp: str, identifier: str):
    start_time = datetime.now()  # Measure response time
    try:
        # Fetch session data
        session_data = await fetch_session_data(year, gp, identifier)

        # If session data is unavailable
        if session_data is None:
            return JSONResponse(content={"error": "Session data unavailable"}, status_code=404)

        end_time = datetime.now()
        print(f"Response time: {end_time - start_time}")  # Log response time

        # Return session data
        return JSONResponse(content={"session": session_data})

    except Exception as e:
        print(f"Error fetching session data: {e}")
        return JSONResponse(content={"error": "Session data unavailable"}, status_code=500)

@app.get("/multi-session")
async def get_multiple_sessions(sessions: list):
    # Example input: [{"year": 2020, "gp": "Hungarian Grand Prix", "identifier": "race"}, ...]
    start_time = datetime.now()
    try:
        session_requests = [(s['year'], s['gp'], s['identifier']) for s in sessions]
        results = await asyncio.gather(*(fetch_session_data(*req) for req in session_requests))

        end_time = datetime.now()
        print(f"Total response time for multiple sessions: {end_time - start_time}")

        return JSONResponse(content={"sessions": results})

    except Exception as e:
        print(f"Error fetching multiple sessions: {e}")
        return JSONResponse(content={"error": "Failed to fetch sessions"}, status_code=500)