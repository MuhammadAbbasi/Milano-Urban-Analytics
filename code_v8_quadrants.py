import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. Load Data
df = pd.read_csv("dataset/milan_real_comprehensive_data.csv")

# 2. Fix Column Names if needed
if 'Avg_Income' in df.columns:
    df.rename(columns={'Avg_Income': 'Avg_Income_Per_Taxpayer'}, inplace=True)

# 3. Create the "Risk Score" (Composite of Traffic + Decay)
# Normalize Traffic (Environmental Risk)
df['Norm_Traffic'] = (df['Traffic_Density'] - df['Traffic_Density'].min()) / (df['Traffic_Density'].max() - df['Traffic_Density'].min())
# Normalize Decay (Physical Risk)
df['Norm_Decay'] = (df['n_decayed_buildings'] - df['n_decayed_buildings'].min()) / (df['n_decayed_buildings'].max() - df['n_decayed_buildings'].min())

# Y-Axis: Composite Vulnerability (Average of the two risks)
df['Physical_Vulnerability'] = (df['Norm_Traffic'] * 0.3) + (df['Norm_Decay'] * 0.7) 
# (Weighting Decay higher for Y-axis to separate the "Forgotten" from "Gilded Cage")

# X-Axis: Economic Power
df['Economic_Power'] = df['Avg_Income_Per_Taxpayer']

# 4. Calculate Medians for the Quadrants
median_income = df['Economic_Power'].median()
median_risk = df['Physical_Vulnerability'].median()

# 5. Plot
plt.figure(figsize=(12, 10))
sns.set_style("whitegrid")

# Scatter Plot
sns.scatterplot(
    data=df, 
    x='Economic_Power', 
    y='Physical_Vulnerability',
    s=100, 
    alpha=0.7, 
    edgecolor='black',
    color='grey'
)

# Add Quadrant Lines
plt.axvline(median_income, color='red', linestyle='--', linewidth=1.5, label='Median Income')
plt.axhline(median_risk, color='blue', linestyle='--', linewidth=1.5, label='Median Vulnerability')

# Annotate the 4 Typologies (Quadrants)
# Top Left: Low Wealth, High Risk
plt.text(df['Economic_Power'].min(), df['Physical_Vulnerability'].max(), 
         "THE FORGOTTEN\n(Low Wealth, High Decay)", 
         fontsize=12, weight='bold', color='darkred', ha='left', va='top')

# Top Right: High Wealth, High Risk
plt.text(df['Economic_Power'].max(), df['Physical_Vulnerability'].max(), 
         "THE GILDED CAGE\n(High Wealth, High Traffic)", 
         fontsize=12, weight='bold', color='orange', ha='right', va='top')

# Bottom Right: High Wealth, Low Risk
plt.text(df['Economic_Power'].max(), df['Physical_Vulnerability'].min(), 
         "THE ELITE\n(Smart City Ideal)", 
         fontsize=12, weight='bold', color='green', ha='right', va='bottom')

# Bottom Left: Low Wealth, Low Risk
plt.text(df['Economic_Power'].min(), df['Physical_Vulnerability'].min(), 
         "THE RESILIENT POOR\n(Peripheral Safety)", 
         fontsize=12, weight='bold', color='blue', ha='left', va='bottom')

# Annotate Specific Labels from your text
key_districts = ['DUOMO', 'LAMBRATE - ORTICA', 'BAGGIO', 'GUASTALLA', 'BRERA', 'QUARTO OGGIARO']
for i, row in df.iterrows():
    name = row['NIL_NAME'].upper().strip()
    if any(x in name for x in key_districts):
        plt.text(row['Economic_Power']+500, row['Physical_Vulnerability'], 
                 name.split("-")[0], fontsize=9, weight='bold')

plt.title("Milan's Urban Quadrants: Economic Power vs. Physical/Environmental Risk", fontsize=15, fontweight='bold')
plt.xlabel("Avg Income per Taxpayer (€)", fontsize=12)
plt.ylabel("Composite Vulnerability Score (Decay + Traffic)", fontsize=12)

plt.savefig("milan_quadrants.png", dpi=300, bbox_inches='tight')
print("Chart generated: milan_quadrants.png")