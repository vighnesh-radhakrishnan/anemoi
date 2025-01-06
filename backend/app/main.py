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

# Define the route for fetching winners
@app.get("/winners/{year}")
async def get_winners(year: int):
    # Fetch actual data using fastf1 (example, adjust based on available methods)
    try:
        race = fastf1.get_race(year, round=1)  # Example call to get race data for the first round of a given year
        wdc = race.winner.driver.full_name  # Example to get the winner's name
        wcc = race.winner.team.name  # Example to get the winner's team name
    except Exception as e:
        wdc = "Data unavailable"
        wcc = "Data unavailable"
        print(f"Error fetching data: {e}")

    return JSONResponse(content={"year": year, "wdc": wdc, "wcc": wcc})
