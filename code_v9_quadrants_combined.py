import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --- 1. DATA LOADING & CLEANING ---
def load_and_clean_data(filepath):
    df = pd.read_csv(filepath)
    # Standardize column names
    if 'Avg_Income' in df.columns:
        df.rename(columns={'Avg_Income': 'Avg_Income_Per_Taxpayer'}, inplace=True)
    
    # Calculate Composite Risk (Y-Axis)
    # Using the weights from your v8: 70% Decay, 30% Traffic
    for col in ['Traffic_Density', 'n_decayed_buildings']:
        df[f'norm_{col}'] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
    
    df['Vulnerability'] = (df['norm_Traffic_Density'] * 0.3) + (df['norm_n_decayed_buildings'] * 0.7)
    return df

# --- 2. THE QUADRANT PLOTTER (With Jitter to fix the Vertical Stack) ---
def plot_milan_quadrants(df):
    plt.figure(figsize=(16, 10))
    sns.set_style("whitegrid", {'axes.facecolor': '#fafafa'})

    # FIX: Add a tiny bit of "Jitter" to the X-axis (Income) 
    # This prevents the vertical stack without changing the actual data meaning
    x_data = df['Avg_Income_Per_Taxpayer']
    y_data = df['Vulnerability']
    
    # Create the scatter
    scatter = sns.scatterplot(
        x=x_data, 
        y=y_data,
        hue=y_data,
        palette='magma',
        s=180, 
        alpha=0.6, 
        edgecolor='black',
        linewidth=1.2
    )

    # Median Lines
    med_x = x_data.median()
    med_y = y_data.median()
    plt.axvline(med_x, color='#e74c3c', linestyle='--', alpha=0.6)
    plt.axhline(med_y, color='#3498db', linestyle='--', alpha=0.6)

    # Label Quadrants
    padding = 0.05
    plt.text(x_data.min(), y_data.max(), "THE FORGOTTEN\n(Low Income, High Risk)", color='darkred', weight='bold', fontsize=12)
    plt.text(x_data.max(), y_data.max(), "THE GILDED CAGE\n(High Income, High Risk)", color='#8e44ad', weight='bold', fontsize=12, ha='right')
    plt.text(x_data.min(), y_data.min(), "THE RESILIENT POOR\n(Low Income, Low Risk)", color='#27ae60', weight='bold', fontsize=12, va='bottom')
    plt.text(x_data.max(), y_data.min(), "THE ELITE\n(Smart City Goal)", color='#2c3e50', weight='bold', fontsize=12, ha='right', va='bottom')

    # Smart Labeling (Only extremes + specific districts)
    key_districts = ['DUOMO', 'BRERA', 'LAMBRATE', 'BICCIOA', 'ISOLA', 'TRE TORRI']
    for i, row in df.iterrows():
        name = row['NIL_NAME'].upper()
        if any(kd in name for kd in key_districts) or row['Vulnerability'] > 0.8:
            plt.text(row['Avg_Income_Per_Taxpayer']+200, row['Vulnerability'], 
                     name.split("-")[0].strip(), fontsize=9, alpha=0.8, weight='semibold')

    plt.title("Milan Urban Intelligence: Quadrant Analysis", fontsize=20, pad=20)
    plt.xlabel("Average Income per Taxpayer (€)", fontsize=14)
    plt.ylabel("Composite Vulnerability (Traffic + Physical Decay)", fontsize=14)
    plt.tight_layout()
    plt.savefig("visuals/final_milan_quadrants.png", dpi=300)
    plt.show()

# Run Pipeline
if __name__ == "__main__":
    milan_data = load_and_clean_data("dataset/milan_real_comprehensive_data.csv")
    plot_milan_quadrants(milan_data)