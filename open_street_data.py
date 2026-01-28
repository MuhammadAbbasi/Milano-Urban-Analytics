import osmnx as ox
import geopandas as gpd
import pandas as pd

# 1. Load your District Map
gdf = gpd.read_file("milan_districts_clean.geojson")

# 2. Define the tags you want to fetch
tags = {
    'leisure': 'park',
    'landuse': ['industrial', 'grass', 'forest'],
    'amenity': ['school', 'bar'] # Extra context
}

# 3. Function to fetch data for each district
def fetch_osm_features(polygon, tags):
    try:
        # Fetch geometries within the district polygon
        features = ox.features_from_polygon(polygon, tags)
        
        # Calculate areas (project to meters first)
        features_proj = features.to_crs(epsg=32632) 
        
        # Extract metrics
        park_area = features_proj[features_proj['leisure']=='park'].area.sum()
        ind_area = features_proj[features_proj['landuse']=='industrial'].area.sum()
        
        return park_area, ind_area
    except Exception as e:
        return 0, 0

# 4. Run the loop (This takes time!)
print("Fetching data from OpenStreetMap...")
results = []
for index, row in gdf.iterrows():
    park_m2, ind_m2 = fetch_osm_features(row.geometry, tags)
    
    # Calculate percentages
    district_area_m2 = row.geometry.area # Ensure this is in meters
    pct_green = (park_m2 / district_area_m2) * 100
    pct_industrial = (ind_m2 / district_area_m2) * 100
    
    results.append({
        'NIL_NAME': row['NIL_NAME'],
        'green_space_pct': pct_green,
        'industrial_pct': pct_industrial
    })
    print(f"Processed {row['NIL_NAME']}")

# 5. Save the new data
df_features = pd.DataFrame(results)
df_features.to_csv("milan_osm_features.csv", index=False)
print("Done! merged this with your main dataset.")