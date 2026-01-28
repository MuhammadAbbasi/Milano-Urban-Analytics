import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --- 1. SETUP & LOAD REAL DATA ---
print("Loading Data...")

# A. Map (Spatial Base)
gdf = gpd.read_file("dataset/milan_districts_clean.geojson")
gdf['NIL_NAME'] = gdf['NIL_NAME'].str.upper().str.strip()

# B. Income (Real Economic Data)
df_income = pd.read_csv("dataset/redditi_e_principali_variabili_irpef_su_base_subcomunale_csv_2023.csv", sep=';')
# C. Heat (Real Climate Data)
gdf_heat = gpd.read_file("dataset/ds2811_spotted-milan-urbanheatexposure-nil-01072024_31072024.geojson")
gdf_heat['NIL'] = gdf_heat['NIL'].str.upper().str.strip()

# D. Green Space (Real Environment Data)
df_osm = pd.read_csv("dataset/milan_osm_features.csv")
df_osm['NIL_NAME'] = df_osm['NIL_NAME'].str.upper().str.strip()

# E. Weather & Accidents (Real Temporal Data)
df_weather = pd.read_csv("dataset/milan_weather_20150101_20241231.csv")
df_acc_new = pd.read_csv("dataset/crime/Incidenti_Stradali_-_Dati_per_comune_-_Quadriennio_2020-2023_20260118.csv")
# dataset\crime\Incidenti_Stradali_-_Dati_per_comune_-_Quadriennio_2020-2023_20260118.csv

# --- 2. PROCESS ECONOMIC DATA (CAP -> NIL) ---
# Filter for Total Income (Ammontare)
target_cats = ['Reddito da lavoro dipendente e assimilati - Ammontare in euro',
               'Reddito da pensione - Ammontare in euro',
               'Reddito da lavoro autonomo (comprensivo dei valori nulli) - Ammontare in euro']
df_income_sum = df_income[df_income['Redditi e variabili Irpef'].isin(target_cats)].groupby('CAP')['Importi'].sum().reset_index()
df_income_sum.rename(columns={'Importi': 'Total_Wealth'}, inplace=True)

# Map CAP to NIL (Hardcoded Dictionary)
nil_to_cap = {
    'DUOMO': 20121, 'BRERA': 20121, 'GIARDINI PORTA VENEZIA': 20121, 'GUASTALLA': 20122,
    'PORTA VIGENTINA': 20122, 'TICINESE': 20123, 'DARSENA': 20123, 'PAGANO': 20145,
    'STAZIONE CENTRALE': 20124, 'ISOLA': 20159, 'BICOCCA': 20126, 'ADRIANO': 20128,
    'CITTÀ STUDI': 20133, 'LAMBRATE': 20134, 'PORTA ROMANA': 20135, 'ROGOREDO': 20138,
    'RIPAMONTI': 20141, 'GRATOSOGLIO': 20142, 'BARONA': 20142, 'GIAMBELLINO': 20146,
    'BANDE NERE': 20146, 'SAN SIRO': 20148, 'QT8': 20148, 'PORTELLO': 20149,
    'GALLARATESE': 20151, 'BAGGIO': 20153, 'QUARTO OGGIARO': 20157, 'BOVISA': 20158,
    'NIGUARDA': 20162, 'AFFORI': 20161, 'SARPI': 20154, 'BUENOS AIRES - PORTA VENEZIA': 20129
}
def get_cap(name):
    if name in nil_to_cap: return nil_to_cap[name]
    for k, v in nil_to_cap.items():
        if k in name: return v
    return 20100 # Fallback

gdf['CAP'] = gdf['NIL_NAME'].apply(get_cap)
gdf_econ = gdf.merge(df_income_sum, left_on='CAP', right_on='CAP', how='left')

# --- 3. MERGE SPATIAL LAYERS (Wealth + Heat + Green) ---
# Merge Wealth with Heat
gdf_master = gdf_econ.merge(gdf_heat[['NIL', 'value']], left_on='NIL_NAME', right_on='NIL', how='left')
# Merge with Green Space
gdf_master = gdf_master.merge(df_osm, on='NIL_NAME', how='left')

# Cleanup
gdf_master['Heat_Index'] = gdf_master['value']
gdf_master = gdf_master[['NIL_NAME', 'Total_Wealth', 'Heat_Index', 'green_space_pct', 'geometry']].dropna()

# --- 4. ANALYZE TEMPORAL SAFETY (Accidents vs Rain) ---
# Prepare Accidents (Filter Milano)
milano_acc = df_acc_new[df_acc_new['Denominazione_comune'] == 'MILANO'].groupby('Anno')['N_Incidenti'].sum().reset_index()

# Prepare Weather (Annual Rain)
df_weather['date'] = pd.to_datetime(df_weather['date'])
df_weather['year'] = df_weather['date'].dt.year
weather_annual = df_weather.groupby('year')['precipitation'].sum().reset_index()

# Merge
df_safety_analysis = milano_acc.merge(weather_annual, left_on='Anno', right_on='year')

# --- 5. VISUALIZATION OUTPUTS ---

fig = plt.figure(figsize=(18, 12))
plt.suptitle("Milan Urban Analysis: Inequality, Climate, and Safety (REAL DATA ONLY)", fontsize=20)

# Plot A: Wealth Map
ax1 = plt.subplot(2, 2, 1)
gdf_master.plot(column='Total_Wealth', cmap='Greens', legend=True, ax=ax1, 
                legend_kwds={'label': "Total Taxable Income (€)"})
ax1.set_title("Economic Geography (Wealth)")
ax1.set_axis_off()

# Plot B: Heat Map
ax2 = plt.subplot(2, 2, 2)
gdf_master.plot(column='Heat_Index', cmap='magma', legend=True, ax=ax2,
                legend_kwds={'label': "Urban Heat Exposure Index"})
ax2.set_title("Climate Vulnerability (Heat)")
ax2.set_axis_off()

# Plot C: Correlation Heatmap (Wealth vs Heat vs Green)
ax3 = plt.subplot(2, 2, 3)
corr_cols = ['Total_Wealth', 'Heat_Index', 'green_space_pct']
sns.heatmap(gdf_master[corr_cols].corr(), annot=True, cmap='coolwarm', ax=ax3)
ax3.set_title("Spatial Correlations")

# Plot D: Accidents vs Rain (Temporal)
ax4 = plt.subplot(2, 2, 4)
ax4.bar(df_safety_analysis['Anno'], df_safety_analysis['N_Incidenti'], color='red', alpha=0.6, label='Accidents')
ax4_twin = ax4.twinx()
ax4_twin.plot(df_safety_analysis['Anno'], df_safety_analysis['precipitation'], color='blue', marker='o', linewidth=3, label='Rainfall')
ax4.set_ylabel("Accidents (Bars)", color='red')
ax4_twin.set_ylabel("Rainfall mm (Line)", color='blue')
ax4.set_title("Road Safety vs. Weather (2020-2023)")

plt.tight_layout()
plt.savefig("visuals/milan_final_real_analysis.png", dpi=300)
print("Analysis Complete. Saved 'milan_final_real_analysis.png'.")