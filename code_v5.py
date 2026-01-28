import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

# --- 1. CONFIGURATION: NIL to CAP MAPPING ---
# This dictionary maps the District Name (NIL) to its Postal Code (CAP).
nil_to_cap = {
    'DUOMO': 20121, 'BRERA': 20121, 'GIARDINI PORTA VENEZIA': 20121, 'GUASTALLA': 20122,
    'PORTA VIGENTINA': 20122, 'TICINESE': 20123, 'DARSENA': 20123, 'PAGANO': 20145,
    'STAZIONE CENTRALE': 20124, 'ISOLA': 20159, 'BICOCCA': 20126, 'ADRIANO': 20128,
    'CITTA\' STUDI': 20133, 'LAMBRATE': 20134, 'PORTA ROMANA': 20135, 'ROGOREDO': 20138,
    'RIPAMONTI': 20141, 'GRATOSOGLIO': 20142, 'BARONA': 20142, 'GIAMBELLINO': 20146,
    'BANDE NERE': 20146, 'SAN SIRO': 20148, 'QT8': 20148, 'PORTELLO': 20149,
    'GALLARATESE': 20151, 'BAGGIO': 20153, 'QUARTO OGGIARO': 20157, 'BOVISA': 20158,
    'NIGUARDA': 20162, 'AFFORI': 20161, 'SARPI': 20154, 'BUENOS AIRES - PORTA VENEZIA': 20129,
    'LORETO': 20131, 'PADOVA': 20127, 'CORVETTO': 20139, 'ORTOMERCATO': 20137
}

# --- 2. LOAD GEOSPATIAL DATA (The "Master V3" from previous step) ---
print("Loading V3 Physical Map (Decay + Flood)...")
try:
    gdf = gpd.read_file("dataset/milan_districts_master_v3.geojson")
except:
    print("⚠️ V3 File not found. Loading basic map (Results will be empty for physical risk).")
    gdf = gpd.read_file("dataset/geo/milan_districts_clean.geojson")
    gdf['n_decayed_buildings'] = 0
    gdf['dist_to_water_m'] = 1000

# --- 3. LOAD & CLEAN INCOME DATA (CAP Based) ---
print("Processing Income Data (CAP)...")
# Load the raw CSV
df_cap_raw = pd.read_csv("dataset/geo/redditi_e_principali_variabili_irpef_su_base_subcomunale_csv_2023.csv", sep=';')

# The file is in "Long Format". We need to find the rows for "Taxable Income".
# We look for strings containing "Reddito" AND "imponibile" to be safe.
mask = df_cap_raw['Redditi e variabili Irpef'].str.contains("Reddito imponibile", case=False, na=False) & \
       df_cap_raw['Redditi e variabili Irpef'].str.contains("Ammontare", case=False, na=False)

df_income = df_cap_raw[mask].copy()

# Clean the 'Importi' column (Convert "12.345,00" to float)
try:
    df_income['Importi'] = df_income['Importi'].astype(str).str.replace('.', '', regex=False) # Remove thousands separator
    df_income['Importi'] = df_income['Importi'].astype(str).str.replace(',', '.', regex=False) # Comma to dot
    df_income['Importi'] = pd.to_numeric(df_income['Importi'])
except Exception as e:
    print(f"Warning during currency conversion: {e}")

# Group by CAP (Average income per CAP)
df_income_clean = df_income.groupby('CAP')['Importi'].mean().reset_index()
df_income_clean.rename(columns={'Importi': 'Avg_Income_CAP'}, inplace=True)

# --- 4. MERGE EVERYTHING ---
print("Merging Wealth + Physical Data...")

# Clean NIL names in Map
gdf['NIL_NAME_CLEAN'] = gdf['NIL_NAME'].str.upper().str.strip()

# A. Assign CAP to each District
gdf['Assigned_CAP'] = gdf['NIL_NAME_CLEAN'].map(nil_to_cap)

# B. Merge Income Data onto the Map
gdf_final = gdf.merge(df_income_clean, left_on='Assigned_CAP', right_on='CAP', how='left')

# Fill missing income with city average (to avoid white spots on map)
avg_city_income = gdf_final['Avg_Income_CAP'].mean()
gdf_final['Avg_Income_CAP'] = gdf_final['Avg_Income_CAP'].fillna(avg_city_income)

# --- 5. CALCULATE FINAL SCORES ---
scaler = MinMaxScaler()

# A. Flood Risk Score (Invert Distance: Near = High Risk)
if 'dist_to_water_m' in gdf_final.columns:
    gdf_final['Flood_Risk'] = gdf_final['dist_to_water_m'].max() - gdf_final['dist_to_water_m']
else:
    gdf_final['Flood_Risk'] = 0

# B. Normalize (0-1 Scale)
cols_norm = ['Avg_Income_CAP', 'n_decayed_buildings', 'Flood_Risk']
for col in cols_norm:
    if col not in gdf_final.columns: gdf_final[col] = 0 # Safety check

gdf_final['Norm_Wealth'] = scaler.fit_transform(gdf_final[['Avg_Income_CAP']])
gdf_final['Norm_Decay'] = scaler.fit_transform(gdf_final[['n_decayed_buildings']])
gdf_final['Norm_Flood'] = scaler.fit_transform(gdf_final[['Flood_Risk']])

# C. Total Vulnerability Index (Physical Risks Only)
# We exclude Wealth from the definition of "Vulnerability" to compare them later.
gdf_final['Physical_Vulnerability'] = (gdf_final['Norm_Decay'] + gdf_final['Norm_Flood']) / 2

# --- 6. VISUALIZATION: THE URBAN DIVIDE ---
fig, ax = plt.subplots(1, 2, figsize=(24, 10))

# Map 1: WEALTH (Income)
gdf_final.plot(column='Norm_Wealth', cmap='Greens', legend=True, ax=ax[0])
ax[0].set_title("Economic Geography (Estimated Wealth)", fontsize=18)
ax[0].axis('off')

# Map 2: VULNERABILITY (Decay + Flood)
gdf_final.plot(column='Physical_Vulnerability', cmap='RdPu', legend=True, ax=ax[1])
ax[1].set_title("Physical Vulnerability (Decay + Flood Risk)", fontsize=18)
ax[1].axis('off')

plt.suptitle("Milan's Urban Divide: Does Wealth Protect You?", fontsize=24)
plt.show()

# --- 7. CORRELATION ANALYSIS ---
print("\n--- CORRELATION MATRIX ---")
# If the number is NEGATIVE, it means Wealthier areas have LESS risk (The Divide exists).
corr = gdf_final[['Norm_Wealth', 'Physical_Vulnerability', 'Norm_Decay', 'Norm_Flood']].corr()
print(corr)

# Save Final Data
gdf_final.to_csv("dataset/milan_final_report_data.csv", index=False)
print("\nSuccess! Final dataset saved.")