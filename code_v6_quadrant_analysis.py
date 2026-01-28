import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import code_v5  # Assuming code_v5.py has been run and gdf_final is available

# --- 1. LOAD DATA ---
# If you are continuing from the previous step, 'gdf_final' is already in memory.
# If not, load the saved CSV:
try:
    df = pd.read_csv("dataset/milan_final_report_data.csv")
except:
    # Use the dataframe from memory if available
    df = gdf_final.copy()

# --- 2. CALCULATE MEDIANS FOR QUADRANTS ---
# We use the Median (not Mean) to find the true "middle" of the data distribution.
wealth_median = df['Norm_Wealth'].median()
vuln_median = df['Physical_Vulnerability'].median()

# --- 3. CREATE THE SCATTER PLOT ---
plt.figure(figsize=(14, 10))
sns.set_style("whitegrid")

# Create the scatter points
# We color them based on vulnerability for visual consistency
scatter = sns.scatterplot(
    data=df, 
    x='Norm_Wealth', 
    y='Physical_Vulnerability', 
    hue='Physical_Vulnerability', 
    palette='RdPu', 
    s=150, # Size of dots
    edgecolor='black',
    alpha=0.8
)

# --- 4. DRAW QUADRANT LINES ---
plt.axvline(x=wealth_median, color='grey', linestyle='--', linewidth=1.5)
plt.axhline(y=vuln_median, color='grey', linestyle='--', linewidth=1.5)

# --- 5. LABEL THE QUADRANTS (The Strategic Insight) ---
# Top Left: Poor & Risky
plt.text(0.1, 0.9, "THE FORGOTTEN\n(Low Wealth, High Risk)", 
         fontsize=12, fontweight='bold', color='darkred', bbox=dict(facecolor='white', alpha=0.8))

# Top Right: Rich & Risky (The Surprise)
plt.text(0.8, 0.9, "THE GILDED CAGE\n(High Wealth, High Risk)", 
         fontsize=12, fontweight='bold', color='purple', bbox=dict(facecolor='white', alpha=0.8))

# Bottom Left: Poor & Safe
plt.text(0.1, 0.1, "THE RESILIENT POOR\n(Low Wealth, Low Risk)", 
         fontsize=12, fontweight='bold', color='green', bbox=dict(facecolor='white', alpha=0.8))

# Bottom Right: Rich & Safe
plt.text(0.8, 0.1, "THE ELITE\n(High Wealth, Low Risk)", 
         fontsize=12, fontweight='bold', color='darkgreen', bbox=dict(facecolor='white', alpha=0.8))

# --- 6. ANNOTATE KEY DISTRICTS (Examples) ---
# We label only the most extreme points to avoid clutter
# Sort by distance from center to find "extremes"
df['dist_from_center'] = ((df['Norm_Wealth'] - wealth_median)**2 + (df['Physical_Vulnerability'] - vuln_median)**2)**0.5
top_extremes = df.sort_values('dist_from_center', ascending=False).head(10)

for line in range(0, top_extremes.shape[0]):
    plt.text(
        top_extremes.Norm_Wealth.iloc[line]+0.01, 
        top_extremes.Physical_Vulnerability.iloc[line], 
        top_extremes.NIL_NAME_CLEAN.iloc[line], 
        horizontalalignment='left', 
        size='small', 
        color='black', 
        weight='semibold'
    )

# Final Formatting
plt.title("Milan's Urban Quadrants: Wealth vs. Vulnerability", fontsize=18)
plt.xlabel("Economic Power (Normalized Wealth)", fontsize=14)
plt.ylabel("Physical Vulnerability (Flood + Decay)", fontsize=14)
plt.legend(title="Risk Score", bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()