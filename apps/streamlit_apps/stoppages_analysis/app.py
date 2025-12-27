import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from PIL import Image

# Load favicon
try:
    favicon_path = os.path.join(os.path.dirname(__file__), "assets", "favicon.ico")
    favicon = Image.open(favicon_path)
except Exception as e:
    favicon = "🏭"  # Default emoji favicon if file can't be loaded

# Must be the first Streamlit command
st.set_page_config(
    page_title="Cement Plant Stoppages Analysis",
    page_icon=favicon,
    layout="wide"
)

# Display logo
try:
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    st.image(logo_path, width=240)
except Exception as e:
    st.error(f"Error loading logo: {str(e)}")

# Title
st.title("Capitol Cement Plant - Stoppages Analysis")
st.markdown("---")

# File upload
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Load data
    @st.cache_data
    def load_data(file):
        df = pd.read_csv(file)
        # Convert duration to hours
        df['DurationAsHours'] = pd.to_numeric(df['DurationAsHours'], errors='coerce')
        # Convert datetime columns
        datetime_cols = ['StopDateTime', 'StartDateTime', 'ClosedDateTime']
        for col in datetime_cols:
            df[col] = pd.to_datetime(df[col], format='%d-%m-%Y %H:%M:%S', errors='coerce')
        return df

    df = load_data(uploaded_file)
    
    # Get date range for subtitle
    min_date = df['StopDateTime'].min().strftime('%B %Y')
    max_date = df['StopDateTime'].max().strftime('%B %Y')
    date_range = min_date if min_date == max_date else f"{min_date} - {max_date}"
    
    st.subheader(f"Analysis Period: {date_range}")
    st.markdown("---")

    # Sidebar filters
    st.sidebar.header("Filters")

    # Clean and prepare filter data
    df['CategoryName'] = df['CategoryName'].fillna('Uncategorized')
    df['AreaName'] = df['AreaName'].fillna('Unknown Area')
    df['DepartmentName'] = df['DepartmentName'].fillna('Unknown Department')
    df['EquipmentName'] = df['EquipmentName'].fillna('Unknown Equipment')
    df['ResponsibleDepartment'] = df['ResponsibleDepartment'].fillna('Unknown Responsible Dept')

    # Date range filter
    st.sidebar.subheader("Date Range Filter")
    min_date = df['StopDateTime'].min().date()
    max_date = df['StopDateTime'].max().date()
    
    start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

    # Filter by date range
    mask = (df['StopDateTime'].dt.date >= start_date) & (df['StopDateTime'].dt.date <= end_date)
    df = df[mask]

    # Sidebar filters
    st.sidebar.subheader("Filter Stoppages")

    # Department filter
    dept_filter = st.sidebar.multiselect(
    "Select Departments",
    options=sorted(df['DepartmentName'].unique().tolist()),
    default=sorted(df['DepartmentName'].unique().tolist())
)

    # Equipment filter
    equipment_filter = st.sidebar.multiselect(
    "Select Equipment",
    options=sorted(df['EquipmentName'].unique().tolist()),
    default=sorted(df['EquipmentName'].unique().tolist())
)

    # Responsible Department filter
    responsible_dept_filter = st.sidebar.multiselect(
    "Select Responsible Departments",
    options=sorted(df['ResponsibleDepartment'].unique().tolist()),
    default=sorted(df['ResponsibleDepartment'].unique().tolist())
)

    # Category filter
    category_filter = st.sidebar.multiselect(
    "Select Categories",
    options=sorted(df['CategoryName'].unique().tolist()),
    default=sorted(df['CategoryName'].unique().tolist())
)

    # Filter data
    filtered_df = df[
    (df['DepartmentName'].isin(dept_filter)) &
    (df['EquipmentName'].isin(equipment_filter)) &
    (df['ResponsibleDepartment'].isin(responsible_dept_filter)) &
    (df['CategoryName'].isin(category_filter))
]

    # Create two columns for KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_stoppages = len(filtered_df)
        st.metric("Total Stoppages", total_stoppages)

    with col2:
        total_hours = filtered_df['DurationAsHours'].sum()
        st.metric("Total Hours", f"{total_hours:.1f}")

    with col3:
        total_economic_value = filtered_df['EconomicValue'].sum()
        st.metric("Economic Impact", f"${total_economic_value:,.2f}")

    with col4:
        avg_duration = filtered_df['DurationAsHours'].mean()
        st.metric("Avg Duration (Hours)", f"{avg_duration:.1f}")

    # Create two columns for charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Stoppages by Department")
        dept_fig = px.bar(
            filtered_df.groupby('DepartmentName')['DurationAsHours'].sum().reset_index(),
            x='DepartmentName',
            y='DurationAsHours',
            title='Total Duration by Department',
            labels={'DepartmentName': 'Department', 'DurationAsHours': 'Duration (Hours)'}
        )
        st.plotly_chart(dept_fig, use_container_width=True)

    with col2:
        st.subheader("Stoppages by Category")
        category_fig = px.pie(
            filtered_df,
            names='CategoryName',
            values='DurationAsHours',
            title='Distribution of Stoppages by Category'
        )
        st.plotly_chart(category_fig, use_container_width=True)

    # Equipment Analysis
    st.subheader("Equipment-wise Stoppages Analysis")
    equipment_df = filtered_df.groupby('EquipmentName').agg({
        'DurationAsHours': ['sum', 'count'],
        'EconomicValue': 'sum'
    }).reset_index()
    equipment_df.columns = ['Equipment', 'Total Hours', 'Number of Stoppages', 'Economic Impact']
    equipment_df = equipment_df.sort_values('Total Hours', ascending=False).head(10)

    equipment_fig = px.bar(
        equipment_df,
        x='Equipment',
        y='Total Hours',
        text='Number of Stoppages',
        title='Top 10 Equipment by Stoppage Duration',
        labels={'Equipment': 'Equipment Name', 'Total Hours': 'Duration (Hours)'}
    )
    equipment_fig.update_traces(texttemplate='%{text} incidents', textposition='outside')
    st.plotly_chart(equipment_fig, use_container_width=True)

    # Timeline of stoppages
    st.subheader("Stoppages Timeline")
    timeline_fig = px.timeline(
        filtered_df,
        x_start='StopDateTime',
        x_end='StartDateTime',
        y='DepartmentName',
        color='CategoryName',
        title='Stoppages Timeline by Department',
        labels={'DepartmentName': 'Department', 'CategoryName': 'Category'}
    )
    timeline_fig.update_yaxes(categoryorder='category ascending')
    st.plotly_chart(timeline_fig, use_container_width=True)

    # Top reasons for stoppages
    st.subheader("Top Reasons for Stoppages")
    reasons_df = filtered_df.groupby('ReasonCode')['DurationAsHours'].agg(['sum', 'count']).reset_index()
    reasons_df.columns = ['Reason', 'Total Hours', 'Count']
    reasons_df = reasons_df.sort_values('Total Hours', ascending=False).head(10)

    reasons_fig = px.bar(
        reasons_df,
        x='Reason',
        y='Total Hours',
        text='Count',
        title='Top 10 Reasons for Stoppages',
        labels={'Reason': 'Reason Code', 'Total Hours': 'Duration (Hours)', 'Count': 'Number of Incidents'}
    )
    reasons_fig.update_traces(texttemplate='%{text} incidents', textposition='outside')
    st.plotly_chart(reasons_fig, use_container_width=True)

    # Detailed data table
    st.subheader("Detailed Stoppages Data")
    st.dataframe(
        filtered_df[[
            'DepartmentName', 'EquipmentName', 'CategoryName', 
            'ResponsibleDepartment', 'ReasonCode', 'StopDateTime', 'StartDateTime', 
            'DurationAsHours', 'EconomicValue'
        ]].sort_values('StopDateTime', ascending=False),
        hide_index=True
    )
else:
    st.info("Please upload a CSV file to begin the analysis.")

st.markdown('''An App by :red[Jose Cedeno]!''')
