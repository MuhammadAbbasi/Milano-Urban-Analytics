import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from shapely import wkt
from shapely.geometry.base import BaseGeometry
import numpy as np

# --- 1. ROBUST DATA LOADING ---
print("Loading data...")
try:
    df = pd.read_csv("dataset/milan_real_comprehensive_data.csv")
    print("Columns found:", df.columns.tolist())
except FileNotFoundError:
    print("Error: 'milan_real_comprehensive_data.csv' not found.")
    exit()

# FIX: Rename column if needed (Handles both naming conventions)
if 'Avg_Income' in df.columns and 'Avg_Income_Per_Taxpayer' not in df.columns:
    df.rename(columns={'Avg_Income': 'Avg_Income_Per_Taxpayer'}, inplace=True)

# --- 2. ROBUST GEOMETRY CONVERSION (The Fix) ---
def parse_geometry(val):
    # If it's already a Geometry object, return it
    if isinstance(val, BaseGeometry):
        return val
    # If it's a string, convert it
    elif isinstance(val, str):
        try:
            return wkt.loads(val)
        except:
            return None
    # Otherwise, return None
    return None

if 'geometry' in df.columns:
    print("Processing geometry...")
    df['geometry'] = df['geometry'].apply(parse_geometry)
    # Drop rows with invalid geometry
    df = df.dropna(subset=['geometry'])
    gdf = gpd.GeoDataFrame(df, geometry='geometry')
else:
    print("Warning: No 'geometry' column found. Maps will be skipped.")
    gdf = None

# Set Style
sns.set_theme(style="whitegrid")

# --- CHART 1: WEALTH vs. TRAFFIC ---
print("Generating Chart 1...")
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='Avg_Income_Per_Taxpayer', y='Traffic_Density', 
                size='Traffic_Density', sizes=(50, 200), color='teal', alpha=0.7, legend=False)
sns.regplot(data=df, x='Avg_Income_Per_Taxpayer', y='Traffic_Density', 
            scatter=False, color='red', line_kws={'linestyle':'--'})
plt.title('1. Wealth vs. Traffic Density (Pollution Proxy)', fontsize=14, fontweight='bold')
plt.xlabel('Average Income (€)')
plt.ylabel('Traffic Density (m/km²)')
plt.savefig('chart_1_wealth_traffic.png', dpi=300, bbox_inches='tight')
plt.close()

# --- CHART 2: TRAFFIC vs. DECAY ---
print("Generating Chart 2...")
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='Traffic_Density', y='n_decayed_buildings', 
                color='orange', s=100, alpha=0.8, edgecolor='black')
plt.title('2. Traffic Density vs. Urban Decay', fontsize=14, fontweight='bold')
plt.xlabel('Traffic Density (m/km²)')
plt.ylabel('Number of Abandoned Buildings')
plt.savefig('chart_2_traffic_decay.png', dpi=300, bbox_inches='tight')
plt.close()

# --- CHART 3: TOP 10 DECAY ---
print("Generating Chart 3...")
plt.figure(figsize=(12, 6))
top_decay = df.sort_values('n_decayed_buildings', ascending=False).head(10)
sns.barplot(data=top_decay, x='n_decayed_buildings', y='NIL_NAME', hue='NIL_NAME', palette='Reds_r', legend=False)
plt.title('3. Top 10 Districts by Physical Decay', fontsize=14, fontweight='bold')
plt.xlabel('Count of Abandoned Buildings')
plt.ylabel('')
plt.savefig('chart_3_top_decay.png', dpi=300, bbox_inches='tight')
plt.close()

# --- CHART 4: RESILIENCE GAP (Binning Fix) ---
print("Generating Chart 4...")
np.random.seed(42)
# Add tiny noise to avoid "Bin edges must be unique" error
df['Income_Binning'] = df['Avg_Income_Per_Taxpayer'] + np.random.normal(0, 0.01, len(df))
df['Wealth_Class'] = pd.qcut(df['Income_Binning'], q=3, labels=['Low Income', 'Middle Class', 'High Income'])

# Normalize
df['Norm_Traffic'] = (df['Traffic_Density'] - df['Traffic_Density'].min()) / (df['Traffic_Density'].max() - df['Traffic_Density'].min())
df['Norm_Flood'] = (df['Flood_Risk'] - df['Flood_Risk'].min()) / (df['Flood_Risk'].max() - df['Flood_Risk'].min())

df_melt = df.melt(id_vars=['Wealth_Class'], value_vars=['Norm_Flood', 'Norm_Traffic'], 
                  var_name='Risk_Type', value_name='Risk_Score')

plt.figure(figsize=(10, 6))
sns.barplot(data=df_melt, x='Wealth_Class', y='Risk_Score', hue='Risk_Type', 
            palette={'Norm_Flood': '#3498db', 'Norm_Traffic': '#e74c3c'}, capsize=.1)
plt.title('4. The Resilience Gap: Wealth vs. Risks', fontsize=14, fontweight='bold')
plt.ylabel('Normalized Risk Score (0-1)')
plt.legend(title='Risk Type', labels=['Flood Risk', 'Traffic/Pollution'])
plt.savefig('chart_4_resilience_gap.png', dpi=300, bbox_inches='tight')
plt.close()

# --- CHART 5: SPATIAL MAP (Traffic) ---
print("Generating Chart 5...")
if gdf is not None:
    fig, ax = plt.subplots(figsize=(12, 12))
    gdf.plot(column='Traffic_Density', ax=ax, cmap='inferno_r', legend=True,
             legend_kwds={'label': "Traffic Density (m/km²)", 'shrink': 0.6})
    gdf.boundary.plot(ax=ax, linewidth=0.5, color='black')
    plt.title('5. Spatial Map of Traffic Density', fontsize=15, fontweight='bold')
    plt.axis('off')
    plt.savefig('chart_5_traffic_map.png', dpi=300, bbox_inches='tight')
    plt.close()
else:
    print("Skipping Map 5 (No geometry).")

# --- CHART 6: SIDE-BY-SIDE MAPS (Income vs Traffic) ---
print("Generating Chart 6...")
if gdf is not None:
    fig, axes = plt.subplots(1, 2, figsize=(20, 12))
    
    # Map 1: Wealth
    gdf.plot(column='Avg_Income_Per_Taxpayer', ax=axes[0], cmap='Greens', legend=True,
             legend_kwds={'label': "Avg Income (€)", 'orientation': "horizontal", 'shrink': 0.8})
    gdf.boundary.plot(ax=axes[0], linewidth=0.5, color='black')
    axes[0].set_title('Geography of Wealth', fontsize=18, fontweight='bold')
    axes[0].axis('off')
    
    # Map 2: Traffic
    gdf.plot(column='Traffic_Density', ax=axes[1], cmap='OrRd', legend=True,
             legend_kwds={'label': "Traffic Density (m/km²)", 'orientation': "horizontal", 'shrink': 0.8})
    gdf.boundary.plot(ax=axes[1], linewidth=0.5, color='black')
    axes[1].set_title('Geography of Congestion', fontsize=18, fontweight='bold')
    axes[1].axis('off')
    
    plt.tight_layout()
    plt.savefig('chart_6_income_vs_traffic_maps.png', dpi=300, bbox_inches='tight')
    plt.close()
else:
    print("Skipping Chart 6 (No geometry).")

# --- CHART 7: HEXBIN CLUSTER ---
print("Generating Chart 7...")
plt.figure(figsize=(10, 8))
hb = plt.hexbin(df['Avg_Income_Per_Taxpayer'], df['Traffic_Density'], 
                gridsize=20, cmap='inferno', mincnt=1, edgecolors='gray')
cb = plt.colorbar(hb)
cb.set_label('Count of Districts')
sns.regplot(data=df, x='Avg_Income_Per_Taxpayer', y='Traffic_Density', 
            scatter=False, color='cyan', line_kws={'linestyle':'--', 'linewidth': 2})
plt.title('Cluster Analysis: Income vs. Traffic Density', fontsize=16, fontweight='bold')
plt.xlabel('Average Income (€)', fontsize=12)
plt.ylabel('Traffic Density (m/km²)', fontsize=12)
plt.savefig('chart_7_income_traffic_hexbin.png', dpi=300, bbox_inches='tight')
plt.close()

print("Success! All 7 charts generated.")