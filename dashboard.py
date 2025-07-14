# --------------------------------------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import duckdb
from datetime import datetime, timedelta

from streamlit.components.v1 import html

# --- Configuration ---
FILE_NAME = 'user_risk_analysis.csv'
DATE_COLUMN = 'date'
RISK_LEVEL_ORDER = ['Low', 'Medium', 'High'] # Define order for risk levels
RISK_LEVEL_COLORS = {
    'Low': '#28a745',    # Green
    'Medium': '#ffc107', # Yellow/Orange
    'High': '#dc3545'    # Red
}

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="User Risk Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    # Theme settings for a more professional look
    # You can customize these colors further
    # primaryColor='#4CAF50', # A nice green
    # backgroundColor='#F0F2F6', # Light grey background
    # secondaryBackgroundColor='#FFFFFF', # White for components
    # textColor='#262730' # Dark text
)

# --- Custom CSS for enhanced styling ---
st.markdown("""
<style>
    /* Main container styling */
    .css-1d391kg {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Header styling */
    h1 {
        color: #1E90FF; /* Dodger Blue */
        text-align: center;
        font-size: 2.5em;
        margin-bottom: 0.5em;
    }
    h2, h3, h4 {
        color: #4682B4; /* Steel Blue */
    }
    /* Info/Warning boxes */
    .stAlert {
        border-radius: 10px;
        padding: 1rem;
    }
    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #f0f2f6; /* Light grey background */
        border-left: 5px solid #1E90FF; /* Blue border */
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
    }
    [data-testid="stMetricLabel"] {
        font-weight: bold;
        color: #4682B4;
    }
    [data-testid="stMetricValue"] {
        color: #1E90FF;
    }
    /* Sidebar styling */
    .css-1lcbmhc { /* Sidebar background */
        background-color: #e0e6ed; /* Slightly darker grey for sidebar */
        border-right: 1px solid #c0c0c0;
    }
    .css-1lcbmhc .stButton > button { /* Sidebar buttons */
        border-radius: 8px;
        border: 1px solid #1E90FF;
        color: #1E90FF;
        background-color: white;
    }
    .css-1lcbmhc .stButton > button:hover {
        background-color: #1E90FF;
        color: white;
    }
    /* Tabs styling */
    .stTabs [data-testid="stTab"] {
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        margin-right: 5px;
        padding: 10px 20px;
        font-weight: bold;
        color: #4682B4;
    }
    .stTabs [data-testid="stTab"][aria-selected="true"] {
        background-color: #1E90FF;
        color: white;
        border-bottom: 3px solid #1E90FF;
    }
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden; /* Ensures rounded corners apply to content */
    }
</style>
""", unsafe_allow_html=True)


# --- DuckDB Connection and Data Loading (Cached Resource) ---
@st.cache_resource(ttl=3600) # Cache the DuckDB connection and initial table load
def get_duckdb_connection(file_path):
    """
    Establishes a DuckDB connection and loads the CSV into a table.
    This function runs only once.
    """
    try:
        con = duckdb.connect(database=':memory:', read_only=False)
        # Use DuckDB's COPY FROM for efficient CSV loading
        # Auto-detects types, but we can cast later if needed
        #st.info(f"Loading '{file_path}' into DuckDB... This might take a moment.")
        con.execute(f"CREATE TABLE user_data AS SELECT * FROM '{file_path}'")
        
        # Cast 'date' column to DATE type for proper filtering
        con.execute(f"ALTER TABLE user_data ALTER COLUMN {DATE_COLUMN} TYPE DATE;")
        
        # Ensure risk_level is treated as an ordered category for sorting
        # DuckDB handles string comparisons, but for explicit order in charts, pandas will re-order
        
        #st.success("Data loaded into DuckDB successfully!")
        return con
    except Exception as e:
        st.error(f"An error occurred while setting up DuckDB or loading data: {e}")
        st.stop()

# --- Main Application Logic ---

st.title("🛡 User Risk Analysis Dashboard")
#st.markdown("""
#This dashboard provides insights into user activity and associated risk levels.
#It uses DuckDB for efficient querying of large datasets.
# """)

# st.warning(f"""
# Performance Note:
# This dashboard leverages DuckDB to efficiently handle your ~4.3 million rows from '{FILE_NAME}'.
# The data is loaded into an in-memory DuckDB database once, and all subsequent operations
# are performed via fast SQL queries. This significantly improves performance compared to
# loading the entire CSV into Pandas directly for every interaction.
# """)

# Get DuckDB connection
con = get_duckdb_connection(FILE_NAME)
if con is None: # Stop if connection failed
    st.stop()

# Get min/max dates from DuckDB
min_date_str = con.execute(f"SELECT MIN({DATE_COLUMN}) FROM user_data").fetchone()[0]
max_date_str = con.execute(f"SELECT MAX({DATE_COLUMN}) FROM user_data").fetchone()[0]
min_date = datetime.strptime(str(min_date_str), '%Y-%m-%d').date()
max_date = datetime.strptime(str(max_date_str), '%Y-%m-%d').date()

# --- Sidebar Filters ---
st.sidebar.header("📊 Filters")

# Date Range Filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Initialize query conditions
query_conditions = []
if len(date_range) == 2:
    start_date, end_date = date_range
    query_conditions.append(f"{DATE_COLUMN} >= '{start_date}' AND {DATE_COLUMN} <= '{end_date}'")
else:
    st.sidebar.warning("Please select a valid date range.")

# User Filter
# Fetch distinct users for the filter (can be slow for millions of users, consider top N or search)
# For very large number of users, a search box is more practical than a multiselect
all_users_query = f"SELECT DISTINCT user FROM user_data {'WHERE ' + ' AND '.join(query_conditions) if query_conditions else ''} ORDER BY user"
all_users_df = con.execute(all_users_query).fetchdf()
all_users = all_users_df['user'].tolist()

selected_users = st.sidebar.multiselect(
    "Select User(s)",
    options=all_users,
    default=all_users if len(all_users) < 1000 else [] # Default to all if less than 1000, else none
)
if selected_users:
    user_list_str = ", ".join(f"'{u}'" for u in selected_users)
    query_conditions.append(f"user IN ({user_list_str})")
elif not all_users: # If no users are found after date filter
    st.warning("No users found for the selected date range. Please adjust filters.")
    st.stop()

# Risk Level Filter
selected_risk_levels = st.sidebar.multiselect(
    "Select Risk Level(s)",
    options=RISK_LEVEL_ORDER,
    default=RISK_LEVEL_ORDER # Select all by default
)
if selected_risk_levels:
    risk_level_list_str = ", ".join(f"'{rl}'" for rl in selected_risk_levels)
    query_conditions.append(f"risk_level IN ({risk_level_list_str})")

# Spike Flags Filter
st.sidebar.subheader("Anomaly Flags")
filter_logon_spike = st.sidebar.checkbox("Logon Spike", value=False)
filter_http_spike = st.sidebar.checkbox("HTTP Spike", value=False)
filter_device_spike = st.sidebar.checkbox("Device Spike", value=False)

if filter_logon_spike:
    query_conditions.append("logon_spike = TRUE")
if filter_http_spike:
    query_conditions.append("http_spike = TRUE")
if filter_device_spike:
    query_conditions.append("device_spike = TRUE")

# Construct the WHERE clause
where_clause = ""
if query_conditions:
    where_clause = "WHERE " + " AND ".join(query_conditions)

# --- Fetch Filtered Data for KPIs and Charts ---
# Use a common query prefix for efficiency
base_query = f"SELECT * FROM user_data {where_clause}"

# Check if filtered data is empty before fetching
count_query = f"SELECT COUNT(*) FROM user_data {where_clause}"
filtered_row_count = con.execute(count_query).fetchone()[0]

if filtered_row_count == 0:
    st.warning("No data matches the selected filters. Please adjust your selections.")
    st.stop() # Stop execution if no data to display

# Fetch data for KPIs (only necessary aggregates)
kpi_query = f"""
    SELECT
        COUNT(DISTINCT user) AS total_unique_users,
        SUM(CASE WHEN risk_level = 'High' THEN 1 ELSE 0 END) AS total_high_risk_events,
        AVG(risk_score) AS avg_risk_score
    FROM user_data {where_clause}
"""
kpi_data = con.execute(kpi_query).fetchdf().iloc[0]

# --- Main Content Area ---

st.subheader(f"Filtered Data Overview (Showing {filtered_row_count:,} records)")

# Key Performance Indicators (KPIs)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Unique Users", f"{int(kpi_data['total_unique_users']):,}")
with col2:
    st.metric("High Risk Events", f"{int(kpi_data['total_high_risk_events']):,}")
with col3:
    st.metric("Avg. Risk Score", f"{kpi_data['avg_risk_score']:.2f}")
with col4:
    st.markdown(f"""
        <div style='background-color: #f0f2f6; border-left: 5px solid #1E90FF;
                    border-radius: 10px; padding: 15px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);'>
            <div style='font-weight: bold; color: #4682B4;'>Data Range</div>
            <div style='color: #1E90FF; font-size: 2rem; line-height: 1.3;'>
                {start_date.strftime('%Y-%m')}<br>to<br>{end_date.strftime('%Y-%m')}
            </div>
        </div>
    """, unsafe_allow_html=True)




# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🚨 Detailed Flagged Events", "📈 Activity Trends", "📥 Export Data"])

with tab1:
    st.header("Overview & Summary")

    # Risk Level Distribution
    risk_level_counts_query = f"""
        SELECT risk_level, COUNT(*) AS count
        FROM user_data {where_clause}
        GROUP BY risk_level
        ORDER BY CASE
            WHEN risk_level = 'Low' THEN 1
            WHEN risk_level = 'Medium' THEN 2
            WHEN risk_level = 'High' THEN 3
            ELSE 4
        END
    """
    risk_level_counts_df = con.execute(risk_level_counts_query).fetchdf()
    
    # Ensure all risk levels are present for consistent coloring, even if count is 0
    full_risk_levels_df = pd.DataFrame({'risk_level': RISK_LEVEL_ORDER})
    risk_level_counts_df = pd.merge(full_risk_levels_df, risk_level_counts_df, on='risk_level', how='left').fillna(0)
    
    fig_risk_dist = px.bar(
        risk_level_counts_df,
        x='risk_level',
        y='count',
        title='Distribution of Risk Levels',
        labels={'risk_level': 'Risk Level', 'count': 'Number of Events'},
        color='risk_level',
        color_discrete_map=RISK_LEVEL_COLORS,
        template="plotly_white" # Use a clean white template
    )
    fig_risk_dist.update_layout(xaxis={'categoryorder':'array', 'categoryarray':RISK_LEVEL_ORDER})
    st.plotly_chart(fig_risk_dist, use_container_width=True)

    # Time Series of High Risk Events
    high_risk_daily_query = f"""
        SELECT {DATE_COLUMN}, COUNT(*) AS count
        FROM user_data
        {where_clause + (' AND risk_level = \'High\'' if where_clause else 'WHERE risk_level = \'High\'')}
        GROUP BY {DATE_COLUMN}
        ORDER BY {DATE_COLUMN}
    """
    df_high_risk_daily = con.execute(high_risk_daily_query).fetchdf()
    
    if not df_high_risk_daily.empty:
        fig_time_series = px.line(
            df_high_risk_daily,
            x=DATE_COLUMN,
            y='count',
            title='Daily High Risk Events Over Time',
            labels={'count': 'Number of High Risk Events', DATE_COLUMN: 'Date'},
            color_discrete_sequence=[RISK_LEVEL_COLORS['High']], # Use High risk color
            template="plotly_white"
        )
        st.plotly_chart(fig_time_series, use_container_width=True)
    else:
        st.info("No high-risk events found for time series analysis with current filters.")

    # Top 10 Users by High Risk Events
    top_users_query = f"""
        SELECT user, COUNT(*) AS "High Risk Events"
        FROM user_data
        {where_clause + (' AND risk_level = \'High\'' if where_clause else 'WHERE risk_level = \'High\'')}
        GROUP BY user
        ORDER BY "High Risk Events" DESC
        LIMIT 10
    """
    top_users_high_risk = con.execute(top_users_query).fetchdf()

    if not top_users_high_risk.empty:
        fig_top_users = px.bar(
            top_users_high_risk,
            x='High Risk Events',
            y='user',
            orientation='h',
            title='Top 10 Users by High Risk Events',
            labels={'High Risk Events': 'Number of High Risk Events', 'user': 'User ID'},
            color_discrete_sequence=['#4682B4'], # Steel Blue
            template="plotly_white"
        )
        fig_top_users.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_top_users, use_container_width=True)
    else:
        st.info("No high-risk events found for top user analysis with current filters.")

    # Risk Score Distribution (Histogram)
    risk_score_query = f"SELECT risk_score FROM user_data {where_clause}"
    df_risk_scores = con.execute(risk_score_query).fetchdf()
    
    if not df_risk_scores.empty:
        fig_risk_score_dist = px.histogram(
            df_risk_scores,
            x='risk_score',
            nbins=50,
            title='Distribution of Risk Scores',
            labels={'risk_score': 'Risk Score', 'count': 'Number of Events'},
            color_discrete_sequence=['#1E90FF'], # Dodger Blue
            template="plotly_white"
        )
        st.plotly_chart(fig_risk_score_dist, use_container_width=True)
    else:
        st.info("No risk score data to display with current filters.")


with tab2:
    st.header("Detailed Flagged Events")
    st.markdown("Displaying a sample of up to 1000 high-risk or medium-risk events based on your filters.")

    # Fetch flagged events (limit to 1000 for display)
    flagged_details_query = f"""
        SELECT
            {DATE_COLUMN}, user, risk_level, risk_score,
            logon_count, http_requests, device_activity_count,
            logon_spike, http_spike, device_spike,
            hour, weekday
        FROM user_data
        {where_clause + (' AND risk_level IN (\'High\', \'Medium\')' if where_clause else 'WHERE risk_level IN (\'High\', \'Medium\')')}
        ORDER BY risk_score DESC
        LIMIT 1000
    """
    df_flagged_details = con.execute(flagged_details_query).fetchdf()

    if df_flagged_details.empty:
        st.info("No High or Medium risk events to display with current filters.")
    else:
        # Custom styling for risk_level column in dataframe
        def color_risk_level(val):
            color = RISK_LEVEL_COLORS.get(val, 'black')
            return f'background-color: {color}; color: white; border-radius: 5px; padding: 2px 5px;'

        st.dataframe(
            df_flagged_details.style.applymap(
                color_risk_level, subset=['risk_level']
            ),
            use_container_width=True,
            height=500 # Fixed height for scrollability
        )
        if filtered_row_count > 1000: # Use overall filtered count, not just flagged
            st.info(f"Showing the top 1000 events by risk score. Apply more filters to see specific events.")

with tab3:
    st.header("Activity Trends")

    # Aggregate data daily for trend analysis
    daily_agg_query = f"""
        SELECT
            {DATE_COLUMN},
            SUM(logon_count) AS logon_count,
            SUM(http_requests) AS http_requests,
            SUM(device_activity_count) AS device_activity_count
        FROM user_data {where_clause}
        GROUP BY {DATE_COLUMN}
        ORDER BY {DATE_COLUMN}
    """
    df_daily_agg = con.execute(daily_agg_query).fetchdf()

    if not df_daily_agg.empty:
        # Logon Count Trend
        fig_logon_trend = px.line(
            df_daily_agg,
            x=DATE_COLUMN,
            y='logon_count',
            title='Daily Logon Count Trend',
            labels={'logon_count': 'Total Logon Count', DATE_COLUMN: 'Date'},
            color_discrete_sequence=['#FF6347'], # Tomato
            template="plotly_dark" # Changed to plotly_dark
        )
        st.plotly_chart(fig_logon_trend, use_container_width=True)

        # HTTP Requests Trend
        # fig_http_trend = px.line(
        #     df_daily_agg,
        #     x=DATE_COLUMN,
        #     y='http_requests',
        #     title='Daily HTTP Requests Trend',
        #     labels={'http_requests': 'Total HTTP Requests', DATE_COLUMN: 'Date'},
        #     color_discrete_sequence=['#4682B4'], # Steel Blue
        #     template="plotly_dark" # Changed to plotly_dark
        # )
        # st.plotly_chart(fig_http_trend, use_container_width=True)

        # Device Activity Count Trend
        fig_device_trend = px.line(
            df_daily_agg,
            x=DATE_COLUMN,
            y='device_activity_count',
            title='Daily Device Activity Count Trend',
            labels={'device_activity_count': 'Total Device Activity Count', DATE_COLUMN: 'Date'},
            color_discrete_sequence=['#3CB371'], # Medium Sea Green
            template="plotly_dark" # Changed to plotly_dark
        )
        st.plotly_chart(fig_device_trend, use_container_width=True)
    else:
        st.info("No daily activity data to display with current filters.")
    
    st.markdown("---") # Separator for pie charts below

    # Pie Chart: High Risk Events by Hour
    high_risk_by_hour_query = f"""
        SELECT hour, COUNT(*) AS count
        FROM user_data
        {where_clause + (' AND risk_level = \'High\'' if where_clause else 'WHERE risk_level = \'High\'')}
        GROUP BY hour
        ORDER BY hour
    """
    df_high_risk_by_hour = con.execute(high_risk_by_hour_query).fetchdf()

    if not df_high_risk_by_hour.empty:
        fig_hour_pie = px.pie(
            df_high_risk_by_hour,
            names='hour',
            values='count',
            title='High Risk Events by Hour of Day',
            hole=.4, # Donut chart
            color_discrete_sequence=px.colors.sequential.Plasma_r, # A nice color sequence
            template="plotly_dark"
        )
        st.plotly_chart(fig_hour_pie, use_container_width=True)
    else:
        st.info("No high-risk events to analyze by hour with current filters.")

    # Pie Chart: High Risk Events by Weekday
    high_risk_by_weekday_query = f"""
        SELECT weekday, COUNT(*) AS count
        FROM user_data
        {where_clause + (' AND risk_level = \'High\'' if where_clause else 'WHERE risk_level = \'High\'')}
        GROUP BY weekday
        ORDER BY weekday
    """
    df_high_risk_by_weekday = con.execute(high_risk_by_weekday_query).fetchdf()

    if not df_high_risk_by_weekday.empty:
        # Map weekday numbers to names for better readability
        weekday_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
        df_high_risk_by_weekday['weekday_name'] = df_high_risk_by_weekday['weekday'].map(weekday_map)

        fig_weekday_pie = px.pie(
            df_high_risk_by_weekday,
            names='weekday_name',
            values='count',
            title='High Risk Events by Day of Week',
            hole=.4, # Donut chart
            color_discrete_sequence=px.colors.sequential.Viridis, # Another nice color sequence
            template="plotly_dark"
        )
        st.plotly_chart(fig_weekday_pie, use_container_width=True)
    else:
        st.info("No high-risk events to analyze by weekday with current filters.")


# with tab4:
#     st.header("Export Filtered Data")
#     st.markdown("Download the data currently displayed based on your filters.")

#     # Fetch all filtered data for export (no limit)
#     df_export = con.execute(base_query).fetchdf()

#     if not df_export.empty:
#         csv_export = df_export.to_csv(index=False).encode('utf-8')
#         st.download_button(
#             label="Download Filtered Data as CSV",
#             data=csv_export,
#             file_name="filtered_user_risk_analysis.csv",
#             mime="text/csv",
#             help="Downloads the data visible after applying filters."
#         )

#         # To use to_excel, you need the 'xlsxwriter' engine, which is installed with openpyxl
#         excel_export = df_export.to_excel(index=False, engine='xlsxwriter')
#         st.download_button(
#             label="Download Filtered Data as Excel",
#             data=excel_export,
#             file_name="filtered_user_risk_analysis.xlsx",
#             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#             help="Downloads the data visible after applying filters."
#         )
#     else:
#         st.info("No data to export with the current filters.")

from io import BytesIO

with tab4:
    st.header("📥 Export Filtered Data")
    st.markdown("Download the currently filtered dataset.")

    df_export = con.execute(base_query).fetchdf()

    if not df_export.empty:
        # CSV Export
        csv_export = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇ Download as CSV",
            data=csv_export,
            file_name="filtered_user_risk_analysis.csv",
            mime="text/csv"
        )

        # Excel Export using openpyxl instead of xlsxwriter
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='FilteredData')
        excel_buffer.seek(0)

        st.download_button(
            label="⬇ Download as Excel",
            data=excel_buffer,
            file_name="filtered_user_risk_analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No data to export with the current filters.")



st.sidebar.markdown("---")
st.sidebar.info("Dashboard created by your AI assistant (Person B) with DuckDB for performance.")