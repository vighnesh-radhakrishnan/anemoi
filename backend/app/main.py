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
import matplotlib.lines as mlines
import requests
from matplotlib.colors import ListedColormap
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

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
            
        # Create figure with reduced size
        plt.rcParams['figure.figsize'] = [6, 6]
        fig, ax = plt.subplots(facecolor='black')
        ax.set_facecolor('black')
        
        # Define speed ranges for legend
        speed_min = speed.min()
        speed_max = speed.max()
        
        # Create F1-themed colormap for speed (yellow-orange-red)
        colors = ["#FFFF00", "#FF9900", "#e10600"]  # Yellow to orange to F1 red
        custom_cmap = LinearSegmentedColormap.from_list("f1_colors", colors)
        
        # Normalize speed for color mapping
        norm = plt.Normalize(speed_min, speed_max)
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        # Create line collection with custom coloring
        lc = LineCollection(segments, cmap=custom_cmap, norm=norm, linewidth=2.5)
        lc.set_array(speed)
        ax.add_collection(lc)
        
        # Set proper axis limits with adjusted padding
        padding = (max(x.max() - x.min(), y.max() - y.min()) * 0.1)
        ax.set_xlim(x.min() - padding, x.max() + padding)
        ax.set_ylim(y.min() - padding, y.max() + padding)
        
        # Set aspect ratio and turn off axis
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Create custom legend with speed ranges
        speed_levels = [speed_min, (speed_min + speed_max)/2, speed_max]
        legend_elements = [
            Line2D([0], [0], color=custom_cmap(norm(speed)), 
                  lw=2, label=f'{int(speed)} km/h')
            for speed in speed_levels
        ]
        
        # Place legend outside the plot on the right with white text
        legend = ax.legend(handles=legend_elements,
                 loc='center left',
                 bbox_to_anchor=(1.05, 0.5),
                 frameon=False,
                 title='Speed',
                 title_fontsize=8,
                 fontsize=6)
        for text in legend.get_texts():
            text.set_color('white')
        legend.get_title().set_color('white')
        
        # Save figure with optimized settings
        img_stream = io.BytesIO()
        plt.savefig(img_stream,
                   format='png',
                   dpi=150,
                   bbox_inches='tight',
                   facecolor='black',
                   edgecolor='none',
                   transparent=False,
                   pad_inches=0.2)
        plt.close()
        
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
    
@app.get("/track-dominance")
async def get_track_dominance_base64(
    year: int, 
    gp: str, 
    identifier: str, 
    driver1: str, 
    driver2: str
):
    try:
        # Load session data
        session = fastf1.get_session(year, gp, identifier)
        session.load(laps=True, telemetry=True, weather=False, messages=False, livedata=None)

        # Get fastest laps for both drivers
        fastest_lap_driver1 = session.laps.pick_drivers(driver1).pick_fastest()
        fastest_lap_driver2 = session.laps.pick_drivers(driver2).pick_fastest()

        if fastest_lap_driver1.empty or fastest_lap_driver2.empty:
            return JSONResponse(content={"error": "Fastest laps unavailable for one or both drivers"})

        # Get telemetry and add distance
        telemetry_driver1 = fastest_lap_driver1.get_telemetry().add_distance()
        telemetry_driver2 = fastest_lap_driver2.get_telemetry().add_distance()

        telemetry_driver1['Driver'] = driver1
        telemetry_driver2['Driver'] = driver2
        telemetry_drivers = pd.concat([telemetry_driver1, telemetry_driver2], ignore_index=True)

        # Calculate minisectors
        num_minisectors = 21
        total_distance = telemetry_drivers['Distance'].max()
        minisector_length = total_distance / num_minisectors

        telemetry_drivers['Minisector'] = telemetry_drivers['Distance'].apply(
            lambda dist: int((dist // minisector_length))
        )

        # Calculate average speed per minisector per driver
        average_speed = telemetry_drivers.groupby(['Minisector', 'Driver'])['Speed'].mean().reset_index()
        
        # Find fastest driver per minisector
        fastest_driver = average_speed.loc[average_speed.groupby(['Minisector'])['Speed'].idxmax()]
        fastest_driver = fastest_driver[['Minisector', 'Driver']].rename(columns={'Driver': 'Fastest_driver'})

        # Merge back to telemetry data
        telemetry_drivers = telemetry_drivers.merge(fastest_driver, on=['Minisector'])
        telemetry_drivers = telemetry_drivers.sort_values(by=['Distance'])

        # Generate the plot
        base64_img = plot_track_dominance_to_base64(
            telemetry_drivers, driver1, driver2, year, gp, identifier
        )
        
        if base64_img:
            return JSONResponse(content={
                "image_base64": base64_img,
                "driver1": driver1,
                "driver2": driver2,
                "gp": gp,
                "identifier": identifier,
                "year": year
            })
        else:
            return JSONResponse(content={
                "error": "Failed to generate track dominance plot",
                "driver1": driver1,
                "driver2": driver2,
                "gp": gp,
                "identifier": identifier,
                "year": year
            })
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={
            "error": "An error occurred while processing the data",
            "driver1": driver1,
            "driver2": driver2,
            "gp": gp,
            "identifier": identifier,
            "year": year
        })

    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={"error": f"An error occurred: {str(e)}"})

def plot_track_dominance_to_base64(telemetry_drivers, driver1, driver2, year, gp, session_type):
    try:
        # Convert driver names to integers for coloring
        telemetry_drivers.loc[telemetry_drivers['Fastest_driver'] == driver1, 'Fastest_driver_int'] = 1
        telemetry_drivers.loc[telemetry_drivers['Fastest_driver'] == driver2, 'Fastest_driver_int'] = 2
        
        # Prepare coordinates for plotting
        x = np.array(telemetry_drivers['X'].values)
        y = np.array(telemetry_drivers['Y'].values)
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        fastest_driver_array = telemetry_drivers['Fastest_driver_int'].to_numpy().astype(float)
        
        # Define better F1-themed colors for both drivers
        driver_colors = {
            driver1: "#e10600",  # F1 Red
            driver2: "#1f1f27"   # Dark navy/grey (from F1 design)
        }
        
        # Create custom colormap using the driver colors
        custom_cmap = ListedColormap([driver_colors[driver1], driver_colors[driver2]])
        
        # Create the plot with appropriate figure size
        plt.rcParams['figure.figsize'] = [6, 6]  # Smaller figure size
        fig, ax = plt.subplots(facecolor='black')
        ax.set_facecolor('black')  # Black background like F1 track maps
        
        # Create line collection with custom coloring
        lc_comp = LineCollection(segments, norm=plt.Normalize(1, 2), cmap=custom_cmap)
        lc_comp.set_array(fastest_driver_array)
        lc_comp.set_linewidth(2.5)  # Slightly thinner lines
        
        # Add the line collection to the plot
        ax.add_collection(lc_comp)
        
        # Set proper axis limits with adjusted padding
        padding = (max(x.max() - x.min(), y.max() - y.min()) * 0.1)
        ax.set_xlim(x.min() - padding, x.max() + padding)
        ax.set_ylim(y.min() - padding, y.max() + padding)
        
        # Set aspect ratio and turn off axis
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Add custom legend with consistent colors and white text on black background
        legend_elements = [
            mlines.Line2D([0], [0], color=driver_colors[driver1], lw=2, label=driver1),
            mlines.Line2D([0], [0], color=driver_colors[driver2], lw=2, label=driver2)
        ]
        
        # Place legend outside the plot on the right with white text
        legend = ax.legend(handles=legend_elements, 
                 loc='center left', 
                 bbox_to_anchor=(1.05, 0.5),
                 frameon=False)
        for text in legend.get_texts():
            text.set_color('white')
        
        # Save figure with adjusted layout and DPI
        img_stream = io.BytesIO()
        plt.savefig(img_stream, 
                   format='png', 
                   dpi=150,  # Lower DPI for smaller file size
                   bbox_inches='tight',
                   facecolor='black',
                   edgecolor='none',
                   transparent=False,  # Set to false for consistent rendering
                   pad_inches=0.2)
        plt.close()
        
        img_stream.seek(0)
        base64_img = base64.b64encode(img_stream.getvalue()).decode('utf-8')
        return base64_img
        
    except Exception as e:
        print(f"Error while plotting track dominance: {e}")
        return None
    
@app.get("/driver-comparison")
async def get_driver_comparison(year: int, gp: str, identifier: str, driver1: str, driver2: str, stint: int = 1):
    try:
        print(f"Starting driver comparison request for {driver1} vs {driver2} at {gp} {year}")
        
        # Load session with telemetry set to True
        session = fastf1.get_session(year, gp, identifier)
        # Need telemetry=True to access car data
        session.load(laps=True, telemetry=True, weather=False, messages=False)
        print("Session data loaded successfully")
        
        # Get laps data for both drivers
        laps_driver1 = session.laps.pick_drivers(driver1)  # Use pick_drivers instead of deprecated pick_driver
        laps_driver2 = session.laps.pick_drivers(driver2)
        
        # Check if we found any lap data before proceeding
        if laps_driver1.empty or laps_driver2.empty:
            print(f"No lap data found for drivers: {driver1}={len(laps_driver1)}, {driver2}={len(laps_driver2)}")
            return JSONResponse(content={"error": f"Not enough lap data for one or both drivers"})
        
        print(f"Found {len(laps_driver1)} laps for {driver1} and {len(laps_driver2)} laps for {driver2}")
        
        # Filter by stint if provided
        if stint is not None:
            laps_driver1 = laps_driver1.loc[laps_driver1['Stint'] == stint]
            laps_driver2 = laps_driver2.loc[laps_driver2['Stint'] == stint]
            print(f"After stint filtering: {len(laps_driver1)} laps for {driver1} and {len(laps_driver2)} laps for {driver2}")
        
        # Check if we have enough data after stint filtering
        if laps_driver1.empty or laps_driver2.empty:
            return JSONResponse(content={"error": f"Not enough lap data for one or both drivers in stint {stint}"})
        
        # Create race lap number
        laps_driver1 = laps_driver1.copy()
        laps_driver2 = laps_driver2.copy()
        laps_driver1.loc[:, 'RaceLapNumber'] = laps_driver1['LapNumber'] - 1
        laps_driver2.loc[:, 'RaceLapNumber'] = laps_driver2['LapNumber'] - 1
        
        # Skip telemetry and just create a simplified lap time comparison
        base64_img = lap_time_comparison_plot(
            laps_driver1, laps_driver2,
            driver1, driver2,
            session.event['EventName']
        )
        
        if base64_img:
            print("Successfully generated image")
            return JSONResponse(content={
                "image_base64": base64_img,
                "driver1": driver1,
                "driver2": driver2,
                "gp": gp,
                "identifier": identifier,
                "year": year,
                "stint": stint
            })
        else:
            print("Failed to generate image")
            return JSONResponse(content={"error": "Failed to generate comparison plot"})
                
    except Exception as e:
        print(f"Error in get_driver_comparison: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={"error": f"An error occurred: {str(e)}"})
    
def lap_time_comparison_plot(
    laps_driver1, laps_driver2, 
    driver1, driver2,
    event_name
):
    try:
        # Set figure size 
        plt.rcParams['figure.figsize'] = [10, 6]
        
        # Create a single panel plot - simpler and faster
        fig, ax = plt.subplots()
        fig.suptitle(f"{driver1} vs {driver2} Lap Time Comparison - {event_name}")
        
        # Convert timedelta to seconds if needed
        if 'LapTime' in laps_driver1.columns and not pd.api.types.is_numeric_dtype(laps_driver1['LapTime']):
            # Convert timedelta to seconds
            laps_driver1['LapTime_sec'] = laps_driver1['LapTime'].dt.total_seconds()
            laps_driver2['LapTime_sec'] = laps_driver2['LapTime'].dt.total_seconds()
            laptime_col = 'LapTime_sec'
        else:
            laptime_col = 'LapTime'
        
        # Plot lap times
        ax.plot(laps_driver1['RaceLapNumber'], laps_driver1[laptime_col], 'o-', label=driver1, color='purple')
        ax.plot(laps_driver2['RaceLapNumber'], laps_driver2[laptime_col], 'o-', label=driver2, color='green')
        
        # Add labels and legend
        ax.set_xlabel('Lap Number')
        ax.set_ylabel('Lap Time (seconds)')
        ax.legend(loc="upper right")
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add best lap markers
        try:
            d1_best_lap = laps_driver1[laptime_col].min()
            d2_best_lap = laps_driver2[laptime_col].min()
            d1_best_lap_idx = laps_driver1[laptime_col].idxmin()
            d2_best_lap_idx = laps_driver2[laptime_col].idxmin()
            
            d1_best_lap_num = laps_driver1.loc[d1_best_lap_idx, 'RaceLapNumber']
            d2_best_lap_num = laps_driver2.loc[d2_best_lap_idx, 'RaceLapNumber']
            
            # Annotate best laps
            ax.annotate(f'Best: {d1_best_lap:.3f}s', 
                        xy=(d1_best_lap_num, d1_best_lap),
                        xytext=(5, -15), 
                        textcoords='offset points',
                        color='purple',
                        fontweight='bold')
            
            ax.annotate(f'Best: {d2_best_lap:.3f}s', 
                        xy=(d2_best_lap_num, d2_best_lap),
                        xytext=(5, 15), 
                        textcoords='offset points',
                        color='green',
                        fontweight='bold')
            
            # Highlight best laps
            ax.plot(d1_best_lap_num, d1_best_lap, 'o', ms=12, mfc='none', mec='purple', mew=2)
            ax.plot(d2_best_lap_num, d2_best_lap, 'o', ms=12, mfc='none', mec='green', mew=2)
            
        except Exception as e:
            print(f"Error highlighting best laps: {e}")
            
        # Generate the base64 image
        img_stream = io.BytesIO()
        plt.savefig(img_stream, format='png', dpi=100, bbox_inches='tight')  # Use even lower DPI
        plt.close()
        
        img_stream.seek(0)
        base64_img = base64.b64encode(img_stream.getvalue()).decode('utf-8')
        return base64_img
        
    except Exception as e:
        print(f"Error while plotting lap time comparison: {e}")
        import traceback
        traceback.print_exc()
        return None
        
def plot_driver_comparison_to_base64(
    laps_driver1, laps_driver2, 
    summarized_distance, 
    lap_telemetry_driver1, lap_telemetry_driver2,
    surrounding_laps,
    driver1, driver2,
    closest_lap,
    event_name
):
    try:
        # Set figure size for the multi-panel plot
        plt.rcParams['figure.figsize'] = [15, 15]
        
        # Create subplots - 5 panels as in the example
        fig, ax = plt.subplots(5, sharex=False)
        fig.suptitle(f"{driver1} vs {driver2} comparison - {event_name}")
        
        # Check for LapTime data type and convert if needed
        if 'LapTime' in laps_driver1.columns and not pd.api.types.is_numeric_dtype(laps_driver1['LapTime']):
            # Convert timedelta to seconds
            laps_driver1['LapTime_sec'] = laps_driver1['LapTime'].dt.total_seconds()
            laps_driver2['LapTime_sec'] = laps_driver2['LapTime'].dt.total_seconds()
            laptime_col = 'LapTime_sec'
        else:
            laptime_col = 'LapTime'
        
        # Panel 1: Lap times comparison
        ax[0].plot(laps_driver1['RaceLapNumber'], laps_driver1[laptime_col], label=driver1, color='purple')
        ax[0].plot(laps_driver2['RaceLapNumber'], laps_driver2[laptime_col], label=driver2, color='green')
        ax[0].set(ylabel='Laptime (s)')
        ax[0].legend(loc="upper center")
        
        # Add circles to highlight specific areas of interest
        try:
            if closest_lap > 2 and closest_lap < max(laps_driver1['RaceLapNumber'].max(), laps_driver2['RaceLapNumber'].max()) - 2:
                # Find lap times for the closest lap
                d1_laptime = laps_driver1.loc[laps_driver1['RaceLapNumber'] == closest_lap, laptime_col]
                d2_laptime = laps_driver2.loc[laps_driver2['RaceLapNumber'] == closest_lap, laptime_col]
                
                if not d1_laptime.empty and not d2_laptime.empty:
                    # Add a circle to highlight the closest battle area
                    x_center = closest_lap
                    y_center = np.mean([d1_laptime.iloc[0], d2_laptime.iloc[0]])
                    radius = 0.5
                    circle = plt.Circle((x_center, y_center), radius, fill=False, edgecolor='white', linewidth=2)
                    ax[0].add_patch(circle)
        except Exception as e:
            print(f"Error adding lap time highlight: {e}")
        
        # Panel 2: Distance between drivers
        ax[1].plot(summarized_distance['Lap'], summarized_distance['Mean'], label='Mean', color='red')
        ax[1].plot(summarized_distance['Lap'], summarized_distance['Median'], label='Median', color='grey')
        ax[1].set(ylabel='Distance (meters)')
        ax[1].legend(loc="upper center")
        
        # Add circle to highlight distance in interesting laps
        try:
            if closest_lap > 2 and closest_lap < summarized_distance['Lap'].max() - 2:
                # Find the median distance for the closest lap
                closest_median = summarized_distance.loc[summarized_distance['Lap'] == closest_lap, 'Median']
                
                if not closest_median.empty:
                    # Add a circle to highlight the closest distance
                    x_center = closest_lap
                    y_center = closest_median.iloc[0]
                    radius = 0.5
                    circle = plt.Circle((x_center, y_center), radius, fill=False, edgecolor='white', linewidth=2)
                    ax[1].add_patch(circle)
        except Exception as e:
            print(f"Error adding distance highlight: {e}")
        
        # Panel 3: Distance to driver ahead across laps
        ax[2].set_title(f"Distance to {driver1} (m)")
        line_styles = ['dotted', 'solid', 'dotted', 'dashed']
        colors = ['grey', 'magenta', 'white', 'lightgrey']
        
        for i, lap_data in enumerate(surrounding_laps):
            lap_num = lap_data['lap']
            distance_df = lap_data['distance_data']
            
            if not distance_df.empty:
                label = f"Lap {lap_num}"
                if lap_num == closest_lap:
                    linestyle = 'solid'
                    color = 'magenta'
                else:
                    linestyle = line_styles[i % len(line_styles)]
                    color = colors[i % len(colors)]
                
                ax[2].plot(
                    distance_df['Distance'], 
                    distance_df['DistanceToDriverAhead'],
                    label=label,
                    linestyle=linestyle,
                    color=color
                )
        
        ax[2].legend(loc="lower right")
        ax[2].set(ylabel=f'Distance to {driver1}')
        
        # Check if required columns exist
        required_columns = ['Distance', 'Speed', 'Throttle']
        d1_cols = all(col in lap_telemetry_driver1.columns for col in required_columns)
        d2_cols = all(col in lap_telemetry_driver2.columns for col in required_columns)
        
        if not d1_cols or not d2_cols:
            print("Missing required telemetry columns")
            # Use simpler plots if data is missing
            ax[3].text(0.5, 0.5, "Telemetry data incomplete", 
                       horizontalalignment='center', verticalalignment='center')
            ax[4].text(0.5, 0.5, "Telemetry data incomplete", 
                       horizontalalignment='center', verticalalignment='center')
        else:
            # Panel 4: Speed comparison for the closest lap
            ax[3].set_title(f"Lap {closest_lap} telemetry")
            ax[3].plot(lap_telemetry_driver1['Distance'], lap_telemetry_driver1['Speed'], label=driver1, color='purple')
            ax[3].plot(lap_telemetry_driver2['Distance'], lap_telemetry_driver2['Speed'], label=driver2, color='green')
            ax[3].set(ylabel='Speed')
            ax[3].legend(loc="lower right")
            
            # Panel 5: Throttle comparison
            ax[4].plot(lap_telemetry_driver1['Distance'], lap_telemetry_driver1['Throttle'], label=driver1, color='purple')
            ax[4].plot(lap_telemetry_driver2['Distance'], lap_telemetry_driver2['Throttle'], label=driver2, color='green')
            ax[4].set(ylabel='Throttle', xlabel='Distance')
            
            # Highlight key differences in throttle application
            try:
                max_dist = min(lap_telemetry_driver1['Distance'].max(), lap_telemetry_driver2['Distance'].max())
                for dist_pct in [0.1, 0.3, 0.5, 0.7, 0.9]:  # Check at various points along the lap
                    dist = max_dist * dist_pct
                    
                    # Find closest points in each dataset
                    d1_idx = (lap_telemetry_driver1['Distance'] - dist).abs().idxmin()
                    d2_idx = (lap_telemetry_driver2['Distance'] - dist).abs().idxmin()
                    
                    d1_throttle = lap_telemetry_driver1.loc[d1_idx, 'Throttle']
                    d2_throttle = lap_telemetry_driver2.loc[d2_idx, 'Throttle']
                    
                    if abs(d1_throttle - d2_throttle) > 20:  # If throttle difference is significant
                        circle = plt.Circle((dist, min(d1_throttle, d2_throttle) + abs(d1_throttle - d2_throttle)/2), 
                                          max_dist/20, fill=False, edgecolor='white', linewidth=2)
                        ax[4].add_patch(circle)
            except Exception as e:
                print(f"Error highlighting throttle differences: {e}")
        
        # Hide x labels and tick labels for top plots and y ticks for right plots
        for a in ax.flat:
            a.label_outer()
        
        # Generate the base64 image
        img_stream = io.BytesIO()
        plt.savefig(img_stream, format='png', dpi=300, bbox_inches='tight')
        plt.close()
        
        img_stream.seek(0)
        base64_img = base64.b64encode(img_stream.getvalue()).decode('utf-8')
        return base64_img
        
    except Exception as e:
        print(f"Error while plotting driver comparison: {e}")
        import traceback
        traceback.print_exc()
        return None