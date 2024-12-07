import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
@st.cache_data
def load_data():
    return pd.read_csv(
        "C:/Users/Zachary Cheney/OneDrive - University of Arkansas/Fall 2024/advanced financial modeling/Hello-world/Personal_AVF_Project/features.csv",
        index_col=0,
        skiprows=1  # Skip the comment row
    )

# Main app function
def main():
    st.set_page_config(page_title="Stock Scoring Dashboard", layout="wide")
    st.title("Stock Scoring Dashboard")
    st.sidebar.title("Navigation")

    # Navigation options
    page = st.sidebar.radio(
        "Go to",
        [
            "Stock Selection", 
            "Top Ranked Stocks", 
            "Growth vs. Stability Scores", 
            "Category Comparison"
        ]
    )

    # Load the data
    features = load_data()

    # Sidebar: Stock Selection Filters (Shared Across Pages)
    st.sidebar.header("Filter Options")
    category_filter = st.sidebar.multiselect(
        "Select Categories",
        options=features['Category'].unique(),
        default=features['Category'].unique()
    )
    min_weighted_score = st.sidebar.slider(
        "Minimum Weighted Score",
        min_value=float(features['Weighted Score'].min()),
        max_value=float(features['Weighted Score'].max()),
        value=float(features['Weighted Score'].min())
    )

    # Apply filters
    filtered_data = features[
        (features['Category'].isin(category_filter)) & 
        (features['Weighted Score'] >= min_weighted_score)
    ]

    # Page 1: Stock Selection
    if page == "Stock Selection":
        st.subheader("Stock Selection")

        # Dropdown for default stock selection
        available_stocks = features.index.tolist()
        selected_stocks_dropdown = st.multiselect(
            "Select stocks from the dropdown:",
            options=available_stocks,
            default=available_stocks
        )

        # Text input for custom stock tickers
        st.write("Alternatively, you can enter custom stock tickers (comma-separated):")
        default_tickers = ",".join(selected_stocks_dropdown)
        custom_stock_input = st.text_input(
            "Enter custom stock tickers:",
            value=default_tickers
        )

        # Process user-provided stocks
        selected_stocks = [ticker.strip().upper() for ticker in custom_stock_input.split(",")]
        filtered_features = filtered_data[filtered_data.index.isin(selected_stocks)]

        st.success(f"{len(filtered_features)} stocks selected.")
        st.write("Here are the selected stocks:")
        st.dataframe(filtered_features)

    # Page 2: Top Ranked Stocks
    elif page == "Top Ranked Stocks":
        st.subheader("Top Ranked Stocks")

        # Top ranked stocks by Adjusted Weighted Score
        top_stocks = filtered_data.sort_values(by="Adjusted Weighted Score", ascending=False).head(10)
        fig = px.bar(
            top_stocks,
            x=top_stocks.index,
            y="Adjusted Weighted Score",
            color="Category",
            title="Top 10 Stocks by Weighted Score",
            labels={"x": "Ticker", "y": "Adjusted Weighted Score"}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Display table of top-ranked stocks
        st.subheader("Top Ranked Stocks Data")
        st.dataframe(top_stocks)

    # Page 3: Growth vs. Stability Scores
    elif page == "Growth vs. Stability Scores":
        st.subheader("Growth vs. Stability Scores Insights")

        # Customization options for the scatter plot
        st.sidebar.header("Scatter Plot Options")
        bubble_color = st.sidebar.selectbox(
            "Choose Bubble Color By:",
            options=["Category", "Rank", "Adjusted Weighted Score"],
            index=0
        )
        show_trend_line = st.sidebar.checkbox("Show Trend Line", value=False)

        # Section 1: Main Scatter Plot
        st.write("### Overall Growth vs. Stability Scores")
        fig = px.scatter(
            filtered_data,
            x="Growth Score",
            y="Stability Score",
            color=bubble_color,
            size="Adjusted Weighted Score",
            hover_name=filtered_data.index,
            title="Growth Potential vs. Long-Term Stability",
            labels={"x": "Growth Score", "y": "Stability Score"},
            trendline="ols" if show_trend_line else None  # Add trend line if enabled
        )
        st.plotly_chart(fig, use_container_width=True)

        # Section 2: Separate Scatter Plots for Each Category
        st.write("### Category-Specific Growth vs. Stability")
        categories = filtered_data["Category"].unique()
        for category in categories:
            st.write(f"#### {category} Stocks")
            category_data = filtered_data[filtered_data["Category"] == category]
            fig = px.scatter(
                category_data,
                x="Growth Score",
                y="Stability Score",
                color="Adjusted Weighted Score",
                size="Adjusted Weighted Score",
                hover_name=category_data.index,
                title=f"Growth vs. Stability for {category} Stocks",
                labels={"x": "Growth Score", "y": "Stability Score"}
            )
            st.plotly_chart(fig, use_container_width=True)

        # Section 3: Top Performers and Outliers
        st.write("### Top Performers and Outliers")
        top_growth = filtered_data.sort_values(by="Growth Score", ascending=False).head(5)
        top_stability = filtered_data.sort_values(by="Stability Score", ascending=False).head(5)
        st.write("#### Top 5 Stocks by Growth Score")
        st.dataframe(top_growth)
        st.write("#### Top 5 Stocks by Stability Score")
        st.dataframe(top_stability)

        # Section 4: Distribution of Scores
        st.write("### Score Distributions")
        st.write("#### Distribution of Growth Scores")
        fig = px.histogram(
            filtered_data,
            x="Growth Score",
            color="Category",
            title="Distribution of Growth Scores by Category",
            labels={"x": "Growth Score", "y": "Count"}
        )
        st.plotly_chart(fig, use_container_width=True)

        st.write("#### Distribution of Stability Scores")
        fig = px.histogram(
            filtered_data,
            x="Stability Score",
            color="Category",
            title="Distribution of Stability Scores by Category",
            labels={"x": "Stability Score", "y": "Count"}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Section 5: Correlation Analysis
        st.write("### Correlation Between Metrics")
        correlation_matrix = filtered_data[["Growth Score", "Stability Score", "Adjusted Weighted Score"]].corr()
        fig = px.imshow(
            correlation_matrix,
            text_auto=True,
            title="Correlation Between Growth, Stability, and Weighted Scores",
            labels={"color": "Correlation"}
        )
        st.plotly_chart(fig, use_container_width=True)

    # Page 4: Category Comparison
    elif page == "Category Comparison":
        st.subheader("Category Comparison")

        # Summary statistics for each category
        summary_stats = filtered_data.groupby("Category").mean()[["Growth Score", "Stability Score", "Adjusted Weighted Score"]]
        st.write("**Summary Statistics by Category:**")
        st.dataframe(summary_stats)

        # Grouped bar chart for category comparison
        st.write("**Category Comparison Chart:**")
        fig = px.bar(
            summary_stats.reset_index(),
            x="Category",
            y=["Growth Score", "Stability Score", "Adjusted Weighted Score"],
            barmode="group",
            title="Comparison of Key Metrics by Category",
            labels={"value": "Score", "variable": "Metric"}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Optional: Separate charts for each category
        st.write("**Detailed Charts for Each Category:**")
        for category in filtered_data["Category"].unique():
            st.write(f"**{category} Stocks:**")
            category_data = filtered_data[filtered_data["Category"] == category]
            fig = px.bar(
                category_data,
                x=category_data.index,
                y=["Growth Score", "Stability Score", "Adjusted Weighted Score"],
                barmode="group",
                title=f"{category} Stocks - Key Metrics",
                labels={"value": "Score", "variable": "Metric"}
            )
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
