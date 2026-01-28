import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os

# --- CONFIGURATION: UPDATE THESE PATHS ---
# 1. Path to your District Map (NIL)
path_nil = "dataset/geo/milan_districts_clean.geojson"

# 2. Path to the DECAY folder (Unzip it first!)
# Example: "dataset/Milano_Edifici_aree_degrado"
path_degrado_folder = "dataset/geo/OpenData_ImmDegrado" 

# 3. Path to the HYDROGRAPHY folder (Unzip it first!)
# Example: "dataset/STRATO_04_Idrografia"
# dataset\
path_hydro_folder = "dataset/ambient/DBT2012_STRATO04_E0" 

# ---------------------------------------------------------
# HELPER: Find the Shapefile in a folder automatically
def find_shapefile(folder_path, hint=""):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".shp"):
                if hint in file: # strict filter
                    return os.path.join(root, file)
                if hint == "": # return first found
                    return os.path.join(root, file)
    return None

# ---------------------------------------------------------
# STEP 1: LOAD BASE MAP
print("Loading Districts...")
gdf_nil = gpd.read_file(path_nil)
gdf_nil = gdf_nil.to_crs(epsg=32632) # Convert to Meters

# ---------------------------------------------------------
# STEP 2: LOAD & MAP DECAY (SAFETY)
print("\n--- Processing Decay Data ---")
# Try to find the file automatically
file_degrado = find_shapefile(path_degrado_folder)

if file_degrado:
    print(f"Found Decay File: {file_degrado}")
    gdf_degrado = gpd.read_file(file_degrado)
    gdf_degrado = gdf_degrado.to_crs(epsg=32632)
    
    # Spatial Join
    print("Mapping decayed buildings to districts...")
    degrado_in_nil = gpd.sjoin(gdf_degrado, gdf_nil, how="inner", predicate="within")
    degrado_counts = degrado_in_nil.groupby('NIL_NAME').size().reset_index(name='n_decayed_buildings')
    
    # Merge
    gdf_master = gdf_nil.merge(degrado_counts, on='NIL_NAME', how='left')
    gdf_master['n_decayed_buildings'] = gdf_master['n_decayed_buildings'].fillna(0)
else:
    print("⚠️ ERROR: Could not find any .shp file in the Decay folder.")
    gdf_master = gdf_nil.copy()
    gdf_master['n_decayed_buildings'] = 0

# ---------------------------------------------------------
# STEP 3: LOAD & MAP HYDROGRAPHY (FLOODS)
print("\n--- Processing Hydrography Data ---")
# Look specifically for 'A040101' (Water Courses)
file_water = find_shapefile(path_hydro_folder, hint="A040101") 

# If specific file not found, try any shapefile
if not file_water:
    print("Specific 'A040101' not found, looking for any shapefile...")
    file_water = find_shapefile(path_hydro_folder)

if file_water:
    print(f"Found Water File: {file_water}")
    gdf_water = gpd.read_file(file_water)
    gdf_water = gdf_water.to_crs(epsg=32632)
    
    # Calculate Distance
    print("Calculating flood risk (distance to water)...")
    gdf_master['dist_to_water_m'] = gdf_master.geometry.centroid.apply(
        lambda x: gdf_water.distance(x).min()
    )
else:
    print("⚠️ ERROR: Could not find Hydrography .shp file.")
    gdf_master['dist_to_water_m'] = 9999

# ---------------------------------------------------------
# STEP 4: SAVE & PLOT
gdf_master.to_file("dataset/milan_districts_master_v3.geojson", driver="GeoJSON")
print("\nSUCCESS! Dataset v3 saved.")

# Simple Plot
fig, ax = plt.subplots(1, 2, figsize=(15, 8))
gdf_master.plot(column='n_decayed_buildings', cmap='OrRd', ax=ax[0], legend=True)
ax[0].set_title('Decay (Safety)')
gdf_master.plot(column='dist_to_water_m', cmap='Blues_r', ax=ax[1], legend=True)
ax[1].set_title('Flood Risk (Distance to Water)')
plt.show()