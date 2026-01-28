import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import json
from shapely.geometry import shape
import math

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

# 2. Prepare Data
# Sort alphabetically for easy lookup
gdf = gdf.sort_values('NIL_NAME').reset_index(drop=True)
gdf['Map_ID'] = gdf.index + 1

# 3. Setup Plot
fig = plt.figure(figsize=(24, 16))
gs = fig.add_gridspec(1, 2, width_ratios=[3, 1]) 

ax_map = fig.add_subplot(gs[0])
ax_legend = fig.add_subplot(gs[1])

# --- DRAW MAP ---
# Use 'nipy_spectral' for high contrast between many categories
gdf.plot(column='Map_ID', ax=ax_map, cmap='nipy_spectral', edgecolor='white', linewidth=0.5)

# Annotate with Numbers
for idx, row in gdf.iterrows():
    cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
    # Add number with black outline for readability
    ax_map.annotate(text=str(row['Map_ID']), xy=(cx, cy),
                    horizontalalignment='center', verticalalignment='center',
                    fontsize=9, color='white', fontweight='bold',
                    path_effects=[pe.withStroke(linewidth=2, foreground="black")])

ax_map.set_title("Map of Milan: 88 NILs (Numbered)", fontsize=24, fontweight='bold')
ax_map.axis('off')

# --- DRAW LEGEND ---
ax_legend.axis('off')

# Create legend items in single column
items = [f"{row['Map_ID']}. {row['NIL_NAME']}" for idx, row in gdf.iterrows()]
legend_text = "\n".join(items)

# Place text
ax_legend.text(0.05, 0.99, legend_text, verticalalignment='top', fontsize=10, family='monospace')

plt.tight_layout()
plt.savefig("milan_nil_map_numbered_med.png", dpi=500, bbox_inches='tight')