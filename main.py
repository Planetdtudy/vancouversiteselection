# main.py
import os
from pathlib import Path
import scripts.config
import geopandas as gpd

# Load the file your main.py just saved
test_gdf = gpd.read_file(r"D:\GEO\vancouver-site-selection\output\vancouver_population_subset.geojson")

print(f"1. CRS of the file: {test_gdf.crs}")
print(f"2. First 2 coordinates: \n{test_gdf.geometry.head(2)}")
print(f"3. Total bounds: {test_gdf.total_bounds}")

print("--- DEBUG START ---")
print(f"File location: {scripts.config.__file__}")
print(f"Variables found: {[v for v in dir(scripts.config) if not v.startswith('__')]}")
print("--- DEBUG END ---")

config_path = Path(scripts.config.__file__)
content = config_path.read_text()

print("--- FILE CONTENT CHECK ---")
print(f"File size: {config_path.stat().st_size} bytes")
print("Full Content below:")
print(f"'{content}'")
print("--- END CHECK ---")
from scripts.config import  POPULATION_FILE, OUTPUT_DIR, BOUNDARY_FILE
from scripts.data_processor import VancouverProcessor

def main():
    print("--- Starting Vancouver Spatial ETL Pipeline ---")
    
    # 1. Ensure output directory exists
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory at: {OUTPUT_DIR}")

    # 2. Initialize the Processor (OOP)
    # We pass the paths from our config into the class
    processor = VancouverProcessor(
        boundary_path=BOUNDARY_FILE , 
        pop_path=POPULATION_FILE
    )

    try:
        print("--- Load the boundary ---")
 
        boundary = processor.load_boundary()
        print("Boundary loaded successfully.")

        # 4. Extract and Clip the data
        vancouver_pop = processor.clip_population()
        print(f"Successfully extracted {len(vancouver_pop)} population hexagons.")

        # Quick Check
        total_pop = vancouver_pop['population'].sum()
        top_5 = vancouver_pop.nlargest(5, 'population')

        print(f"\n--- Analysis for Vancouver ---")
        print(f"Total Population in Study Area: {total_pop:,.0f}")
        print(f"Average population per hexagon: {vancouver_pop['population'].mean():.1f}")
        print("\nTop 5 High-Density Hexagons:")
        print(top_5[['population', 'geometry']])


        print("--- Save the result---")
        output_path = OUTPUT_DIR / "vancouver_population_subset.geojson"
        vancouver_pop.to_file(output_path, driver='GeoJSON')
        
        print(f"--- Process Complete! ---")
        print(f"File saved to: {output_path}")

    except Exception as e:
        print(f"An error occurred during processing: {e}")

if __name__ == "__main__":
    main()