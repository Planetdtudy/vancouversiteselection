import folium
import geopandas as gpd
from pathlib import Path

# Use Path to make sure Windows doesn't get confused by slashes
base_path = Path(__file__).parent
data_path = base_path / "output" / "vancouver_population_subset.geojson"

# 1. Load data
gdf = gpd.read_file(data_path)

# 2. Create Map
m = folium.Map(location=[49.2827, -123.1207], zoom_start=12, tiles="CartoDB positron")

# 3. Add Heatmap (Choropleth)
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

# 4. Save
output_html = base_path / "output" / "vancouver_pop_map.html"
m.save(str(output_html))
print(f" Map generated! Open this file in your browser: {output_html}")