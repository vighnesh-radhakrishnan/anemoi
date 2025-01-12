from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import fastf1
import asyncio
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

# Function to fetch session data asynchronously with timeout
async def fetch_session_data(year, gp, identifier, timeout=30):
    try:
        # Fetch session data using fastf1
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

        return session_data

    except Exception as e:
        print(f"Error fetching session data: {e}")
        return None

@app.get("/session")
async def get_session_data(year: int, gp: str, identifier: str):
    start_time = datetime.now()  # Measure response time
    try:
        # Fetch session data with a timeout
        session_data = await asyncio.wait_for(fetch_session_data(year, gp, identifier), timeout=30)

        # If session data is unavailable
        if session_data is None:
            return JSONResponse(content={"error": "Session data unavailable"}, status_code=404)

        end_time = datetime.now()
        print(f"Response time: {end_time - start_time}")  # Log response time

        # Return session data
        return JSONResponse(content={"session": session_data})

    except asyncio.TimeoutError:
        return JSONResponse(content={"error": "Session data request timed out"}, status_code=408)
    except Exception as e:
        print(f"Error fetching session data: {e}")
        return JSONResponse(content={"error": "Session data unavailable"}, status_code=500)

@app.get("/multi-session")
async def get_multiple_sessions(sessions: list):
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
