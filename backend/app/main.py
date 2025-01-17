import io
import base64
import fastf1
import pandas as pd
import numpy as np
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection

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

# Define the route for fetching session data

@app.get("/session")
async def get_session_data(year: int, gp: str, identifier: str):
    try:
        # Fetch the session
        session = fastf1.get_session(year, gp, identifier)

        if session is None:
            return JSONResponse(content={"error": "Session data unavailable"})

        # Load the session data (required to access timing/telemetry)
        session.load(laps=True, telemetry=False, weather=False, messages=False)

        # Initialize results as None
        results = None

        # Check if session results are available
        if session.results is not None and not session.results.empty:
            # Extract only the required fields from the session results

            results = []
            for _, row in session.results.iterrows():
                result = {
                    'Position': int(row['Position']) if pd.notna(row['Position']) else None,
                    'HeadshotUrl': row['HeadshotUrl'],
                    'BroadcastName': row['BroadcastName'],
                    'FullName': row['FullName'],
                    'TeamName': row['TeamName'],
                    'Time': str(row['Time']) if pd.notna(row['Time']) else None,
                    'Status': row['Status'] if row['Status'] else None,
                    'Points': float(row['Points']) if pd.notna(row['Points']) and not isinstance(row['Points'], str) else None
                }
                results.append(result)
        else:
            print("Results data is unavailable or empty")

        # Create a basic response with session details
        session_data = {
            "Year": year,
            "GrandPrix": gp,
            "Session": identifier,
            "Date": str(session.date),
            "Event": session.event['EventName'],
            "Location": session.event['Location'],
        }

        # Add results only if they are available
        if results:
            session_data["Results"] = results

        print(f"Session Data: {session_data}")

        return JSONResponse(content={"session": session_data})

    except Exception as e:
        print(f"Error fetching session data: {e}")
        return JSONResponse(content={"error": "Session data unavailable"})
    

@app.get("/telemetry")
async def get_fastest_lap_telemetry_base64(year: int, gp: str, identifier: str, driver: str):
    try:
        # Load the session and telemetry data
        session = fastf1.get_session(year, gp, identifier)
        session.load(laps=True, telemetry=True, weather=False, messages=False)

        # Debug: Print the session event details to check what's available
        print(f"Session Event: {session.event}")

        # Get the fastest lap for the specified driver
        fastest_lap = session.laps.pick_driver(driver)

        # Check if a fastest lap is available for the driver
        if fastest_lap.empty:
            return JSONResponse(content={"error": f"No fastest lap data available for driver {driver}"})

        fastest_lap = fastest_lap.pick_fastest()

        # Get telemetry data with added distance
        telemetry = fastest_lap.get_telemetry().add_distance()

        # Generate the base64 image
        base64_img = plot_fastest_lap_to_base64(telemetry, driver, gp, identifier, session.event["EventName"])
        
        if base64_img:
            # Safely handle missing 'Date' field
            session_data = {
                "GrandPrix": session.event["EventName"],
                "Year": year,
                "Session": identifier,
                "Driver": driver,
                "Event": session.event["EventName"],
                "Location": session.event.get("Location", "Unknown"),  # Default to "Unknown" if not available
            }
            return JSONResponse(content={"session": session_data, "image_base64": base64_img})
        else:
            return JSONResponse(content={"error": "Failed to generate plot"})

    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={"error": "An error occurred while processing the data"})


def plot_fastest_lap_to_base64(telemetry, driver, gp, identifier, event_name):
    try:
        # Check for missing or invalid telemetry data
        if "X" not in telemetry or "Y" not in telemetry or "Speed" not in telemetry:
            raise ValueError("Telemetry data is incomplete or missing necessary columns.")
        
        x = telemetry["X"].to_numpy()
        y = telemetry["Y"].to_numpy()
        speed = telemetry["Speed"].to_numpy()

        # Handle NaN values by removing them
        valid_indices = ~np.isnan(x) & ~np.isnan(y) & ~np.isnan(speed)
        x = x[valid_indices]
        y = y[valid_indices]
        speed = speed[valid_indices]

        if len(x) == 0 or len(y) == 0 or len(speed) == 0:
            raise ValueError("No valid telemetry data available for plotting.")

        # Normalize speed for color mapping
        norm = plt.Normalize(speed.min(), speed.max())
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        # Create the plot with an adjusted figure size
        fig, ax = plt.subplots(figsize=(8, 6))  # Adjusted to an appropriate size (8x6)
        cmap = plt.get_cmap("viridis")
        lc = LineCollection(segments, cmap=cmap, norm=norm)
        lc.set_array(speed)
        lc.set_linewidth(3)
        ax.add_collection(lc)
        ax.autoscale()
        ax.axis("off")
        cbar = plt.colorbar(lc, ax=ax)
        cbar.set_label("Speed (km/h)")
        ax.set_title(f"{event_name} ({gp} - {identifier})\nFastest Lap: {driver}", fontsize=14)

        # Save the plot to a BytesIO object and encode to Base64
        img_stream = io.BytesIO()
        plt.savefig(img_stream, format="png", dpi=300, bbox_inches="tight")
        plt.close(fig)
        img_stream.seek(0)
        base64_img = base64.b64encode(img_stream.getvalue()).decode('utf-8')
        return base64_img

    except Exception as e:
        print(f"Error while plotting: {e}")
        return None