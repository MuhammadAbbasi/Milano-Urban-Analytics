import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import json
from shapely.geometry import shape

# 1. Load Data
with open("dataset/milan_districts_master_v3.geojson", "r") as f:
    data = json.load(f)

# Convert to GeoDataFrame
features = data['features']
rows = []
for feat in features:
    props = feat['properties']
    geom = shape(feat['geometry'])
    props['geometry'] = geom
    rows.append(props)
gdf = gpd.GeoDataFrame(rows)

# 2. Define Zones based on NIL Names
# Current Area C (Historic Center)
current_area_c = [
    'DUOMO', 'BRERA', 'GUASTALLA', 'PORTA VIGENTINA', 
    'TICINESE', 'MAGENTA - S. VITTORE', 'PARCO SEMPIONE'
]

# Proposed Expansion (The "Gilded Cage" - High Income/High Traffic neighbors)
proposed_expansion = [
    'BUENOS AIRES - PORTA VENEZIA', 'PORTA ROMANA', 'PAGANO', 
    'SARPI', 'STAZIONE CENTRALE - PONTE SEVESO', 'TRE TORRI', 
    'ISOLA', 'CITY LIFE', 'XXII MARZO'
]

# Assign Categories
def assign_zone(name):
    name = name.upper().strip()
    if any(x in name for x in current_area_c):
        return 'Current Area C'
    elif any(x in name for x in proposed_expansion):
        return 'Proposed Expansion'
    else:
        return 'Standard Zone'

gdf['Zone_Type'] = gdf['NIL_NAME'].apply(assign_zone)

# 3. Plotting
fig, ax = plt.subplots(figsize=(12, 12))

# Plot Base (Standard Zone)
gdf[gdf['Zone_Type'] == 'Standard Zone'].plot(
    ax=ax, color='#f0f0f0', edgecolor='#d9d9d9'
)

# Plot Current Area C (Blue)
gdf[gdf['Zone_Type'] == 'Current Area C'].plot(
    ax=ax, color='#3498db', edgecolor='black', alpha=0.8, label='Current Area C'
)

# Plot Proposed Expansion (Orange with Stripes)
gdf[gdf['Zone_Type'] == 'Proposed Expansion'].plot(
    ax=ax, color='#e67e22', edgecolor='black', alpha=0.6, hatch='//', label='Proposed Expansion'
)

# Custom Legend
legend_elements = [
    mpatches.Patch(facecolor='#3498db', edgecolor='black', label='Current Area C (Historic Core)'),
    mpatches.Patch(facecolor='#e67e22', edgecolor='black', alpha=0.6, hatch='//', label='Proposed Expansion (Gilded Cage)')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=12)

# Annotate key areas
for idx, row in gdf.iterrows():
    if row['Zone_Type'] != 'Standard Zone':
        # Shorten name for map
        label = row['NIL_NAME'].split(" - ")[0]
        if label in ['DUOMO', 'BRERA', 'BUENOS AIRES', 'PAGANO']:
            plt.annotate(text=label, xy=(row.geometry.centroid.x, row.geometry.centroid.y),
                         horizontalalignment='center', fontsize=8, fontweight='bold')

plt.title("Strategic Expansion of Restricted Traffic Zones", fontsize=18, fontweight='bold')
plt.axis('off')

plt.savefig("milan_area_c_expansion.png", dpi=600, bbox_inches='tight')
print("Map saved as 'milan_area_c_expansion.png'")