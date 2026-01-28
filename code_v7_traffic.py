import pandas as pd
import geopandas as gpd
import numpy as np

# 1. LOAD DATA
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

# Load Source Files
df_traffic = pd.read_csv("dataset/milan_traffic_density.csv")
gdf_master = gpd.read_file("dataset/milan_districts_master_v3.geojson")
df_redditi = pd.read_csv("dataset/geo/redditi_e_principali_variabili_irpef_su_base_subcomunale_csv_2023.csv", sep=';')

# 2. PROCESS INCOME
if df_redditi['Importi'].dtype == 'O':
    df_redditi['Importi'] = pd.to_numeric(df_redditi['Importi'].astype(str).str.replace('.', '').str.replace(',', '.'), errors='coerce')

# Filter for "Reddito complessivo"
mask_total = df_redditi['Redditi e variabili Irpef'].str.contains("Reddito complessivo", case=False, na=False)
df_filtered = df_redditi[mask_total]

# Group by CAP
df_amt = df_filtered[df_filtered['Redditi e variabili Irpef'].str.contains("Ammontare")].groupby('CAP')['Importi'].sum().reset_index().rename(columns={'Importi': 'Total_Euro'})
df_frq = df_filtered[df_filtered['Redditi e variabili Irpef'].str.contains("Frequenza")].groupby('CAP')['Importi'].sum().reset_index().rename(columns={'Importi': 'Num_Taxpayers'})
df_cap_income = pd.merge(df_amt, df_frq, on='CAP')
df_cap_income['Avg_Income'] = df_cap_income['Total_Euro'] / df_cap_income['Num_Taxpayers']

# 3. MERGE EVERYTHING
# Clean Names
gdf_master['NIL_clean'] = gdf_master['NIL_NAME'].str.upper().str.strip()
df_traffic['NIL_clean'] = df_traffic['NIL_NAME'].str.upper().str.strip()

# Map CAP Income to NIL
df_mapping = pd.DataFrame(list(nil_to_cap.items()), columns=['NIL_clean', 'CAP'])
df_mapping['NIL_clean'] = df_mapping['NIL_clean'].str.upper().str.strip()
df_nil_income = df_mapping.merge(df_cap_income, on='CAP', how='left')

# Final Merge
gdf_final = gdf_master.merge(df_nil_income[['NIL_clean', 'Avg_Income', 'CAP']], on='NIL_clean', how='left')
gdf_final = gdf_final.merge(df_traffic[['NIL_clean', 'Total_Road_Length_m', 'Intersections']], on='NIL_clean', how='left')

# 4. CALCULATE METRICS
gdf_final['Traffic_Density'] = gdf_final['Total_Road_Length_m'] / (gdf_final.geometry.area / 10**6)
gdf_final['Flood_Risk'] = gdf_final['dist_to_water_m'].max() - gdf_final['dist_to_water_m']
gdf_final['Avg_Income'] = gdf_final['Avg_Income'].fillna(gdf_final['Avg_Income'].mean())

# 5. SAVE
gdf_final.to_csv("dataset/milan_real_comprehensive_data.csv", index=False)
print("File saved: milan_real_comprehensive_data.csv")