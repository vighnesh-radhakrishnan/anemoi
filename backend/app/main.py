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
import requests

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
        fastest_lap = session.laps.pick_drivers(driver)

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

        # Create the plot with a smaller figure size
        fig, ax = plt.subplots(figsize=(3, 1.5))  # Reduce the circuit plot size (3x1.5)
        cmap = plt.get_cmap("viridis")
        
        # Reduce the line width here
        lc = LineCollection(segments, cmap=cmap, norm=norm, linewidth=1)  # Set linewidth to 1 (smaller)
        lc.set_array(speed)
        ax.add_collection(lc)
        ax.autoscale()
        ax.axis("off")

        # Adjust the color bar size
        cbar = plt.colorbar(lc, ax=ax, fraction=0.025, pad=0.03)  # Even smaller fraction and padding
        cbar.set_label("Speed (km/h)", fontsize=6)  # Smaller font size for the label
        cbar.ax.tick_params(labelsize=5)  # Further reduce tick label size
        cbar.ax.set_ylim([speed.min(), speed.max()])  # Ensure the color bar range matches the data

        # Save the plot to a BytesIO object and encode to Base64
        img_stream = io.BytesIO()
        plt.savefig(img_stream, format="png", dpi=300, bbox_inches="tight")  # Reduced DPI (300)
        plt.close(fig)
        img_stream.seek(0)
        base64_img = base64.b64encode(img_stream.getvalue()).decode('utf-8')
        return base64_img

    except Exception as e:
        print(f"Error while plotting: {e}")
        return None


@app.get("/circuits")
async def get_circuits(
    year: int = None, 
    circuit_id: str = None, 
    driver_id: str = None, 
    constructor_id: str = None, 
    country: str = None
):
    try:
        base_url = "http://ergast.com/api/f1"
        url = base_url + "/circuits.json"
        limit = 100
        offset = 0
        all_circuits = []

        # Build the base URL based on parameters
        if circuit_id:
            url = f"{base_url}/circuits/{circuit_id}.json"
        elif year and driver_id and constructor_id:
            url = f"{base_url}/{year}/drivers/{driver_id}/constructors/{constructor_id}/circuits.json"
        elif year:
            url = f"{base_url}/{year}/circuits.json"
        elif driver_id and constructor_id:
            url = f"{base_url}/drivers/{driver_id}/constructors/{constructor_id}/circuits.json"
        elif driver_id or constructor_id:
            return JSONResponse(
                content={"error": "Both driver_id and constructor_id are required for filtering by driver/constructor."},
                status_code=400,
            )

        while True:
            response = requests.get(f"{url}?limit={limit}&offset={offset}")
            if response.status_code != 200:
                return JSONResponse(content={"error": "Failed to fetch circuit data"}, status_code=500)

            data = response.json()
            circuits = data.get("MRData", {}).get("CircuitTable", {}).get("Circuits", [])
            all_circuits.extend(circuits)

            # Check if all pages are fetched
            total = int(data.get("MRData", {}).get("total", 0))
            offset += limit
            if offset >= total:
                break

        # Apply country filter
        if country:
            all_circuits = [
                circuit for circuit in all_circuits
                if circuit.get("Location", {}).get("country", "").lower() == country.lower()
            ]

        # Transform the data
        result = []
        for circuit in all_circuits:
            location = circuit.get("Location", {})
            result.append({
                "circuitName": circuit.get("circuitName"),
                "locality": location.get("locality"),
                "country": location.get("country"),
                "lat": location.get("lat"),
                "long": location.get("long"),
                "url": circuit.get("url"),
            })

        return JSONResponse(content={"circuits": result})
    except Exception as e:
        print(f"Error fetching circuit data: {e}")
        return JSONResponse(content={"error": "Data unavailable"}, status_code=500)
    
@app.get("/standings")
async def get_standings(year: int, type: str):
    try:
        # Validate the type parameter
        if type not in ["driverStandings", "constructorStandings"]:
            return JSONResponse(content={"error": "Invalid type. Must be 'driverStandings' or 'constructorStandings'."})
        
        # Construct the API URL
        url = f"http://ergast.com/api/f1/{year}/{type}.json?limit=25"
        
        # Fetch the data from the API
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP errors

        data = response.json()

        # Extract standings information
        standings_list = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        
        if not standings_list:
            return JSONResponse(content={"error": f"No standings data found for year {year}"})

        # Prepare the results
        standings = []
        for item in standings_list[0].get(f"{type.split('Standings')[0].capitalize()}Standings", []):
            entry = {
                "Position": item.get("position"),
                "Points": item.get("points"),
                "Wins": item.get("wins"),
            }
            if type == "driverStandings":
                entry.update({
                    "Driver": {
                        "Name": f"{item['Driver']['givenName']} {item['Driver']['familyName']}",
                        "Nationality": item["Driver"]["nationality"],
                        "PermanentNumber": item["Driver"].get("permanentNumber"),
                        "Code": item["Driver"].get("code"),
                        "URL": item["Driver"].get("url"),
                    },
                    "Constructor": {
                        "Name": item["Constructors"][0]["name"],
                        "Nationality": item["Constructors"][0]["nationality"],
                        "URL": item["Constructors"][0].get("url"),
                    },
                })
            elif type == "constructorStandings":
                entry.update({
                    "Constructor": {
                        "Name": item["Constructor"]["name"],
                        "Nationality": item["Constructor"]["nationality"],
                        "URL": item["Constructor"].get("url"),
                    },
                })
            standings.append(entry)

        # Include metadata for the response
        result = {
            "Year": year,
            "Type": type,
            "Standings": standings,
        }

        return JSONResponse(content=result)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching standings data: {e}")
        return JSONResponse(content={"error": "Unable to fetch standings data."})

@app.get("/constructors")
async def get_constructors(
    year: int = None,
    round: int = None,
    circuit_id: str = None,
    driver_id: str = None,
    constructor_id: str = None,
    position: int = None,
    status_id: str = None,
    rank: int = None
):
    try:
        base_url = "http://ergast.com/api/f1"
        url = f"{base_url}/constructors.json"
        limit = 100
        offset = 0
        all_constructors = []

        # Build the base URL based on parameters
        if constructor_id:
            url = f"{base_url}/constructors/{constructor_id}.json"
        elif year and round:
            url = f"{base_url}/{year}/{round}/constructors.json"
        elif year:
            url = f"{base_url}/{year}/constructors.json"
        elif driver_id and circuit_id:
            url = f"{base_url}/drivers/{driver_id}/circuits/{circuit_id}/constructors.json"
        elif position:
            url = f"{base_url}/constructorStandings/{position}/constructors.json"
        elif circuit_id:
            url = f"{base_url}/circuits/{circuit_id}/constructors.json"
        elif driver_id:
            url = f"{base_url}/drivers/{driver_id}/constructors.json"
        elif rank:
            url = f"{base_url}/fastest/{rank}/constructors.json"
        elif status_id:
            url = f"{base_url}/status/{status_id}/constructors.json"

        while True:
            response = requests.get(f"{url}?limit={limit}&offset={offset}")
            if response.status_code != 200:
                return JSONResponse(content={"error": "Failed to fetch constructor data"}, status_code=500)

            data = response.json()
            constructors = data.get("MRData", {}).get("ConstructorTable", {}).get("Constructors", [])
            all_constructors.extend(constructors)

            # Check if all pages are fetched
            total = int(data.get("MRData", {}).get("total", 0))
            offset += limit
            if offset >= total:
                break

        # Transform the data
        result = []
        for constructor in all_constructors:
            result.append({
                "constructorId": constructor.get("constructorId"),
                "name": constructor.get("name"),
                "nationality": constructor.get("nationality"),
                "url": constructor.get("url"),
            })

        return JSONResponse(content={"constructors": result})
    except Exception as e:
        print(f"Error fetching constructor data: {e}")
        return JSONResponse(content={"error": "Data unavailable"}, status_code=500)

@app.get("/drivers")
async def get_drivers(
    year: int = None,
    round: int = None,
    circuit_id: str = None,
    constructor_id: str = None,
    position: int = None,
    driver_id: str = None,
    rank: int = None,
    status_id: str = None
):
    try:
        base_url = "http://ergast.com/api/f1"
        url = f"{base_url}/drivers.json"
        limit = 100
        offset = 0
        all_drivers = []

        # Build the URL based on the query parameters
        if driver_id:
            url = f"{base_url}/drivers/{driver_id}.json"
        elif year and round:
            url = f"{base_url}/{year}/{round}/drivers.json"
        elif year:
            url = f"{base_url}/{year}/drivers.json"
        elif constructor_id and circuit_id:
            url = f"{base_url}/constructors/{constructor_id}/circuits/{circuit_id}/drivers.json"
        elif constructor_id:
            url = f"{base_url}/constructors/{constructor_id}/drivers.json"
        elif circuit_id:
            url = f"{base_url}/circuits/{circuit_id}/drivers.json"
        elif position:
            url = f"{base_url}/results/{position}/drivers.json"
        elif rank:
            url = f"{base_url}/fastest/{rank}/drivers.json"
        elif status_id:
            url = f"{base_url}/status/{status_id}/drivers.json"

        # Paginate through results
        while True:
            response = requests.get(f"{url}?limit={limit}&offset={offset}")
            if response.status_code != 200:
                return JSONResponse(content={"error": "Failed to fetch driver data"}, status_code=500)

            data = response.json()
            drivers = data.get("MRData", {}).get("DriverTable", {}).get("Drivers", [])
            all_drivers.extend(drivers)

            # Check if all pages are fetched
            total = int(data.get("MRData", {}).get("total", 0))
            offset += limit
            if offset >= total:
                break

        # Transform the data
        result = []
        for driver in all_drivers:
            result.append({
                "driverId": driver.get("driverId"),
                "code": driver.get("code"),
                "url": driver.get("url"),
                "givenName": driver.get("givenName"),
                "familyName": driver.get("familyName"),
                "dateOfBirth": driver.get("dateOfBirth"),
                "nationality": driver.get("nationality"),
            })

        return JSONResponse(content={"drivers": result})
    except Exception as e:
        print(f"Error fetching driver data: {e}")
        return JSONResponse(content={"error": "Data unavailable"}, status_code=500)
