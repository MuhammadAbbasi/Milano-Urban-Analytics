import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler

# --- 1. LOAD THE NEW GEOSPATIAL MASTER FILE (V3) ---
print("Loading V3 Master File (Decay + Water)...")
gdf = gpd.read_file("dataset/milan_districts_master_v3.geojson")

'''
# --- 2. RELOAD WEALTH & HEAT (From your previous datasets) ---
# We merge them again to be sure everything is in one place
print("Merging Wealth and Heat data...")

# Load Income (Wealth)
df_income = pd.read_csv("dataset/geo/redditi_e_principali_variabili_irpef_su_base_subcomunale_csv_2023.csv", sep=';')
# Clean names for merging
df_income['NIL'] = df_income['NIL'].str.upper().str.strip()
gdf['NIL_NAME'] = gdf['NIL_NAME'].str.upper().str.strip()
# Merge Income
gdf = gdf.merge(df_income[['NIL', 'Redditi_totale_imponibile_eur']], 
                left_on='NIL_NAME', right_on='NIL', how='left')

                
'''

# --- 2. RELOAD WEALTH (Con controllo nomi colonne) ---
print("Merging Wealth data...")

# Carica il file CSV
df_income = pd.read_csv("dataset/geo/redditi_e_principali_variabili_irpef_su_base_subcomunale_csv_2023.csv", sep=';')

# 1. Pulisci i nomi delle colonne (rimuove spazi extra es. " NIL " -> "NIL")
df_income.columns = df_income.columns.str.strip()

# 2. Cerca la colonna del quartiere e rinominala in 'NIL'
# Elenco dei nomi possibili usati dal comune
possible_names = ['Quartiere', 'Denominazione', 'NIL', 'NIL_NAME', 'Zona']
found_col = None

for col in df_income.columns:
    if col in possible_names:
        found_col = col
        break

if found_col:
    print(f"Colonna quartiere trovata: '{found_col}' -> Rinomino in 'NIL'")
    df_income.rename(columns={found_col: 'NIL'}, inplace=True)
else:
    print("⚠️ ATTENZIONE: Nessuna colonna 'NIL' o 'Quartiere' trovata!")
    print("Colonne disponibili:", df_income.columns.tolist())
    # Se fallisce, fermiamo lo script per farti leggere l'errore
    raise KeyError("Controlla i nomi delle colonne stampati qui sopra.")

# Ora procedi con la pulizia e il merge
df_income['NIL'] = df_income['NIL'].str.upper().str.strip()
gdf['NIL_NAME'] = gdf['NIL_NAME'].str.upper().str.strip()

# Merge
gdf = gdf.merge(df_income[['NIL', 'Redditi_totale_imponibile_eur']], 
                left_on='NIL_NAME', right_on='NIL', how='left')

# --- CONTINUA CON IL RESTO DEL CODICE (HEAT, ETC.) ---
# Load Heat (If not already in V3, we load it. If V3 was built on V2, it might be there. Let's start fresh to be safe)
# Assuming Heat was in a separate GeoJSON or CSV. 
# If you don't have the heat file handy, we can skip it, but let's assume you have the one from Code V2:
try:
    gdf_heat = gpd.read_file("dataset/geo/ds2811_spotted-milan-urbanheatexposure-nil-01072024_31072024.geojson")
    gdf_heat['NIL'] = gdf_heat['NIL'].str.upper().str.strip()
    # We only want the heat index column
    gdf = gdf.merge(gdf_heat[['NIL', 'heat_index']], 
                    left_on='NIL_NAME', right_on='NIL', how='left', suffixes=('', '_new'))
except:
    print("⚠️ Heat file not found or merge failed. Proceeding without Heat update.")

# --- 3. DATA NORMALIZATION (Crucial for "Index" creation) ---
# We need to compare Euros, Meters, and Counts. We scale everything from 0 to 1.
scaler = MinMaxScaler()

# A. Vulnerability Score (Higher is WORSE)
# - Heat: High is bad
# - Decay: High is bad
# - Distance to Water: LOW is bad (risk of flood). So we invert it.

# Invert Distance (1/Distance) or just negating it for correlation
# Let's create a "Flood Risk Score": Closer = Higher Score
# We use a simple trick: Max Distance - Current Distance
gdf['Flood_Risk_Score'] = gdf['dist_to_water_m'].max() - gdf['dist_to_water_m']

# Normalize
columns_to_normalize = ['Redditi_totale_imponibile_eur', 'n_decayed_buildings', 'Flood_Risk_Score', 'heat_index']
# Handle missing values before scaling
gdf[columns_to_normalize] = gdf[columns_to_normalize].fillna(gdf[columns_to_normalize].mean())

# Create Normalized Columns (0-1)
gdf['Norm_Wealth'] = scaler.fit_transform(gdf[['Redditi_totale_imponibile_eur']])
gdf['Norm_Decay'] = scaler.fit_transform(gdf[['n_decayed_buildings']])
gdf['Norm_Flood'] = scaler.fit_transform(gdf[['Flood_Risk_Score']])
if 'heat_index' in gdf.columns:
    gdf['Norm_Heat'] = scaler.fit_transform(gdf[['heat_index']])
else:
    gdf['Norm_Heat'] = 0

# Create Composite "TOTAL VULNERABILITY INDEX"
# Vulnerability = (Heat + Flood + Decay) / 3
gdf['Total_Vulnerability'] = (gdf['Norm_Heat'] + gdf['Norm_Flood'] + gdf['Norm_Decay']) / 3

# --- 4. VISUALIZATION: THE URBAN DIVIDE ---
fig, ax = plt.subplots(1, 2, figsize=(20, 10))

# Map 1: The Wealthy City
gdf.plot(column='Norm_Wealth', cmap='Greens', legend=True, ax=ax[0])
ax[0].set_title("The Wealthy City (Income)", fontsize=15)
ax[0].axis('off')

# Map 2: The Vulnerable City (Composite Index)
gdf.plot(column='Total_Vulnerability', cmap='RdPu', legend=True, ax=ax[1])
ax[1].set_title("The Vulnerable City (Heat + Flood + Decay)", fontsize=15)
ax[1].axis('off')

plt.suptitle("Milan's Urban Divide: Wealth vs. Vulnerability", fontsize=20)
plt.show()

# --- 5. STATISTICAL PROOF ---
# Correlation Matrix
corr = gdf[['Norm_Wealth', 'Total_Vulnerability', 'Norm_Decay', 'Norm_Flood', 'Norm_Heat']].corr()
print("\n--- Correlation Matrix (Does Wealth Protect You?) ---")
print(corr)

# Save Final Data for your Report
gdf.to_csv("dataset/milan_urban_divide_final_data.csv", index=False)
print("Final CSV saved for reporting.")