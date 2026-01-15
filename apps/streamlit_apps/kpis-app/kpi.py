import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import calendar
from PIL import Image
import json
from database import KPIDatabase

# Page configuration - Must be the first Streamlit command
try:
    favicon_path = os.path.join(os.path.dirname(__file__), "assets", "favicon.ico")
    favicon = Image.open(favicon_path)
except Exception as e:
    favicon = "🔧"  # Default emoji favicon if file can't be loaded

st.set_page_config(
    page_title="Maintenance KPI Dashboard",
    page_icon=favicon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
@st.cache_resource
def get_database():
    """Get database instance (cached)"""
    db = KPIDatabase()
    db.initialize_sample_data()  # Add sample data if database is empty
    return db

db = get_database()

# Load data from database
weeks_data = db.get_all_weeks()

# Display logo
try:
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    st.image(logo_path, width=240)
except Exception as e:
    pass  # Logo is optional

# Company color palette
PRIMARY_COLOR = '#357b2d'
SECONDARY_COLOR = '#4a9d3e'
ACCENT_COLOR = '#6bc259'
LIGHT_GREEN = '#e8f5e9'
DARK_GREEN = '#1b5e20'

# Custom CSS with company colors
st.markdown(f"""
    <style>
    .main {{
        background-color: #f5f5f5;
    }}
    .metric-card {{
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    h1 {{
        color: {PRIMARY_COLOR};
        font-family: 'Arial', sans-serif;
    }}
    .stMetric {{
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    div[data-testid="stMetricValue"] {{
        color: {PRIMARY_COLOR};
    }}
    </style>
    """, unsafe_allow_html=True)

# Function to get Monday start date for a given YYWW week number
def get_week_start_date(week_num):
    """
    Get the Monday start date for a week number in YYWW format.
    Example: 2601 = Week 1 of 2026, starts December 29, 2025
    """
    year = 2000 + (week_num // 100)  # e.g., 2601 -> 26 -> 2026
    week = week_num % 100  # e.g., 2601 -> 01
    
    if week < 1 or week > 53:
        return None
    
    # Get January 4th of the year (always in ISO week 1)
    jan4 = datetime(year, 1, 4)
    
    # Find Monday of week 1
    week1_monday = jan4 - timedelta(days=jan4.weekday())
    
    # Calculate Monday of requested week
    target_monday = week1_monday + timedelta(weeks=int(week - 1))
    
    return target_monday

def format_week_num(week_num):
    """
    Convert week number to YYWW format for display.
    Example: 202601 -> 2601, 2601 -> 2601
    """
    if week_num > 9999:
        # Convert from YYYYWW to YYWW
        return (week_num // 100 % 100) * 100 + (week_num % 100)
    return week_num

def get_next_week_num(current_week_num):
    """
    Calculate the next week number in YYWW format.
    Example: 2552 -> 2601, 2601 -> 2602
    """
    year = current_week_num // 100
    week = current_week_num % 100
    
    # Check if this week exists in the year
    dec_28 = datetime(2000 + year, 12, 28)
    max_week = dec_28.isocalendar()[1]
    
    if week >= max_week:
        # Move to next year, week 1
        return ((year + 1) * 100) + 1
    else:
        return current_week_num + 1

# Function to calculate averages
def calculate_averages(data_list):
    if not data_list:
        return {}
    
    avg = {
        'Week': 'Average',
        'WeekNum': 0,
        'WeekDate': f'{len(data_list)}-Week Avg',
        'Personnel': round(sum(d['Personnel'] for d in data_list) / len(data_list)),
        'WorkingDays': round(sum(d['WorkingDays'] for d in data_list) / len(data_list)),
        'AvailableHours': round(sum(d['AvailableHours'] for d in data_list) / len(data_list)),
        'PlannedHrs_Corrective': round(sum(d['PlannedHrs_Corrective'] for d in data_list) / len(data_list)),
        'PlannedHrs_Reliability': round(sum(d['PlannedHrs_Reliability'] for d in data_list) / len(data_list)),
        'ExecutedHrs_Corrective': round(sum(d['ExecutedHrs_Corrective'] for d in data_list) / len(data_list)),
        'ExecutedHrs_Reliability': round(sum(d['ExecutedHrs_Reliability'] for d in data_list) / len(data_list)),
        'PlanningRate': round(sum(d['PlanningRate'] for d in data_list) / len(data_list)),
        'PlanAttainment': round(sum(d['PlanAttainment'] for d in data_list) / len(data_list)),
        'PlanAttainment_Corrective': round(sum(d['PlanAttainment_Corrective'] for d in data_list) / len(data_list)),
        'PlanAttainment_Reliability': round(sum(d['PlanAttainment_Reliability'] for d in data_list) / len(data_list)),
        'UnplannedJob_Pct': round(sum(d['UnplannedJob_Pct'] for d in data_list) / len(data_list)),
        'PMR_Pct': round(sum(d['PMR_Pct'] for d in data_list) / len(data_list)),
        'PMR_Completion': round(sum(d['PMR_Completion'] for d in data_list) / len(data_list)),
        'UnplannedHrs_Total': round(sum(d['UnplannedHrs_Total'] for d in data_list) / len(data_list))
    }
    return avg

# Create dataframe with current data
df_weeks_only = pd.DataFrame(weeks_data)
avg_data = calculate_averages(weeks_data)
df_with_avg = pd.concat([df_weeks_only, pd.DataFrame([avg_data])], ignore_index=True)

# Get latest week info
latest_week = df_weeks_only.iloc[-1] if len(df_weeks_only) > 0 else None
previous_week = df_weeks_only.iloc[-2] if len(df_weeks_only) > 1 else None

# Main title with dynamic date
if latest_week is not None:
    week_num = format_week_num(latest_week['WeekNum'])
    week_date = latest_week['WeekDate']
    st.title("🔧 Maintenance KPI Dashboard")
    st.markdown(f"### Performance Analysis - Week {week_num} ({week_date})")
else:
    st.title("🔧 Maintenance KPI Dashboard")
    st.markdown("### Performance Analysis")

st.markdown("---")

# Sidebar with filters and data entry
st.sidebar.header("📊 Dashboard Controls")

# Add new week data section
with st.sidebar.expander("➕ Add New Week Data", expanded=False):
    st.markdown("**Enter data for new week:**")
    st.markdown("*Format: YYWW (e.g., 2601 = Week 1 of 2026, 2603 = Week 3 of 2026)*")
    
    # Auto-calculate next week number and date
    if latest_week is not None:
        latest_week_num = latest_week['WeekNum']
        # Handle both YYYYWW (6-digit) and YYWW (4-digit) formats
        if latest_week_num > 9999:
            # Convert from YYYYWW to YYWW
            latest_week_num = (latest_week_num // 100 % 100) * 100 + (latest_week_num % 100)
        next_week_num = get_next_week_num(latest_week_num)
    else:
        # Default to current ISO week
        today = datetime.now()
        iso_cal = today.isocalendar()
        next_week_num = (iso_cal[0] % 100) * 100 + iso_cal[1]
    
    # Calculate the Monday start date for this week
    next_monday = get_week_start_date(next_week_num)
    next_date_str = next_monday.strftime('%m/%d/%Y') if next_monday else datetime.now().strftime('%m/%d/%Y')
    
    st.markdown(f"**Week Number (YYWW format)**")
    new_week_num = st.number_input("Example: 2601, 2602, 2603...", min_value=2001, max_value=9953, value=next_week_num, key='new_week_num', label_visibility="collapsed")
    
    # Auto-calculate date when week number changes
    auto_date = get_week_start_date(new_week_num)
    auto_date_str = auto_date.strftime('%m/%d/%Y') if auto_date else next_date_str
    
    new_week_date = st.text_input("Week Start Date (Monday)", value=auto_date_str, key='new_week_date', disabled=True)
    st.caption("Date auto-calculated from week number")
    
    col1, col2 = st.columns(2)
    with col1:
        new_personnel = st.number_input("Personnel", min_value=1, value=15, key='new_personnel')
        new_working_days = st.number_input("Working Days", min_value=1, max_value=7, value=5, key='new_working_days')
        new_available_hrs = st.number_input("Available Hours", min_value=0, value=496, key='new_available_hrs')
        new_planned_corr = st.number_input("Planned Hrs (Corrective)", min_value=0, value=400, key='new_planned_corr')
        new_planned_rel = st.number_input("Planned Hrs (Reliability)", min_value=0, value=150, key='new_planned_rel')
        new_exec_corr = st.number_input("Executed Hrs (Corrective)", min_value=0, value=300, key='new_exec_corr')
        new_exec_rel = st.number_input("Executed Hrs (Reliability)", min_value=0, value=140, key='new_exec_rel')
    
    with col2:
        new_planning_rate = st.number_input("Planning Rate %", min_value=0, max_value=200, value=100, key='new_planning_rate')
        new_plan_attain = st.number_input("Plan Attainment %", min_value=0, max_value=100, value=70, key='new_plan_attain')
        new_plan_attain_corr = st.number_input("Plan Attainment Corrective %", min_value=0, max_value=100, value=65, key='new_plan_attain_corr')
        new_plan_attain_rel = st.number_input("Plan Attainment Reliability %", min_value=0, max_value=100, value=85, key='new_plan_attain_rel')
        new_unplanned_pct = st.number_input("Unplanned Jobs %", min_value=0, max_value=100, value=20, key='new_unplanned_pct')
        new_pmr_pct = st.number_input("PMR %", min_value=0, max_value=100, value=30, key='new_pmr_pct')
        new_pmr_completion = st.number_input("PMR Completion %", min_value=0, max_value=100, value=80, key='new_pmr_completion')
        new_unplanned_hrs = st.number_input("Unplanned Hours Total", min_value=0, value=100, key='new_unplanned_hrs')
    
    if st.button("Add Week", type="primary"):
        new_week_data = {
            'Week': f'Week {new_week_num}',
            'WeekNum': new_week_num,
            'WeekDate': auto_date_str,
            'Personnel': new_personnel,
            'WorkingDays': new_working_days,
            'AvailableHours': new_available_hrs,
            'PlannedHrs_Corrective': new_planned_corr,
            'PlannedHrs_Reliability': new_planned_rel,
            'ExecutedHrs_Corrective': new_exec_corr,
            'ExecutedHrs_Reliability': new_exec_rel,
            'PlanningRate': new_planning_rate,
            'PlanAttainment': new_plan_attain,
            'PlanAttainment_Corrective': new_plan_attain_corr,
            'PlanAttainment_Reliability': new_plan_attain_rel,
            'UnplannedJob_Pct': new_unplanned_pct,
            'PMR_Pct': new_pmr_pct,
            'PMR_Completion': new_pmr_completion,
            'UnplannedHrs_Total': new_unplanned_hrs
        }
        
        if db.add_week(new_week_data):
            st.success(f"✅ Week {new_week_num} added successfully!")
            st.rerun()
        else:
            st.error(f"❌ Week {new_week_num} already exists or could not be added.")

# Data management section
with st.sidebar.expander("🗑️ Manage Weeks", expanded=False):
    week_count = db.get_week_count()
    if week_count > 0:
        weeks_to_remove = st.multiselect(
            "Select weeks to remove:",
            options=[w['Week'] for w in weeks_data],
            key='weeks_to_remove'
        )
        if st.button("Remove Selected Weeks", type="secondary"):
            if db.remove_weeks(weeks_to_remove):
                st.success("✅ Weeks removed successfully!")
                st.rerun()
            else:
                st.error("❌ Error removing weeks.")
        
        st.markdown(f"**Total weeks:** {week_count}/52")
    else:
        st.info("No weeks to manage")

st.sidebar.markdown("---")

# View filters
view_option = st.sidebar.radio(
    "Select View:",
    ["Weekly Data Only", "Include Average"]
)

if view_option == "Weekly Data Only":
    df_display = df_weeks_only
else:
    df_display = df_with_avg

week_filter = st.sidebar.multiselect(
    "Select Weeks to Display:",
    options=df_display['Week'].tolist(),
    default=df_display['Week'].tolist()
)

df_filtered = df_display[df_display['Week'].isin(week_filter)]

# Main KPI cards - always show latest week
if latest_week is not None:
    st.markdown(f"## 📈 Key Performance Indicators - Week {format_week_num(latest_week['WeekNum'])}")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if previous_week is not None:
            delta_planning = latest_week['PlanningRate'] - previous_week['PlanningRate']
            st.metric(
                label="Planning Rate",
                value=f"{latest_week['PlanningRate']}%",
                delta=f"{delta_planning:+.0f} pts",
                delta_color="inverse" if delta_planning > 10 else "normal"
            )
        else:
            st.metric(
                label="Planning Rate",
                value=f"{latest_week['PlanningRate']}%"
            )

    with col2:
        if previous_week is not None:
            delta_attainment = latest_week['PlanAttainment'] - previous_week['PlanAttainment']
            st.metric(
                label="Plan Attainment",
                value=f"{latest_week['PlanAttainment']}%",
                delta=f"{delta_attainment:+.0f} pts",
                delta_color="normal"
            )
        else:
            st.metric(
                label="Plan Attainment",
                value=f"{latest_week['PlanAttainment']}%"
            )

    with col3:
        if previous_week is not None:
            delta_unplanned = latest_week['UnplannedJob_Pct'] - previous_week['UnplannedJob_Pct']
            st.metric(
                label="Unplanned Jobs",
                value=f"{latest_week['UnplannedJob_Pct']}%",
                delta=f"{delta_unplanned:+.0f} pts",
                delta_color="inverse"
            )
        else:
            st.metric(
                label="Unplanned Jobs",
                value=f"{latest_week['UnplannedJob_Pct']}%"
            )

    with col4:
        if previous_week is not None:
            delta_pmr_pct = latest_week['PMR_Pct'] - previous_week['PMR_Pct']
            st.metric(
                label="PMR %",
                value=f"{latest_week['PMR_Pct']}%",
                delta=f"{delta_pmr_pct:+.0f} pts",
                delta_color="normal"
            )
        else:
            st.metric(
                label="PMR %",
                value=f"{latest_week['PMR_Pct']}%"
            )

    with col5:
        if previous_week is not None:
            delta_pmr = latest_week['PMR_Completion'] - previous_week['PMR_Completion']
            st.metric(
                label="PMR Completion",
                value=f"{latest_week['PMR_Completion']}%",
                delta=f"{delta_pmr:+.0f} pts",
                delta_color="normal"
            )
        else:
            st.metric(
                label="PMR Completion",
                value=f"{latest_week['PMR_Completion']}%"
            )

st.markdown("---")

# Main charts section
col_left, col_right = st.columns(2)

# Chart 1: Plan Attainment Trend
with col_left:
    st.markdown("### 📉 Plan Attainment Trend")
    
    fig_attainment = go.Figure()
    
    # Filter data based on selection
    plot_data = df_filtered.copy()
    
    fig_attainment.add_trace(go.Scatter(
        x=plot_data['Week'],
        y=plot_data['PlanAttainment'],
        mode='lines+markers',
        name='Overall',
        line=dict(color=PRIMARY_COLOR, width=3),
        marker=dict(size=10),
        text=plot_data['PlanAttainment'].apply(lambda x: f"{x}%"),
        textposition='top center'
    ))
    
    fig_attainment.add_trace(go.Scatter(
        x=plot_data['Week'],
        y=plot_data['PlanAttainment_Corrective'],
        mode='lines+markers',
        name='Corrective',
        line=dict(color='#ff7f0e', width=2, dash='dash'),
        marker=dict(size=8),
        text=plot_data['PlanAttainment_Corrective'].apply(lambda x: f"{x}%"),
        textposition='top center'
    ))
    
    fig_attainment.add_trace(go.Scatter(
        x=plot_data['Week'],
        y=plot_data['PlanAttainment_Reliability'],
        mode='lines+markers',
        name='Reliability',
        line=dict(color=SECONDARY_COLOR, width=2, dash='dash'),
        marker=dict(size=8),
        text=plot_data['PlanAttainment_Reliability'].apply(lambda x: f"{x}%"),
        textposition='top center'
    ))
    
    # Target line at 85%
    fig_attainment.add_hline(
        y=85, 
        line_dash="dot", 
        line_color="red",
        annotation_text="Target: 85%",
        annotation_position="right"
    )
    
    fig_attainment.update_layout(
        xaxis_title="Week",
        yaxis_title="Attainment (%)",
        hovermode='x unified',
        height=400,
        template='plotly_white',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_attainment, use_container_width=True)
    
    if latest_week is not None and previous_week is not None:
        attain_change = latest_week['PlanAttainment'] - df_weeks_only.iloc[0]['PlanAttainment']
        st.markdown(f"""
        **💬 Key Insight:** Plan attainment trend: {df_weeks_only.iloc[0]['PlanAttainment']}% → {latest_week['PlanAttainment']}% ({attain_change:+.0f} points)
        """)

# Chart 2: Unplanned Work Growth
with col_right:
    st.markdown("### ⚠️ Unplanned Work Trend")
    
    fig_unplanned = go.Figure()
    
    # Color coding based on thresholds
    colors = []
    for val in plot_data['UnplannedJob_Pct']:
        if val < 15:
            colors.append(PRIMARY_COLOR)
        elif val < 25:
            colors.append('#f39c12')
        else:
            colors.append('#e74c3c')
    
    fig_unplanned.add_trace(go.Bar(
        x=plot_data['Week'],
        y=plot_data['UnplannedJob_Pct'],
        name='Unplanned %',
        marker_color=colors,
        text=plot_data['UnplannedJob_Pct'].apply(lambda x: f"{x}%"),
        textposition='outside'
    ))
    
    fig_unplanned.add_hline(
        y=15, 
        line_dash="dot", 
        line_color="orange",
        annotation_text="Target: <15%",
        annotation_position="right"
    )
    
    fig_unplanned.update_layout(
        xaxis_title="Week",
        yaxis_title="Unplanned Work (%)",
        height=400,
        template='plotly_white',
        showlegend=False
    )
    
    st.plotly_chart(fig_unplanned, use_container_width=True)
    
    if latest_week is not None and previous_week is not None:
        unplanned_change = latest_week['UnplannedJob_Pct'] - df_weeks_only.iloc[0]['UnplannedJob_Pct']
        st.markdown(f"""
        **💬 Key Insight:** Unplanned work trend: {df_weeks_only.iloc[0]['UnplannedJob_Pct']}% → {latest_week['UnplannedJob_Pct']}% ({unplanned_change:+.0f} points)
        """)

st.markdown("---")

# Second row of charts
col_left2, col_right2 = st.columns(2)

# Chart 3: Resource Utilization
with col_left2:
    st.markdown("### 👥 Resource Utilization")
    
    fig_resource = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_resource.add_trace(
        go.Bar(
            x=plot_data['Week'],
            y=plot_data['AvailableHours'],
            name='Available Hours',
            marker_color=LIGHT_GREEN
        ),
        secondary_y=False
    )
    
    fig_resource.add_trace(
        go.Bar(
            x=plot_data['Week'],
            y=plot_data['ExecutedHrs_Corrective'] + plot_data['ExecutedHrs_Reliability'],
            name='Executed Hours',
            marker_color=PRIMARY_COLOR
        ),
        secondary_y=False
    )
    
    fig_resource.add_trace(
        go.Scatter(
            x=plot_data['Week'],
            y=plot_data['Personnel'],
            mode='lines+markers',
            name='Personnel',
            line=dict(color='#e74c3c', width=3),
            marker=dict(size=12),
            text=plot_data['Personnel'],
            textposition='top center'
        ),
        secondary_y=True
    )
    
    fig_resource.update_xaxes(title_text="Week")
    fig_resource.update_yaxes(title_text="Hours", secondary_y=False)
    fig_resource.update_yaxes(title_text="Personnel Count", secondary_y=True)
    
    fig_resource.update_layout(
        height=400,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_resource, use_container_width=True)
    
    if latest_week is not None:
        personnel_change = latest_week['Personnel'] - df_weeks_only.iloc[0]['Personnel']
        st.markdown(f"""
        **💬 Key Insight:** Personnel trend: {df_weeks_only.iloc[0]['Personnel']} → {latest_week['Personnel']} ({personnel_change:+.0f})
        """)

# Chart 4: Planned vs Executed by Week
with col_right2:
    st.markdown("### 📊 Planned vs Executed Hours")
    
    fig_planned_exec = go.Figure()
    
    # Total planned hours
    total_planned = plot_data['PlannedHrs_Corrective'] + plot_data['PlannedHrs_Reliability']
    # Total executed hours
    total_executed = plot_data['ExecutedHrs_Corrective'] + plot_data['ExecutedHrs_Reliability']
    
    fig_planned_exec.add_trace(go.Bar(
        x=plot_data['Week'],
        y=total_planned,
        name='Planned',
        marker_color='lightcoral',
        text=total_planned,
        textposition='auto'
    ))
    
    fig_planned_exec.add_trace(go.Bar(
        x=plot_data['Week'],
        y=total_executed,
        name='Executed',
        marker_color=SECONDARY_COLOR,
        text=total_executed,
        textposition='auto'
    ))
    
    fig_planned_exec.update_layout(
        barmode='group',
        height=400,
        template='plotly_white',
        yaxis_title="Hours",
        xaxis_title="Week",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_planned_exec, use_container_width=True)
    
    if latest_week is not None:
        latest_planned = latest_week['PlannedHrs_Corrective'] + latest_week['PlannedHrs_Reliability']
        latest_executed = latest_week['ExecutedHrs_Corrective'] + latest_week['ExecutedHrs_Reliability']
        st.markdown(f"""
        **💬 Key Insight:** Latest week: {latest_planned} hrs planned vs {latest_executed} hrs executed ({latest_week['PlanAttainment']}% attainment)
        """)

st.markdown("---")

# Chart 5: Team Performance Comparison
col_team1, col_team2 = st.columns(2)

with col_team1:
    st.markdown("### 🔧 Team Performance by Week")
    
    fig_teams = go.Figure()
    
    fig_teams.add_trace(go.Bar(
        x=plot_data['Week'],
        y=plot_data['PlanAttainment_Corrective'],
        name='Corrective Team',
        marker_color='#ff7f0e',
        text=plot_data['PlanAttainment_Corrective'].apply(lambda x: f"{x}%"),
        textposition='outside'
    ))
    
    fig_teams.add_trace(go.Bar(
        x=plot_data['Week'],
        y=plot_data['PlanAttainment_Reliability'],
        name='Reliability Team',
        marker_color=SECONDARY_COLOR,
        text=plot_data['PlanAttainment_Reliability'].apply(lambda x: f"{x}%"),
        textposition='outside'
    ))
    
    fig_teams.add_hline(
        y=85, 
        line_dash="dot", 
        line_color="red",
        annotation_text="Target",
        annotation_position="right"
    )
    
    fig_teams.update_layout(
        barmode='group',
        yaxis_title="Attainment (%)",
        xaxis_title="Week",
        height=400,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_teams, use_container_width=True)
    
    if latest_week is not None:
        st.markdown(f"""
        **💬 Key Insight:** Corrective: {latest_week['PlanAttainment_Corrective']}%, Reliability: {latest_week['PlanAttainment_Reliability']}%
        """)

# Chart 6: PMR Metrics
with col_team2:
    st.markdown("### 📋 PMR (Preventive Maintenance) Performance")
    
    fig_pmr = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_pmr.add_trace(
        go.Bar(
            x=plot_data['Week'],
            y=plot_data['PMR_Pct'],
            name='PMR %',
            marker_color='steelblue',
            text=plot_data['PMR_Pct'].apply(lambda x: f"{x}%"),
            textposition='outside'
        ),
        secondary_y=False
    )
    
    fig_pmr.add_trace(
        go.Scatter(
            x=plot_data['Week'],
            y=plot_data['PMR_Completion'],
            mode='lines+markers',
            name='PMR Completion %',
            line=dict(color=PRIMARY_COLOR, width=3),
            marker=dict(size=10),
            text=plot_data['PMR_Completion'].apply(lambda x: f"{x}%"),
            textposition='top center'
        ),
        secondary_y=True
    )
    
    fig_pmr.update_xaxes(title_text="Week")
    fig_pmr.update_yaxes(title_text="PMR %", secondary_y=False)
    fig_pmr.update_yaxes(title_text="Completion %", secondary_y=True)
    
    fig_pmr.update_layout(
        height=400,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_pmr, use_container_width=True)
    
    if latest_week is not None:
        st.markdown(f"""
        **💬 Key Insight:** PMR focus at {latest_week['PMR_Pct']}% with {latest_week['PMR_Completion']}% completion rate
        """)

st.markdown("---")

# Detailed Data Table
st.markdown("## 📋 Detailed Weekly Metrics")

# Create displayable dataframe
display_df = df_filtered[['Week', 'WeekDate', 'Personnel', 'AvailableHours', 'PlanningRate', 
                          'PlanAttainment', 'PlanAttainment_Corrective', 
                          'PlanAttainment_Reliability', 'UnplannedJob_Pct', 
                          'PMR_Pct', 'PMR_Completion']].copy()

display_df.columns = ['Week', 'Date', 'Personnel', 'Available Hrs', 'Planning Rate %', 
                      'Plan Attainment %', 'Corrective %', 'Reliability %', 
                      'Unplanned %', 'PMR %', 'PMR Completion %']

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.markdown("---")

# Executive summary footer
st.markdown("## 📝 Summary Statistics")

week_count = db.get_week_count()
if week_count > 0:
    summary_col1, summary_col2, summary_col3 = st.columns(3)

    avg_row = avg_data

    with summary_col1:
        st.markdown(f"""
        ### Overall Averages ({week_count} weeks)
        - **Plan Attainment:** {avg_row['PlanAttainment']}%
        - **Planning Rate:** {avg_row['PlanningRate']}%
        - **Unplanned Work:** {avg_row['UnplannedJob_Pct']}%
        - **PMR %:** {avg_row['PMR_Pct']}%
        - **PMR Completion:** {avg_row['PMR_Completion']}%
        """)

    with summary_col2:
        st.markdown(f"""
        ### Team Performance
        - **Corrective Attainment:** {avg_row['PlanAttainment_Corrective']}%
        - **Reliability Attainment:** {avg_row['PlanAttainment_Reliability']}%
        - **Average Personnel:** {avg_row['Personnel']}
        - **Average Available Hrs:** {avg_row['AvailableHours']}
        """)

    with summary_col3:
        st.markdown(f"""
        ### Latest Week ({latest_week['Week']})
        - **Date:** {latest_week['WeekDate']}
        - **Plan Attainment:** {latest_week['PlanAttainment']}%
        - **Unplanned Work:** {latest_week['UnplannedJob_Pct']}%
        - **PMR %:** {latest_week['PMR_Pct']}%
        - **Personnel:** {latest_week['Personnel']}
        """)

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: {PRIMARY_COLOR};'>
    <p><strong>Maintenance KPI Dashboard | Streamlit Application</strong></p>
    <p>Total Weeks Tracked: {week_count}/52 | Data Stored in SQLite Database | An App by Jose Cedeno</p>
</div>
""", unsafe_allow_html=True)
