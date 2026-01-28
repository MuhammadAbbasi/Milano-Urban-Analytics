import pandas as pd
import geopandas as gpd
import json
import matplotlib.pyplot as plt
import seaborn as sns

# --- STEP 1: LOAD THE DATA ---
# Load the "Master File" with all the data
df = pd.read_csv("milan_districts_data.csv")

# Load the Map Shapes (using json to be safe)
with open("milan_districts_clean.geojson", 'r') as f:
    geojson_data = json.load(f)
gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
gdf.set_crs(epsg=4326, inplace=True) # Ensure it uses Latitude/Longitude

# --- STEP 2: MERGE DATA WITH MAP ---
# Clean up names to ensure they match (uppercase, no spaces)
df['district_name'] = df['district_name'].str.upper().str.strip()
gdf['NIL_NAME'] = gdf['NIL_NAME'].str.upper().str.strip()

# Merge: This adds the data (income, pollution) to the map shapes
merged = gdf.merge(df, left_on='NIL_NAME', right_on='district_name', how='left')

# --- STEP 3: FIGURE 1 - THE COMPARISON MAPS ---
fig, ax = plt.subplots(1, 2, figsize=(24, 12))

# Subplot A: Pollution Map
merged.plot(column='avg_pm25', ax=ax[0], legend=True, 
            cmap='OrRd', # Orange-Red helps visualize "Danger/Heat"
            edgecolor='black', linewidth=0.3,
            legend_kwds={'label': "Average PM2.5 (µg/m³)", 'orientation': "horizontal"})
ax[0].set_title("Map A: Air Pollution Exposure", fontsize=20)
ax[0].axis('off')

# Subplot B: Crime Map
merged.plot(column='crime_rate', ax=ax[1], legend=True, 
            cmap='viridis', # Distinct color scheme for contrast
            edgecolor='black', linewidth=0.3,
            legend_kwds={'label': "Crime Rate (per 1,000 residents)", 'orientation': "horizontal"})
ax[1].set_title("Map B: Crime Density", fontsize=20)
ax[1].axis('off')

plt.suptitle("Spatial Correlation: Pollution vs. Crime in Milan", fontsize=24)
plt.tight_layout()
plt.show()

# --- STEP 4: FIGURE 2 - ENVIRONMENTAL JUSTICE SCATTER PLOT ---
plt.figure(figsize=(14, 10))

# Create the Scatter Plot
# X=Income (Wealth), Y=Pollution (Health), Size=Crime (Safety)
scatter = sns.scatterplot(data=df, 
                          x='median_income', 
                          y='avg_pm25', 
                          size='crime_rate', 
                          hue='crime_rate',
                          palette='viridis', 
                          sizes=(100, 1000), # Make bubbles big enough to read
                          alpha=0.8,
                          edgecolor='black')

# Add Labels and Guidelines
plt.title("Environmental Justice Analysis: The 'Wealth Shield' Effect", fontsize=18)
plt.xlabel("Median Neighborhood Income (€)", fontsize=14)
plt.ylabel("Air Pollution (PM2.5 Level)", fontsize=14)
plt.axvline(x=df['median_income'].mean(), color='red', linestyle='--', alpha=0.5, label='Avg Income')
plt.axhline(y=df['avg_pm25'].mean(), color='red', linestyle='--', alpha=0.5, label='Avg Pollution')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Crime Rate")
plt.grid(True, linestyle='--', alpha=0.3)

# Label the most interesting districts (Outliers)
# 1. The Richest District
richest = df.loc[df['median_income'].idxmax()]
plt.text(richest['median_income'], richest['avg_pm25'], richest['district_name'], fontsize=10, fontweight='bold')

# 2. The Most Dangerous District
most_crime = df.loc[df['crime_rate'].idxmax()]
plt.text(most_crime['median_income'], most_crime['avg_pm25'], most_crime['district_name'], fontsize=10, fontweight='bold')

# 3. The Most Polluted District
most_polluted = df.loc[df['avg_pm25'].idxmax()]
plt.text(most_polluted['median_income'], most_polluted['avg_pm25'], most_polluted['district_name'], fontsize=10, fontweight='bold')

plt.tight_layout()
plt.show()