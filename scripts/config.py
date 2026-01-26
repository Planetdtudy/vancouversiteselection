
from pathlib import Path

# --- Project Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# --- File Names ---
#BOUNDARY_FILE = DATA_DIR / "city_bound_Vancouver.json"
BOUNDARY_FILE = DATA_DIR / "Vancouver_Fixed.geojson"
POPULATION_FILE = DATA_DIR / "kontur_population_CA_20231101.gpkg"

# --- GIS Constants (Fixes here) ---
# WGS84 is standard Lat/Long
WGS84_CRS = "EPSG:4326"  

# UTM Zone 10N is best for Vancouver area measurements (meters)
TARGET_CRS = "EPSG:32610"