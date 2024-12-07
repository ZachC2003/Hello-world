import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import json

# Load your pre-processed data
@st.cache_data
def load_data():
    # Replace with the path to your processed dataset
    combined_data = pd.read_csv("C:/Users/Zachary Cheney/OneDrive - University of Arkansas/Fall 2024/advanced financial modeling/Hello-world/Group_FDA_Project/combined_data.csv", index_col=0, parse_dates=True)
    return combined_data
def load_metadata():
    with open('C:/Users/Zachary Cheney/OneDrive - University of Arkansas/Fall 2024/advanced financial modeling/Hello-world/Group_FDA_Project/combined_data_metadata.json', 'r') as f:
        return json.load(f)


# Load data
combined_data = load_data()
metadata = load_metadata()

# Define columns from metadata
etf_columns = metadata['ETF Columns']
crsp_columns = metadata['CRSP Columns']

# Define columns
macro_columns = ['GDP Growth', 'Unemployment Rate', 'Interest Rate', 'Inflation Rate']
sector_columns = [col for col in combined_data.columns if '_ETF' in col or '_CRSP' in col]

# App title
st.title("Sector Rotation Strategy Dashboard")

# Section: Economic Cycle Transitions
st.header("Economic Cycle Transitions Over Time")

# Add explanation of economic cycles
st.markdown("""
### What are Economic Cycles?
Economic cycles are the natural fluctuation of the economy between periods of expansion (growth) and contraction (recession). 
These cycles are driven by changes in factors like GDP growth, unemployment rates, inflation, and interest rates.

#### Phases of the Economic Cycle:
- **Expansion (1)**: A period of economic growth characterized by increasing GDP, lower unemployment rates, and rising consumer confidence.
- **Neutral (0)**: A transitional phase where the economy is stable, but not showing strong growth or contraction.
- **Contraction (-1)**: A period of economic decline, often marked by decreasing GDP, higher unemployment rates, and reduced consumer spending.

Understanding these cycles is crucial for identifying investment opportunities, as different sectors tend to perform better during specific phases.
""")

# Section 1: Economic Cycle Summary
st.header("Economic Cycle Summary")
cycle = st.selectbox('Select Economic Cycle', combined_data['Economic Cycle'].unique())

# Dropdown to choose data type (ETFs, CRSP, or Both)
data_type = st.radio('Select Data Type', ['ETFs', 'CRSP', 'Both'])

# Filter columns based on selection
if data_type == 'ETFs':
    selected_columns = etf_columns
elif data_type == 'CRSP':
    selected_columns = crsp_columns
else:
    selected_columns = etf_columns + crsp_columns

# Show average returns for the selected economic cycle
filtered_data = combined_data[combined_data['Economic Cycle'] == cycle]
st.write(f"Average Returns by Sector for {cycle} ({data_type}):")
st.bar_chart(filtered_data[selected_columns].mean())

# Section 2: Correlation of Macro Indicators with Sectors
st.header("Macro Indicators vs. Sector Returns")
if st.checkbox("Show Correlation Heatmap"):
    macro_correlation = combined_data[macro_columns + selected_columns].corr()
    macro_to_sector_corr = macro_correlation.loc[macro_columns, selected_columns]

    # Display heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(macro_to_sector_corr, annot=True, cmap='coolwarm', fmt=".2f")
    st.pyplot(plt)

# Section 3: Hypothetical Portfolio Returns
st.header("Hypothetical Portfolio Returns")

# Define best sectors dynamically for the selected columns
best_sectors = combined_data.groupby('Economic Cycle')[selected_columns].mean().idxmax(axis=1).to_dict()

portfolio_returns = combined_data.apply(
    lambda row: row[best_sectors[row['Economic Cycle']]] if row['Economic Cycle'] in best_sectors else 0,
    axis=1
).cumsum()

st.line_chart(portfolio_returns)
st.write(f"This portfolio invests in the best-performing {data_type} sector for each economic cycle.")

# Section 4: Explore Data
st.header("Explore Data")
st.write("Full dataset:")
st.dataframe(combined_data)

# Section: Best and Worst Performing Sectors
st.header("Best and Worst Performing Sectors by Economic Cycle")

# Calculate average returns for each cycle
average_returns = combined_data.groupby('Economic Cycle')[etf_columns + crsp_columns].mean()

# Identify the best and worst sectors for each cycle
best_sectors = average_returns.idxmax(axis=1).to_dict()
worst_sectors = average_returns.idxmin(axis=1).to_dict()

# Display the average returns table
st.subheader("Average Sector Returns by Economic Cycle")
st.dataframe(average_returns)

# Display best and worst sectors
st.markdown("### Summary")
for cycle in average_returns.index:
    st.write(f"**{cycle}:**")
    st.write(f"- Best Performing Sector: {best_sectors[cycle]} with an average return of {average_returns.loc[cycle, best_sectors[cycle]]:.2f}")
    st.write(f"- Worst Performing Sector: {worst_sectors[cycle]} with an average return of {average_returns.loc[cycle, worst_sectors[cycle]]:.2f}")

#Section 5: Economic Cycle Transitions
st.header("Economic Cycle Transitions Over Time")

# Prepare data for plotting
economic_cycles = combined_data[['Economic Cycle']].copy()
economic_cycles['Cycle Code'] = economic_cycles['Economic Cycle'].map({
    'Expansion': 1,
    'Neutral': 0,
    'Contraction': -1,
    'Unknown': None  # Exclude "Unknown" if not needed
})
economic_cycles.dropna(subset=['Cycle Code'], inplace=True)

# Plot transitions
if st.checkbox("Show Economic Cycle Transitions"):
    plt.figure(figsize=(12, 6))
    plt.plot(economic_cycles.index, economic_cycles['Cycle Code'], drawstyle='steps-post', label="Economic Cycle")
    plt.axhline(y=0, color='gray', linestyle='--', linewidth=0.5, label='Neutral')
    plt.axhline(y=1, color='green', linestyle='--', linewidth=0.5, label='Expansion')
    plt.axhline(y=-1, color='red', linestyle='--', linewidth=0.5, label='Contraction')
    plt.title("Economic Cycle Transitions")
    plt.xlabel("Date")
    plt.ylabel("Economic Cycle")
    plt.yticks([-1, 0, 1], ['Contraction', 'Neutral', 'Expansion'])
    plt.legend()
    st.pyplot(plt)
