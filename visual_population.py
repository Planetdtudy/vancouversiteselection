import folium
import geopandas as gpd
from pathlib import Path

base_path = Path(__file__).parent
data_path = base_path / "output" / "vancouver_population_subset.geojson"

# Load data
gdf = gpd.read_file(data_path)

# Create Map
m = folium.Map(location=[49.2827, -123.1207], zoom_start=12, tiles="CartoDB positron")

# Add Heatmap 
folium.Choropleth(
    geo_data=gdf,
    name="Population",
    data=gdf,
    columns=[gdf.index, "population"], 
    key_on="feature.id",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="People per Hexagon"
).add_to(m)

# Save
output_html = base_path / "output" / "vancouver_pop_map.html"
m.save(str(output_html))
print(f" Map generated! Open this file in your browser: {output_html}")