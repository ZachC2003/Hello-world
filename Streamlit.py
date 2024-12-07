import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# Load Data
@st.cache_data
def load_data():
    return pd.read_csv("final_valuation_results_with_prices.csv")

valuation_results = load_data()

# Sidebar: Stock Selection Filter
st.sidebar.header("Filter Stocks")
selected_tickers = st.sidebar.multiselect(
    "Select Tickers to Include",
    options=valuation_results["Ticker"].unique(),
    default=valuation_results["Ticker"].unique()
)

# Filter Data Globally
filtered_data = valuation_results[valuation_results["Ticker"].isin(selected_tickers)]

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Overview", "DCF Model", "CCA Model", "DDM Model", "Comparison", "Valuation Gap Analysis", "Correlation Matrix"])

# Home Page
if page == "Home":
    st.title("Stock Valuation Dashboard")
    st.write(
        """
        Welcome to the Stock Valuation Dashboard! This tool evaluates stocks using 
        Discounted Cash Flow (DCF), Comparable Company Analysis (CCA), and Dividend 
        Discount Model (DDM).
        
        **Choose stocks to analyze using the filter in the sidebar.**
        """
    )
    
    # Opening Image
    image = Image.open("C:/Users/Zachary Cheney/OneDrive - University of Arkansas/Fall 2024/advanced financial modeling/90ea43f5-5f7a-4e48-9de7-6dcb015703ef.webp")  # Replace with your own image file
    st.image(image, caption="Stock Analysis Dashboard", use_container_width=True)

    st.markdown("### Selected Stocks")
    st.dataframe(filtered_data)

# Overview Page
elif page == "Overview":
    st.title("Overview of Results")
    st.write(
        """
        This page provides an overview of the valuation results for the selected stocks.
        You can explore the dataset and analyze summary statistics.
        """
    )
    st.markdown("### Full Dataset")
    st.dataframe(filtered_data)

    st.markdown("### Summary Statistics")
    st.write(filtered_data.describe())

# DCF Model Page
elif page == "DCF Model":
    st.title("Discounted Cash Flow (DCF) Model")
    st.write(
        """
        The DCF model estimates a stock's intrinsic value based on future cash flows. 
        This model works best for companies with stable cash flow projections.

        **Note:** The intrinsic values shown on the graph are scaled to a range of 0 to 1. 
        This allows for easier comparison across companies and highlights relative differences.
        """
    )
    fig = px.bar(
        filtered_data,
        x="Ticker",
        y="Intrinsic Value per Share",
        title="DCF Model: Scaled Intrinsic Value per Share",
        labels={"Intrinsic Value per Share": "Scaled Intrinsic Value", "Ticker": "Company"},
        color="Ticker"
    )
    st.plotly_chart(fig)

    st.markdown("### Insights")
    st.write(f"The DCF model predicts the intrinsic value of stocks based on future cash flow. The highest-valued stock is {filtered_data.loc[filtered_data['Intrinsic Value per Share'].idxmax(), 'Ticker']}.")

# CCA Model Page
elif page == "CCA Model":
    st.title("Comparable Company Analysis (CCA) Model")
    st.write(
        """
        The CCA model compares a company's valuation to its peers using metrics like 
        P/E (Price-to-Earnings) and EV/EBITDA (Enterprise Value to EBITDA).

        **Note:** The P/E valuations shown on the graph are scaled to a range of 0 to 1 
        for better visualization and comparison.
        """
    )
    fig = px.bar(
        filtered_data,
        x="Ticker",
        y="P/E Valuation",
        title="CCA Model: Scaled P/E Valuation",
        labels={"P/E Valuation": "Scaled Valuation", "Ticker": "Company"},
        color="Ticker"
    )
    st.plotly_chart(fig)

    st.markdown("### Insights")
    st.write(f"The CCA model shows that {filtered_data.loc[filtered_data['P/E Valuation'].idxmax(), 'Ticker']} has the highest valuation based on peer multiples.")

# DDM Model Page
elif page == "DDM Model":
    st.title("Dividend Discount Model (DDM)")
    st.write(
        """
        The DDM model calculates intrinsic value based on dividend payments and growth rates. 
        It is ideal for companies with consistent dividend histories.

        **Note:** The intrinsic values displayed on the graph are scaled to a range of 0 to 1 
        to standardize comparisons and make visual analysis more intuitive.
        """
    )
    fig = px.bar(
        filtered_data,
        x="Ticker",
        y="Intrinsic Value",
        title="DDM Model: Scaled Intrinsic Value",
        labels={"Intrinsic Value": "Scaled Valuation", "Ticker": "Company"},
        color="Ticker"
    )
    st.plotly_chart(fig)

    st.markdown("### Insights")
    st.write(f"The DDM model values {filtered_data.loc[filtered_data['Intrinsic Value'].idxmax(), 'Ticker']} the highest among the dividend-paying stocks.")

# Comparison Page
elif page == "Comparison":
    st.title("Weighted Valuation Comparison")
    
    # Explanation of the Weighted Valuation
    st.markdown("""
    ### How the Weighted Valuation is Calculated
    The **Weighted Valuation** combines insights from the three valuation models: 
    - **DCF (Discounted Cash Flow)**: Focuses on future cash flows discounted to the present.
    - **CCA (Comparable Company Analysis)**: Uses industry multiples like P/E and EV/EBITDA to assess valuation.
    - **DDM (Dividend Discount Model)**: Evaluates dividend-paying stocks based on expected dividends.

    ### Interpretation of Rankings:
    The higher the **Weighted Valuation**, the better the overall outlook of the stock based on the combined models. 
    Use this ranking to identify stocks that stand out based on their overall valuation.
    """)

    # Sort the data by Weighted Valuation in descending order
    sorted_data = filtered_data.sort_values(by="Weighted Valuation", ascending=False)

    # Weighted Valuation Chart
    fig = px.bar(
        sorted_data,
        x="Ticker",
        y="Weighted Valuation",
        title="Weighted Valuation Ranking Across Models",
        labels={"Weighted Valuation": "Valuation ($)", "Ticker": "Company"},
        color="Ticker"  # Assign unique colors for each company
    )
    st.plotly_chart(fig)

    # Display Sorted Weighted Valuation Table
    st.markdown("### Weighted Valuation Results (Ranked)")
    st.write(sorted_data[["Ticker", "Weighted Valuation"]])

# Valuation Gap Analysis Page
elif page == "Valuation Gap Analysis":
    st.title("Valuation Gap Analysis")
    st.write("""
    This analysis compares the normalized current price to the normalized weighted valuation 
    to calculate a Valuation Gap Ratio, offering additional insights into stock valuation.
    """)

    # Explanation of Valuation Gap Ratio Calculation
    st.markdown("""
    ### How the Valuation Gap Ratio is Calculated:
    1. **Normalize Data**:
       - **Current Price**: Normalized between 0 and 1 based on the range of prices across all selected stocks.
         \[
         \text{Normalized Current Price} = \frac{\text{Current Price} - \text{Min Price}}{\text{Max Price} - \text{Min Price}}
         \]
       - **Weighted Valuation**: Normalized between 0 and 1 based on the range of weighted valuations across all selected stocks.
         \[
         \text{Normalized Weighted Valuation} = \frac{\text{Weighted Valuation} - \text{Min Weighted Valuation}}{\text{Max Weighted Valuation} - \text{Min Weighted Valuation}}
         \]

    2. **Valuation Gap Ratio**:
       - Compares the **Normalized Current Price** with the **Normalized Weighted Valuation**.
         \[
         \text{Valuation Gap Ratio} = \frac{\text{Normalized Current Price} - \text{Normalized Weighted Valuation}}{\text{Normalized Weighted Valuation}}
         \]

    3. **Categorization**:
       - **Overvalued**: If the Valuation Gap Ratio is **positive**, indicating the stock’s current price exceeds its weighted valuation.
       - **Undervalued**: If the Valuation Gap Ratio is **negative**, suggesting the stock is priced below its weighted valuation.

    ### Insights and Interpretation:
    - **Overvalued Stocks**: These have a higher normalized current price compared to their weighted valuation, signaling they may be overpriced based on the combined valuation models.
    - **Undervalued Stocks**: These show a lower normalized current price compared to their weighted valuation, potentially indicating investment opportunities.
    """)

    # Normalize Current Price and Weighted Valuation
    min_price, max_price = filtered_data["Current Price"].min(), filtered_data["Current Price"].max()
    filtered_data["Normalized Current Price"] = (
        (filtered_data["Current Price"] - min_price) / (max_price - min_price)
    )

    min_valuation, max_valuation = filtered_data["Weighted Valuation"].min(), filtered_data["Weighted Valuation"].max()
    filtered_data["Normalized Weighted Valuation"] = (
        (filtered_data["Weighted Valuation"] - min_valuation) / (max_valuation - min_valuation)
    )

    # Calculate Valuation Gap Ratio
    filtered_data["Valuation Gap Ratio"] = (
        (filtered_data["Normalized Current Price"] - filtered_data["Normalized Weighted Valuation"]) /
        filtered_data["Normalized Weighted Valuation"]
    )

    # Categorize Stocks
    filtered_data["Valuation Category"] = filtered_data["Valuation Gap Ratio"].apply(
        lambda x: "Overvalued" if x > 0 else "Undervalued"
    )

    # Sort Data
    sorted_data = filtered_data.sort_values(by="Valuation Gap Ratio", ascending=False)

    # Display Results
    st.markdown("### Valuation Gap Ratio Results (Normalized)")
    st.write(sorted_data[[
        "Ticker", "Normalized Weighted Valuation", "Normalized Current Price", "Valuation Gap Ratio", "Valuation Category"
    ]])

    # Visualization
    fig = px.bar(
        sorted_data,
        x="Ticker",
        y="Valuation Gap Ratio",
        title="Normalized Valuation Gap Ratio Across Stocks",
        labels={"Valuation Gap Ratio": "Valuation Gap", "Ticker": "Company"},
        color="Valuation Category"
    )
    st.plotly_chart(fig)

# Correlation Matrix Page
elif page == "Correlation Matrix":
    st.title("Correlation Matrix")
    st.write(
        """
        This page analyzes the correlation between the valuation models (DCF, CCA, and DDM). 
        High correlations indicate that the models are aligned in their evaluations.
        """
    )
    correlation_matrix = filtered_data[[
        "Intrinsic Value per Share", "P/E Valuation", "Intrinsic Value", "Weighted Valuation"
    ]].corr()

    st.markdown("### Correlation Heatmap")
    fig = px.imshow(
        correlation_matrix,
        title="Correlation Between Models",
        labels=dict(x="Metrics", y="Metrics", color="Correlation"),
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig)
