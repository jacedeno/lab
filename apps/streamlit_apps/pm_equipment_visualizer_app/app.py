import streamlit as st
import pandas as pd
import plotly.express as px
import io

# --- Page Configuration ---
# Set the layout and title for the Streamlit page.
st.set_page_config(layout="wide", page_title="Equipment PM Dashboard")

# --- Title and Description ---
# Display a main title and a subtitle for the application.
st.title("🔧 Equipment Preventive Maintenance Dashboard")
st.markdown("This interactive dashboard allows you to filter and visualize equipment PM data.")

# --- File Uploader ---
# Add a file uploader widget to allow users to upload their own CSV data.
# It accepts files with a .csv extension.
uploaded_file = st.sidebar.file_uploader("Upload your Equipment CSV", type=["csv"])

@st.cache_data
def load_data(file):
    """
    Load data from the uploaded file.
    The @st.cache_data decorator caches the data, so it doesn't have to be reloaded
    every time a widget is changed.
    """
    try:
        # The default file is read differently than an uploaded file.
        if isinstance(file, str):
             # For the default file, which is a path
            return pd.read_csv(file)
        else:
            # For an uploaded file, which is a file-like object
            return pd.read_csv(file)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame() # Return an empty DataFrame on error

# --- Load Data ---
# If a file is uploaded, use it. Otherwise, load the default file.
# This makes the app functional on first run without requiring user action.
if uploaded_file is not None:
    df = load_data(uploaded_file)
else:
    # Use the provided file as the default data source
    df = load_data("Equipment List for PMs for Streamlit.csv")


# --- Data Cleaning and Preparation ---
# Perform some basic data cleaning and type conversion.
if not df.empty:
    # Map the actual column names to expected names for compatibility
    column_mapping = {
        'area': 'Site',
        'dept': 'System', 
        'equipment_type': 'PM Group',
        'equip_num': 'Equipment Description'
    }
    
    # Rename columns to match expected names
    df = df.rename(columns=column_mapping)
    
    # Fill NaN values with 'Unknown' for string columns
    string_columns = ['Site', 'System', 'PM Group', 'Equipment Description']
    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')
    
    # Create a dummy 'Next PM Date' column based on frequency if it doesn't exist
    if 'Next PM Date' not in df.columns:
        # Create a date range starting from today for demonstration
        import datetime
        base_date = datetime.datetime.now()
        df['Next PM Date'] = [base_date + datetime.timedelta(days=i*30) for i in range(len(df))]
    
    # Convert 'Next PM Date' to datetime objects for proper filtering and sorting.
    df['Next PM Date'] = pd.to_datetime(df['Next PM Date'], errors='coerce')

    # Drop rows where the date conversion failed to ensure data integrity.
    df.dropna(subset=['Next PM Date'], inplace=True)


# --- Sidebar Filters ---
# Create filters in the sidebar for user interaction.
st.sidebar.header("Filter Data")

# Check if the dataframe is not empty before creating filters
if not df.empty:
    # Filter by Site
    # Create a multiselect dropdown for the 'Site' column.
    # The options are the unique values in the column.
    selected_sites = st.sidebar.multiselect(
        "Select Site",
        options=sorted(df["Site"].unique()),
        default=sorted(df["Site"].unique())
    )

    # Filter by System
    # Create a multiselect dropdown for the 'System' column.
    selected_systems = st.sidebar.multiselect(
        "Select System",
        options=sorted(df["System"].unique()),
        default=sorted(df["System"].unique())
    )

    # Filter by PM Group
    # Create a multiselect dropdown for the 'PM Group' column.
    selected_pm_groups = st.sidebar.multiselect(
        "Select PM Group",
        options=sorted(df["PM Group"].unique()),
        default=sorted(df["PM Group"].unique())
    )

    # Filter by Date Range
    # Create a date input for selecting a date range for 'Next PM Date'.
    min_date = df["Next PM Date"].min().date()
    max_date = df["Next PM Date"].max().date()
    date_range = st.sidebar.date_input(
        "Select Date Range for Next PM",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    # --- Filtering Logic ---
    # Apply the selected filters to the DataFrame.
    # The .isin() method is used to filter based on the multiple selections.
    start_date, end_date = date_range
    start_datetime = pd.to_datetime(start_date)
    end_datetime = pd.to_datetime(end_date)

    filtered_df = df[
        (df["Site"].isin(selected_sites)) &
        (df["System"].isin(selected_systems)) &
        (df["PM Group"].isin(selected_pm_groups)) &
        (df["Next PM Date"] >= start_datetime) &
        (df["Next PM Date"] <= end_datetime)
    ]

else:
    # If the dataframe is empty, show a message and create an empty frame
    st.warning("No data available to display or filter. Please upload a valid CSV file.")
    filtered_df = pd.DataFrame()


# --- Main Page Layout ---
# Display the filtered data and visualizations on the main page.

# --- Key Metrics ---
# Display some key performance indicators (KPIs) at the top.
st.subheader("High-Level Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Equipment", filtered_df.shape[0])
col2.metric("Unique Systems", filtered_df["System"].nunique())
col3.metric("Unique Sites", filtered_df["Site"].nunique())

st.markdown("---") # Separator

# --- Data Table ---
# Display the filtered data in an expandable table.
with st.expander("View Filtered Data Table"):
    st.dataframe(filtered_df)

# --- Visualizations ---
st.subheader("Data Visualizations")

if not filtered_df.empty:
    # Create two columns for the visualizations
    viz_col1, viz_col2 = st.columns(2)

    with viz_col1:
        # Bar Chart: Equipment Count by System
        # This chart shows the number of equipment items for each system.
        st.markdown("#### Equipment Count by System")
        system_counts = filtered_df["System"].value_counts().reset_index()
        system_counts.columns = ['System', 'Count']
        fig_system = px.bar(
            system_counts,
            x="System",
            y="Count",
            title="Number of Equipment Items per System",
            color="System"
        )
        st.plotly_chart(fig_system, use_container_width=True)

        # Pie Chart: PM Group Distribution
        # This chart shows the proportion of equipment in each PM group.
        st.markdown("#### PM Group Distribution")
        pm_group_counts = filtered_df["PM Group"].value_counts().reset_index()
        pm_group_counts.columns = ['PM Group', 'Count']
        fig_pm_group = px.pie(
            pm_group_counts,
            names="PM Group",
            values="Count",
            title="Distribution of PM Groups",
            hole=0.3
        )
        st.plotly_chart(fig_pm_group, use_container_width=True)


    with viz_col2:
        # Bar Chart: Equipment Count by Site
        # This chart shows the number of equipment items at each site.
        st.markdown("#### Equipment Count by Site")
        site_counts = filtered_df["Site"].value_counts().reset_index()
        site_counts.columns = ['Site', 'Count']
        fig_site = px.bar(
            site_counts,
            x="Count",
            y="Site",
            orientation='h',
            title="Number of Equipment Items per Site",
            color="Site"
        )
        st.plotly_chart(fig_site, use_container_width=True)
        
        # Timeline: PM Schedule
        # This chart shows the timeline of upcoming PMs.
        st.markdown("#### Upcoming PM Schedule")
        timeline_df = filtered_df.sort_values('Next PM Date')
        fig_timeline = px.timeline(
            timeline_df,
            x_start="Next PM Date",
            x_end=timeline_df["Next PM Date"] + pd.Timedelta(days=1), # Make it a bar
            y="Equipment Description",
            color="PM Group",
            title="Timeline of Next PM Dates"
        )
        fig_timeline.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig_timeline, use_container_width=True)

else:
    st.warning("No data to display for the selected filters.")
