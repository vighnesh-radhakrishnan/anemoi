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

        # Create figure with same size as track dominance
        plt.rcParams['figure.figsize'] = [8, 8]
        fig, ax = plt.subplots(facecolor='none')
        ax.set_facecolor('none')

        # Define speed ranges for legend
        speed_min = speed.min()
        speed_max = speed.max()
        speed_range = speed_max - speed_min
        
        # Create custom colormap for speed
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]  # Blue to Orange to Green
        custom_cmap = LinearSegmentedColormap.from_list("custom", colors)

        # Normalize speed for color mapping
        norm = plt.Normalize(speed_min, speed_max)
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        # Create line collection with custom coloring
        lc = LineCollection(segments, cmap=custom_cmap, norm=norm, linewidth=3)
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

        # Place legend outside the plot on the right
        ax.legend(handles=legend_elements,
                 loc='center left',
                 bbox_to_anchor=(1.05, 0.5),
                 frameon=False,
                 title='Speed',
                 title_fontsize=8,
                 fontsize=6)

        # Save figure with same settings as track dominance
        img_stream = io.BytesIO()
        plt.savefig(img_stream,
                   format='png',
                   dpi=300,
                   bbox_inches='tight',
                   facecolor='none',
                   edgecolor='none',
                   transparent=True,
                   pad_inches=0.1)
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
        
        # Define consistent colors for both drivers
        driver_colors = {
            driver1: "#1f77b4",  # Blue
            driver2: "#ff7f0e"   # Orange
        }
        
        # Create custom colormap using the driver colors
        custom_cmap = ListedColormap([driver_colors[driver1], driver_colors[driver2]])
        
        # Create the plot with adjusted figure size
        plt.rcParams['figure.figsize'] = [8, 8]  # Make figure more compact and square
        fig, ax = plt.subplots()
        
        # Create line collection with custom coloring
        lc_comp = LineCollection(segments, norm=plt.Normalize(1, 2), cmap=custom_cmap)
        lc_comp.set_array(fastest_driver_array)
        lc_comp.set_linewidth(3)  # Slightly reduced line width
        
        # Add the line collection to the plot
        ax.add_collection(lc_comp)
        
        # Set proper axis limits with adjusted padding
        padding = (max(x.max() - x.min(), y.max() - y.min()) * 0.1)  # 10% padding
        ax.set_xlim(x.min() - padding, x.max() + padding)
        ax.set_ylim(y.min() - padding, y.max() + padding)
        
        # Set aspect ratio and turn off axis
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Add custom legend with consistent colors
        legend_elements = [
            mlines.Line2D([0], [0], color=driver_colors[driver1], lw=2, label=driver1),
            mlines.Line2D([0], [0], color=driver_colors[driver2], lw=2, label=driver2)
        ]
        
        # Place legend outside the plot on the right
        ax.legend(handles=legend_elements, 
                 loc='center left', 
                 bbox_to_anchor=(1.05, 0.5),
                 frameon=False)
    
        
        # Save figure with adjusted layout
        img_stream = io.BytesIO()
        plt.savefig(img_stream, 
                   format='png', 
                   dpi=300, 
                   bbox_inches='tight',  # Tight layout
                   facecolor='none',    # White background
                   edgecolor='none',
                   transparent=True,  # Non-transparent background
                   pad_inches=0.1)       # Add padding around the plot
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
        # Load the session data
        session = fastf1.get_session(year, gp, identifier)
        session.load(laps=True, telemetry=True, weather=False, messages=False)
        
        # Get laps for both drivers
        laps_driver1 = session.laps.pick_driver(driver1)
        laps_driver2 = session.laps.pick_driver(driver2)
        
        # Filter by stint if provided
        if stint is not None:
            laps_driver1 = laps_driver1.loc[laps_driver1['Stint'] == stint]
            laps_driver2 = laps_driver2.loc[laps_driver2['Stint'] == stint]
        
        # Check if we have enough data
        if laps_driver1.empty or laps_driver2.empty:
            return JSONResponse(content={"error": f"Not enough lap data for one or both drivers in stint {stint}"})
        
        # Create race lap number (subtracting 1 to account for formation lap)
        # Use proper pandas method to avoid SettingWithCopyWarning
        laps_driver1 = laps_driver1.copy()
        laps_driver2 = laps_driver2.copy()
        laps_driver1.loc[:, 'RaceLapNumber'] = laps_driver1['LapNumber'] - 1
        laps_driver2.loc[:, 'RaceLapNumber'] = laps_driver2['LapNumber'] - 1
        
        # Get driver numbers directly from lap data instead of session.get_driver
        try:
            driver1_number = laps_driver1['DriverNumber'].iloc[0]
            driver2_number = laps_driver2['DriverNumber'].iloc[0]
        except:
            return JSONResponse(content={"error": f"Could not get driver numbers for {driver1} and {driver2}"})
        
        # Determine which driver is ahead based on position
        ahead_driver = driver1
        behind_driver = driver2
        ahead_driver_number = driver1_number
        behind_driver_number = driver2_number
        ahead_laps = laps_driver1
        behind_laps = laps_driver2
        
        # Try to determine who's ahead based on position or lap times
        try:
            d1_median_time = laps_driver1['LapTime'].median()
            d2_median_time = laps_driver2['LapTime'].median()
            
            if d2_median_time < d1_median_time:
                ahead_driver = driver2
                behind_driver = driver1
                ahead_driver_number = driver2_number
                behind_driver_number = driver1_number
                ahead_laps = laps_driver2
                behind_laps = laps_driver1
        except:
            pass  # If this fails, stick with the default assignment
        
        # Process distance data
        full_distance_data = pd.DataFrame()
        summarized_distance_data = pd.DataFrame()
        
        for _, lap in behind_laps.iterrows():
            try:
                # Get the lap telemetry with car data
                tel = lap.get_telemetry().add_distance()
                
                # Check if telemetry has driver ahead data
                if 'DriverAhead' in tel.columns:
                    tel = tel.add_driver_ahead()
                    # Filter to only include data where driver ahead is our ahead_driver
                    tel_filtered = tel[tel['DriverAhead'] == str(ahead_driver_number)]
                    
                    if len(tel_filtered) > 0:
                        # Full distance data
                        lap_telemetry = tel_filtered[['Distance', 'DistanceToDriverAhead']].copy()
                        lap_telemetry.loc[:, 'Lap'] = lap['RaceLapNumber']
                        full_distance_data = pd.concat([full_distance_data, lap_telemetry])
                        
                        # Summarized distance data
                        distance_mean = np.nanmean(tel_filtered['DistanceToDriverAhead'])
                        distance_median = np.nanmedian(tel_filtered['DistanceToDriverAhead'])
                        new_row = pd.DataFrame({
                            'Lap': [lap['RaceLapNumber']],
                            'Mean': [distance_mean],
                            'Median': [distance_median]
                        })
                        summarized_distance_data = pd.concat([summarized_distance_data, new_row])
            except Exception as e:
                print(f"Error processing lap {lap['RaceLapNumber']}: {e}")
                continue
        
        # If we couldn't get distance data, return an error
        if full_distance_data.empty or summarized_distance_data.empty:
            return JSONResponse(content={
                "error": f"Could not calculate distance between {driver1} and {driver2}. They may not have been close enough on track."
            })
        
        # Find the lap with the smallest median distance
        summarized_distance_data = summarized_distance_data.reset_index(drop=True)
        closest_lap_idx = summarized_distance_data['Median'].idxmin()
        closest_lap = int(summarized_distance_data.loc[closest_lap_idx, 'Lap'])
        
        # Get detailed telemetry for the closest lap
        try:
            ahead_lap = ahead_laps[ahead_laps['RaceLapNumber'] == closest_lap].iloc[0]
            behind_lap = behind_laps[behind_laps['RaceLapNumber'] == closest_lap].iloc[0]
            
            lap_telemetry_ahead = ahead_lap.get_telemetry().add_distance()
            lap_telemetry_behind = behind_lap.get_telemetry().add_distance()
        except:
            # Fallback to using the fastest lap if we can't get the closest lap
            lap_telemetry_ahead = ahead_laps.pick_fastest().get_telemetry().add_distance()
            lap_telemetry_behind = behind_laps.pick_fastest().get_telemetry().add_distance()
        
        # Get distance data for a few laps around the closest lap
        surrounding_laps = []
        for lap_num in range(closest_lap - 1, closest_lap + 3):
            lap_data = full_distance_data.loc[full_distance_data['Lap'] == lap_num]
            if not lap_data.empty:
                surrounding_laps.append({
                    'lap': lap_num,
                    'distance_data': lap_data.reset_index(drop=True)
                })
        
        # Generate the comparison plots
        base64_img = plot_driver_comparison_to_base64(
            laps_driver1, laps_driver2,
            summarized_distance_data,
            lap_telemetry_ahead, lap_telemetry_behind,
            surrounding_laps,
            driver1, driver2,
            closest_lap,
            session.event['EventName']
        )
        
        if base64_img:
            return JSONResponse(content={
                "image_base64": base64_img,
                "driver1": driver1,
                "driver2": driver2,
                "gp": gp,
                "identifier": identifier,
                "year": year,
                "stint": stint,
                "closest_lap": closest_lap
            })
        else:
            return JSONResponse(content={"error": "Failed to generate comparison plot"})
    
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={"error": f"An error occurred: {str(e)}"})
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
        
        # Panel 1: Lap times comparison
        ax[0].plot(laps_driver1['RaceLapNumber'], laps_driver1['LapTime'], label=driver1, color='purple')
        ax[0].plot(laps_driver2['RaceLapNumber'], laps_driver2['LapTime'], label=driver2, color='green')
        ax[0].set(ylabel='Laptime')
        ax[0].legend(loc="upper center")
        
        # Add circles to highlight specific areas of interest
        if closest_lap > 2 and closest_lap < max(laps_driver1['RaceLapNumber'].max(), laps_driver2['RaceLapNumber'].max()) - 2:
            # Add a circle to highlight the closest battle area
            x_center = closest_lap
            y_center = np.mean([
                laps_driver1.loc[laps_driver1['RaceLapNumber']==closest_lap, 'LapTime'].iloc[0],
                laps_driver2.loc[laps_driver2['RaceLapNumber']==closest_lap, 'LapTime'].iloc[0]
            ])
            radius = 0.5
            circle = plt.Circle((x_center, y_center), radius, fill=False, edgecolor='white', linewidth=2)
            ax[0].add_patch(circle)
        
        # Panel 2: Distance between drivers
        ax[1].plot(summarized_distance['Lap'], summarized_distance['Mean'], label='Mean', color='red')
        ax[1].plot(summarized_distance['Lap'], summarized_distance['Median'], label='Median', color='grey')
        ax[1].set(ylabel='Distance (meters)')
        ax[1].legend(loc="upper center")
        
        # Add circle to highlight distance in interesting laps
        if closest_lap > 2 and closest_lap < summarized_distance['Lap'].max() - 2:
            # Add a circle to highlight the closest distance
            x_center = closest_lap
            y_center = summarized_distance.loc[summarized_distance['Lap']==closest_lap, 'Median'].iloc[0]
            radius = 0.5
            circle = plt.Circle((x_center, y_center), radius, fill=False, edgecolor='white', linewidth=2)
            ax[1].add_patch(circle)
        
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
        ax[2].set(ylabel='Distance to driver1')
        
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
        for dist in range(0, int(lap_telemetry_driver1['Distance'].max()), int(lap_telemetry_driver1['Distance'].max() / 5)):
            d1_throttle = lap_telemetry_driver1.loc[lap_telemetry_driver1['Distance'] > dist].iloc[0]['Throttle']
            d2_throttle = lap_telemetry_driver2.loc[lap_telemetry_driver2['Distance'] > dist].iloc[0]['Throttle']
            
            if abs(d1_throttle - d2_throttle) > 20:  # If throttle difference is significant
                circle = plt.Circle((dist, min(d1_throttle, d2_throttle) + abs(d1_throttle - d2_throttle)/2), 
                                   50, fill=False, edgecolor='white', linewidth=2)
                ax[4].add_patch(circle)
        
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
        return None