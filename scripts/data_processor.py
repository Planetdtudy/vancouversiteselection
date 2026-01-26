import gzip
import shutil
import geopandas as gpd
from pathlib import Path
#from config import WGS84_CRS
WGS84_CRS = "EPSG:4326"

class VancouverProcessor:
    def __init__(self, boundary_path, pop_path):
        self.boundary_path = boundary_path
        self.pop_path = pop_path  # This might be .gpkg.gz initially
        self.boundary = None
        self.clipped_pop = None

    def load_boundary(self):
            """Loads the boundary and turns the line into a solid shape."""
            print(f"Loading boundary: {self.boundary_path.name}")
            self.boundary = gpd.read_file(self.boundary_path)
            
            # --- THE MAGIC LINE ---
            # This fills the area inside your city line
            self.boundary['geometry'] = self.boundary.convex_hull
            
            if self.boundary.crs is None:
                self.boundary.set_crs("EPSG:4326", inplace=True)
            
            print("✓ Boundary loaded and converted to solid shape.")
            return self.boundary

    def clip_population(self):
            """Clips the national data using the city boundary."""
            if self.boundary is None:
                self.load_boundary()

            print("Clipping population data... (this might take a moment)")
            
            # 1. Load the data WITH the mask first
            # This only pulls the hexagons that hit your boundary
            self.clipped_pop = gpd.read_file(self.pop_path, mask=self.boundary, read_only=True)
            
            # 2. NOW check the CRS
            if self.clipped_pop.crs != self.boundary.crs:
                print(f"Aligning CRS: {self.clipped_pop.crs} -> {self.boundary.crs}")
                self.clipped_pop = self.clipped_pop.to_crs(self.boundary.crs)
                
            # 3. Clean: remove cells with 0 or negative population
            # (Make sure your column name is exactly 'population' in the source file)
            self.clipped_pop = self.clipped_pop[self.clipped_pop['population'] > 0]
            
            print(f"✓ Extraction complete: {len(self.clipped_pop)} hexagons found.")
            return self.clipped_pop