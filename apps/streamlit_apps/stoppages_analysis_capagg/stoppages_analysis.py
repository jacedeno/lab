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
    min_date = df['StopDateTime'].min()
    max_date = df['StopDateTime'].max()
    date_range_display = f"{min_date.strftime('%b %d, %Y %H:%M')} - {max_date.strftime('%b %d, %Y %H:%M')}"
    
    st.subheader(f"Duration: {date_range_display}")
    
    # Calculate calendar time in hours
    calendar_time_hours = (max_date - min_date).total_seconds() / 3600
    
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
    min_date_filter = df['StopDateTime'].min().date()
    max_date_filter = df['StopDateTime'].max().date()
    
    start_date = st.sidebar.date_input("Start Date", min_date_filter, min_value=min_date_filter, max_value=max_date_filter)
    end_date = st.sidebar.date_input("End Date", max_date_filter, min_value=min_date_filter, max_value=max_date_filter)

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

    # ========== KPI CALCULATIONS ==========
    # Identify stoppages due to circumstances vs incidents
    # Assuming CategoryName contains this information - adjust field name as needed
    circumstances_categories = ['Circumstances', 'External', 'Planned', 'Maintenance']  # Adjust as needed
    
    # Calculate total stoppage hours
    total_stop_time = filtered_df['DurationAsHours'].sum()
    
    # Separate stoppages by type
    stoppages_circumstances = filtered_df[filtered_df['CategoryName'].str.contains('|'.join(circumstances_categories), case=False, na=False)]
    stoppages_incidents = filtered_df[~filtered_df['CategoryName'].str.contains('|'.join(circumstances_categories), case=False, na=False)]
    
    stop_time_circumstances = stoppages_circumstances['DurationAsHours'].sum()
    stop_time_incidents = stoppages_incidents['DurationAsHours'].sum()
    count_incidents = len(stoppages_incidents)
    
    # Calculate operating hours
    operating_hours = calendar_time_hours - total_stop_time
    
    # Calculate KPIs
    run_factor = (operating_hours * 100) / calendar_time_hours if calendar_time_hours > 0 else 0
    availability_factor = ((operating_hours + stop_time_circumstances) * 100) / calendar_time_hours if calendar_time_hours > 0 else 0
    reliability_factor = (operating_hours * 100) / (operating_hours + stop_time_incidents) if (operating_hours + stop_time_incidents) > 0 else 0
    mtbf = operating_hours / count_incidents if count_incidents > 0 else 0

    # ========== OVERALL KPI GAUGES ==========
    st.subheader("Overall Performance KPIs")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fig_run = go.Figure(go.Indicator(
            mode="gauge+number",
            value=run_factor,
            title={'text': "RUN FACTOR"},
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#FDB813"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 100], 'color': '#E8E8E8'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_run.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_run, use_container_width=True)
    
    with col2:
        fig_avail = go.Figure(go.Indicator(
            mode="gauge+number",
            value=availability_factor,
            title={'text': "AVAILABILITY FACTOR"},
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#FDB813"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 100], 'color': '#E8E8E8'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_avail.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_avail, use_container_width=True)
    
    with col3:
        fig_reliab = go.Figure(go.Indicator(
            mode="gauge+number",
            value=reliability_factor,
            title={'text': "RELIABILITY FACTOR"},
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "#4CAF50"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 100], 'color': '#E8E8E8'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_reliab.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_reliab, use_container_width=True)
    
    with col4:
        st.markdown("### MEAN TIME BETWEEN FAILURES")
        st.markdown(f"<div style='text-align: center; font-size: 48px; color: #1E88E5; font-weight: bold;'>{mtbf:.3f}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; font-size: 18px; color: #666;'>HOURS</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ========== KPI BY EQUIPMENT/DEPARTMENT ==========
    def calculate_kpis_by_group(df, calendar_hours, group_col='DepartmentName'):
        """Calculate KPIs for each equipment/department"""
        kpi_data = []
        
        for group_name in df[group_col].unique():
            group_df = df[df[group_col] == group_name]
            
            # Total stoppage time
            total_stop = group_df['DurationAsHours'].sum()
            
            # Count stoppages
            total_count = len(group_df)
            
            # Separate by circumstances and incidents
            circumstances = group_df[group_df['CategoryName'].str.contains('|'.join(circumstances_categories), case=False, na=False)]
            incidents = group_df[~group_df['CategoryName'].str.contains('|'.join(circumstances_categories), case=False, na=False)]
            
            stop_circumstances = circumstances['DurationAsHours'].sum()
            stop_incidents = incidents['DurationAsHours'].sum()
            count_circumstances = len(circumstances)
            count_incidents = len(incidents)
            
            # Operating hours
            operating_hrs = calendar_hours - total_stop
            
            # Calculate KPIs
            rf = (operating_hrs * 100) / calendar_hours if calendar_hours > 0 else 0
            af = ((operating_hrs + stop_circumstances) * 100) / calendar_hours if calendar_hours > 0 else 0
            rlf = (operating_hrs * 100) / (operating_hrs + stop_incidents) if (operating_hrs + stop_incidents) > 0 else 0
            mtbf_val = operating_hrs / count_incidents if count_incidents > 0 else 0
            
            kpi_data.append({
                group_col: group_name,
                'Operating Hours': operating_hrs,
                'Stop Time (hrs)': total_stop,
                'Stoppages Due To Circumstances': count_circumstances,
                'Stop Time Due To Circumstances (hrs)': stop_circumstances,
                'Stoppages Due To Incidents': count_incidents,
                'Stop Time Due To Incidents (hrs)': stop_incidents,
                'Run Factor (%)': rf,
                'Availability Factor (%)': af,
                'Reliability Factor (%)': rlf,
                'Mean Time Between Failures (hrs)': mtbf_val
            })
        
        return pd.DataFrame(kpi_data)

    # Calculate KPIs by department
    kpi_by_dept = calculate_kpis_by_group(filtered_df, calendar_time_hours, 'DepartmentName')
    if len(kpi_by_dept) > 0:
        group_col_name = kpi_by_dept.columns[0]  # Get the actual column name
        kpi_by_dept = kpi_by_dept.sort_values(group_col_name)

    # ========== KPI CHARTS BY EQUIPMENT ==========
    st.subheader("KPI Analysis by Department")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Run Factor by Equipment
        fig_rf = px.bar(
            kpi_by_dept,
            x='DepartmentName',
            y='Run Factor (%)',
            title='RUN FACTOR',
            labels={'DepartmentName': '', 'Run Factor (%)': 'Percentage'},
            color_discrete_sequence=['#2C5F8D']
        )
        fig_rf.update_layout(
            yaxis=dict(range=[0, 100]),
            xaxis_tickangle=-45,
            height=400
        )
        st.plotly_chart(fig_rf, use_container_width=True)
    
    with col2:
        # Availability Factor by Equipment
        fig_af = px.bar(
            kpi_by_dept,
            x='DepartmentName',
            y='Availability Factor (%)',
            title='AVAILABILITY FACTOR',
            labels={'DepartmentName': '', 'Availability Factor (%)': 'Percentage'},
            color_discrete_sequence=['#5B9BD5']
        )
        fig_af.update_layout(
            yaxis=dict(range=[0, 100]),
            xaxis_tickangle=-45,
            height=400
        )
        st.plotly_chart(fig_af, use_container_width=True)

    col3, col4 = st.columns(2)
    
    with col3:
        # Reliability Factor by Equipment
        fig_rlf = px.bar(
            kpi_by_dept,
            x='DepartmentName',
            y='Reliability Factor (%)',
            title='RELIABILITY FACTOR',
            labels={'DepartmentName': '', 'Reliability Factor (%)': 'Percentage'},
            color_discrete_sequence=['#7CB5EC']
        )
        fig_rlf.update_layout(
            yaxis=dict(range=[0, 100]),
            xaxis_tickangle=-45,
            height=400
        )
        st.plotly_chart(fig_rlf, use_container_width=True)
    
    with col4:
        # MTBF by Equipment
        fig_mtbf = px.bar(
            kpi_by_dept,
            x='DepartmentName',
            y='Mean Time Between Failures (hrs)',
            title='MEAN TIME BETWEEN FAILURES',
            labels={'DepartmentName': '', 'Mean Time Between Failures (hrs)': 'Hours'},
            color_discrete_sequence=['#9B7EBD']
        )
        fig_mtbf.update_layout(
            xaxis_tickangle=-45,
            height=400
        )
        st.plotly_chart(fig_mtbf, use_container_width=True)

    st.markdown("---")

    # ========== OVERALL PERFORMANCE ANALYSIS ==========
    st.subheader("Capitol Cement - Overall Performance Analysis")
    
    # Create combined chart with all KPIs
    fig_combined = go.Figure()
    
    # Add bars for each KPI
    fig_combined.add_trace(go.Bar(
        name='Run Factor',
        x=kpi_by_dept['DepartmentName'],
        y=kpi_by_dept['Run Factor (%)'],
        marker_color='#2C5F8D'
    ))
    
    fig_combined.add_trace(go.Bar(
        name='Availability Factor',
        x=kpi_by_dept['DepartmentName'],
        y=kpi_by_dept['Availability Factor (%)'],
        marker_color='#5B9BD5'
    ))
    
    fig_combined.add_trace(go.Bar(
        name='Reliability Factor',
        x=kpi_by_dept['DepartmentName'],
        y=kpi_by_dept['Reliability Factor (%)'],
        marker_color='#9ECAE1'
    ))
    
    # Add line for MTBF (on secondary y-axis)
    fig_combined.add_trace(go.Scatter(
        name='Mean Time Between Failures',
        x=kpi_by_dept['DepartmentName'],
        y=kpi_by_dept['Mean Time Between Failures (hrs)'],
        mode='lines+markers',
        marker=dict(size=8, color='#9B7EBD'),
        line=dict(color='#9B7EBD', width=2),
        yaxis='y2'
    ))
    
    fig_combined.update_layout(
        barmode='group',
        height=500,
        xaxis=dict(title='', tickangle=-45),
        yaxis=dict(title='Percentage', side='left', range=[0, 105]),
        yaxis2=dict(title='Hours', side='right', overlaying='y', showgrid=False),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_combined, use_container_width=True)

    st.markdown("---")

    # ========== KPIs BY EQUIPMENT CHART ==========
    st.subheader("Capitol Cement - KPIs")
    
    # Calculate KPIs by Equipment
    kpi_by_equipment = calculate_kpis_by_group(filtered_df, calendar_time_hours, 'EquipmentName')
    kpi_by_equipment = kpi_by_equipment.sort_values('EquipmentName')
    
    # Create multi-series chart
    fig_kpi_equipment = go.Figure()
    
    # Add Operating Hours as bars
    fig_kpi_equipment.add_trace(go.Bar(
        name='Operating Hours',
        x=kpi_by_equipment['EquipmentName'],
        y=kpi_by_equipment['Operating Hours'],
        marker_color='#4A2E6B',
        yaxis='y'
    ))
    
    # Add Stop Time as bars
    fig_kpi_equipment.add_trace(go.Bar(
        name='Stop Time',
        x=kpi_by_equipment['EquipmentName'],
        y=kpi_by_equipment['Stop Time (hrs)'],
        marker_color='#8B6FB5',
        yaxis='y'
    ))
    
    # Add MTBF as bars
    fig_kpi_equipment.add_trace(go.Bar(
        name='Mean Time Between Failures',
        x=kpi_by_equipment['EquipmentName'],
        y=kpi_by_equipment['Mean Time Between Failures (hrs)'],
        marker_color='#B8A3D6',
        yaxis='y'
    ))
    
    # Add KPI percentages as lines (secondary axis)
    fig_kpi_equipment.add_trace(go.Scatter(
        name='Run Factor',
        x=kpi_by_equipment['EquipmentName'],
        y=kpi_by_equipment['Run Factor (%)'],
        mode='lines+markers',
        marker=dict(size=8, color='#1F77B4'),
        line=dict(color='#1F77B4', width=2),
        yaxis='y2'
    ))
    
    fig_kpi_equipment.add_trace(go.Scatter(
        name='Availability Factor',
        x=kpi_by_equipment['EquipmentName'],
        y=kpi_by_equipment['Availability Factor (%)'],
        mode='lines+markers',
        marker=dict(size=8, color='#FF7F0E'),
        line=dict(color='#FF7F0E', width=2),
        yaxis='y2'
    ))
    
    fig_kpi_equipment.add_trace(go.Scatter(
        name='Reliability Factor',
        x=kpi_by_equipment['EquipmentName'],
        y=kpi_by_equipment['Reliability Factor (%)'],
        mode='lines+markers',
        marker=dict(size=8, color='#2CA02C'),
        line=dict(color='#2CA02C', width=2),
        yaxis='y2'
    ))
    
    fig_kpi_equipment.update_layout(
        height=500,
        xaxis=dict(title='', tickangle=-45),
        yaxis=dict(title='Hours', side='left'),
        yaxis2=dict(title='Percentage', side='right', overlaying='y', showgrid=False, range=[0, 105]),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_kpi_equipment, use_container_width=True)

    st.markdown("---")

    # ========== KPI DATA TABLE ==========
    st.subheader(f"Capitol Cement KPIs Data for the Calendar Duration of {calendar_time_hours:.2f} Hours")
    
    # Add the total row to the department KPIs
    total_row = {
        'DepartmentName': 'TOTAL',
        'Operating Hours': operating_hours,
        'Stop Time (hrs)': total_stop_time,
        'Stoppages Due To Circumstances': len(stoppages_circumstances),
        'Stop Time Due To Circumstances (hrs)': stop_time_circumstances,
        'Stoppages Due To Incidents': count_incidents,
        'Stop Time Due To Incidents (hrs)': stop_time_incidents,
        'Run Factor (%)': run_factor,
        'Availability Factor (%)': availability_factor,
        'Reliability Factor (%)': reliability_factor,
        'Mean Time Between Failures (hrs)': mtbf
    }
    
    kpi_table = pd.concat([kpi_by_dept, pd.DataFrame([total_row])], ignore_index=True)
    
    # Rename column for display
    kpi_table = kpi_table.rename(columns={'DepartmentName': 'Department'})
    
    # Add row number
    kpi_table.insert(0, '#', range(1, len(kpi_table) + 1))
    
    # Format the table
    st.dataframe(
        kpi_table.style.format({
            'Operating Hours': '{:.3f}',
            'Stop Time (hrs)': '{:.3f}',
            'Stop Time Due To Circumstances (hrs)': '{:.3f}',
            'Stop Time Due To Incidents (hrs)': '{:.3f}',
            'Run Factor (%)': '{:.2f}',
            'Availability Factor (%)': '{:.2f}',
            'Reliability Factor (%)': '{:.2f}',
            'Mean Time Between Failures (hrs)': '{:.3f}'
        }).apply(lambda x: ['background-color: #E8F4F8' if x.name == len(kpi_table) - 1 else '' for i in x], axis=1),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")

    # ========== ORIGINAL VISUALIZATIONS ==========
    st.subheader("Detailed Stoppages Analysis")
    
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
