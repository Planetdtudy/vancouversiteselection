import gzip
import shutil
import geopandas as gpd
from pathlib import Path
from shapely.ops import unary_union, polygonize

WGS84_CRS = "EPSG:4326"

class VancouverProcessor:
    def __init__(self, boundary_path, pop_path):
        self.boundary_path = Path(boundary_path)
        self.pop_path = Path(pop_path)
        self.boundary = None
        self.clipped_pop = None

    def load_boundary(self):
        """polygonize method creates a "cookie cutter" that follows the actual shoreline"""
        print(f"Loading boundary: {self.boundary_path.name}")
        raw_gdf = gpd.read_file(self.boundary_path)
        
        # Ensure we are in WGS84 (Degrees)
        if raw_gdf.crs is None:
            raw_gdf.set_crs(WGS84_CRS, inplace=True)
        else:
            raw_gdf = raw_gdf.to_crs(WGS84_CRS)

        # Polygonize finds the "holes" inside the lines and fills them
        lines = raw_gdf.geometry.unary_union
        polygons = list(polygonize(lines))
        
        if polygons:
            self.boundary = gpd.GeoDataFrame(geometry=[unary_union(polygons)], crs=WGS84_CRS)
            print("City Lines are succesfully converted into a solid polygon.")
        else:
            # precision
            print("Lines are not closed. Attempting to close gaps with 1 m buffer...")
            self.boundary = gpd.GeoDataFrame(geometry=[lines.buffer(0.00001)], crs=WGS84_CRS)
        
        #print("Transforming boundary to EPSG:3857 (Meters) for population masking...")
        #self.boundary = self.boundary.to_crs("EPSG:3857")
        
        return self.boundary


    def clip_population(self):
            """Clips the national data using the solidified city boundary."""
            if self.boundary is None:
                self.load_boundary()

            print("Aligning boundary for spatial query...")
            
            #  Read just the metadata/header of the pop file to get its CRS
            print(gpd.read_file(self.pop_path, rows=0).crs)
            # Test 1: Your version (Reads 1 row of data)
            #meta_1 = gpd.read_file(self.pop_path, rows=1)
            #print(f"Rows=1 CRS: {meta_1.crs}")

            # Test 2: The metadata version (Reads 0 rows of data)
            #meta_0 = gpd.read_file(self.pop_path, rows=0)
            #print(f"Rows=0 CRS: {meta_0.crs}")

            pop_metadata = gpd.read_file(self.pop_path, rows=1)
            pop_crs = pop_metadata.crs
            mask_3857 = self.boundary.to_crs(pop_crs)
            # Project boundary to match the file on disk so the mask works
            #temp_mask = self.boundary.to_crs(pop_crs)

            print(f"Clipping population data using 3857 mask in {pop_crs}...")
            
            #  Masked read (Fast)
            self.clipped_pop = gpd.read_file(self.pop_path, mask=mask_3857)
            
            #Convert the found hexagons to degrees
            self.clipped_pop = self.clipped_pop.to_crs("EPSG:4326")
            #  Precise Clip (Geometric accuracy)
            # This ensures hexagons overlapping the boundary are cut perfectly
            #self.clipped_pop = gpd.clip(self.clipped_pop, mask_3857)
            
            #  Bring it back to WGS84 for your final output
            #self.clipped_pop = self.clipped_pop.to_crs(WGS84_CRS)
            #Final clip for precision
            self.clipped_pop = gpd.clip(self.clipped_pop, self.boundary)
            #  Filter for actual data
            self.clipped_pop = self.clipped_pop[self.clipped_pop['population'] > 0]
            
            print(f"✓ Extraction complete: {len(self.clipped_pop)} hexagons found.")
            return self.clipped_pop

   