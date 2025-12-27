import streamlit as st
import pandas as pd
import requests
from datetime import date, timedelta

# --- Page Configuration ---
st.set_page_config(
    page_title="SAM.gov Opportunity Search",
    page_icon="🔍",
    layout="wide"
)

# --- API Key Management (IMPORTANT FOR DEPLOYMENT) ---
# For local development, you can uncomment the line below and paste your key.
# For deployment on Streamlit Community Cloud, use st.secrets.
# api_key = "YOUR_API_KEY_HERE" 

# Secure method for deployed apps:
try:
    api_key = st.secrets["SAM_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("⚠️ SAM_API_KEY not found. Please add it to your Streamlit secrets.")
    st.info("Create a file `.streamlit/secrets.toml` and add the following line:\n`SAM_API_KEY = \"Your-40-character-api-key-here\"`")
    st.stop()

# --- Helper Functions ---
def convert_df_to_csv(df):
    """Converts a DataFrame to a CSV string for downloading."""
    return df.to_csv(index=False).encode('utf-8')

# --- Main App UI ---
st.title("🔍 Federal Contract Opportunity Search")
st.markdown("Query the official [SAM.gov](https://sam.gov/) API to find federal contract opportunities.")

# --- Search Form ---
with st.sidebar:
    st.header("Search Parameters")
    
    # Date Pickers (Required)
    today = date.today()
    posted_from = st.date_input("Posted From", value=today - timedelta(days=7))
    posted_to = st.date_input("Posted To", value=today)

    # Dropdowns for Procurement and Set-Aside types
    ptype = st.selectbox(
        "Procurement Type",
        options=[
            ('All', ''), ('Justification (J&A)', 'u'), ('Pre-solicitation', 'p'),
            ('Award Notice', 'a'), ('Sources Sought', 'r'), ('Special Notice', 's'),
            ('Solicitation', 'o'), ('Sale of Surplus Property', 'g'),
            ('Combined Synopsis/Solicitation', 'k'), ('Intent to Bundle (DoD)', 'i')
        ],
        format_func=lambda x: x[0]
    )

    set_aside = st.selectbox(
        "Set-Aside Type",
        options=[
            ('Any', ''), ('Total Small Business', 'SBA'), ('Partial Small Business', 'SBP'),
            ('8(a)', '8A'), ('8(a) Sole Source', '8AN'), ('HUBZone', 'HZC'),
            ('HUBZone Sole Source', 'HZS'), ('SDVOSB', 'SDVOSBC'),
            ('SDVOSB Sole Source', 'SDVOSBSS'), ('WOSB', 'WOSB'), ('WOSB Sole Source', 'WOSBSS')
            # Add other set-aside types if needed
        ],
        format_func=lambda x: x[0]
    )

    # Optional Text Inputs
    title = st.text_input("Title Keywords")
    org_name = st.text_input("Organization Name", placeholder="e.g., Department of Defense")
    
    # NAICS Code Selection
    st.subheader("NAICS Code Selection")
    
    # Default NAICS codes
    default_naics_codes = {
        '423840': 'Industrial Supplies Merchant Wholesalers',
        '423420': 'Office Equipment Merchant Wholesalers',
        '423430': 'Computer and Computer Peripheral Equipment and Software Merchant Wholesalers',
        '423850': 'Service Establishment Equipment and Supplies Wholesalers',
        '424120': 'Stationery and Office Supplies Merchant Wholesalers',
        '423710': 'Hardware Merchant Wholesalers'
    }
    
    naics_mode = st.radio(
        "Choose NAICS filtering method:",
        options=["All NAICS Codes", "Default Codes", "Custom Code"],
        help="Select how you want to filter opportunities by NAICS codes"
    )
    
    naics_code = ''
    
    if naics_mode == "All NAICS Codes":
        st.info("🔍 Searching across all NAICS codes (no filtering)")
        naics_code = ''
        
    elif naics_mode == "Default Codes":
        st.write("Select from predefined NAICS codes:")
        
        # Select All checkbox
        select_all = st.checkbox("Select All Default Codes")
        
        if select_all:
            selected_codes = list(default_naics_codes.keys())
        else:
            # Multi-select for individual codes
            code_options = [f"{code} - {desc}" for code, desc in default_naics_codes.items()]
            selected_displays = st.multiselect(
                "Choose specific codes:",
                options=code_options,
                help="Select one or more NAICS codes to search"
            )
            selected_codes = [display.split(' - ')[0] for display in selected_displays]
        
        if selected_codes:
            naics_code = ','.join(selected_codes)
            st.success(f"Selected {len(selected_codes)} NAICS code(s): {', '.join(selected_codes)}")
        else:
            st.warning("Please select at least one NAICS code")
            
    elif naics_mode == "Custom Code":
        st.write("Enter a custom 6-digit NAICS code:")
        custom_code = st.text_input(
            "NAICS Code", 
            max_chars=6, 
            placeholder="e.g., 541511",
            help="Enter exactly 6 digits for a valid NAICS code"
        )
        
        if custom_code:
            if len(custom_code) == 6 and custom_code.isdigit():
                naics_code = custom_code
                st.success(f"✅ Valid NAICS code: {custom_code}")
            else:
                st.error("❌ NAICS code must be exactly 6 digits")
                naics_code = ''
    
    limit = st.slider("Max Records per Page", 1, 1000, 100)

    # Search button
    search_clicked = st.button("Search Opportunities", type="primary", use_container_width=True)

# --- Data Fetching and Display ---
if 'results_df' not in st.session_state:
    st.session_state.results_df = pd.DataFrame()

if search_clicked:
    with st.spinner("Searching..."):
        # --- Validation ---
        if not posted_from or not posted_to:
            st.error("'Posted From' and 'Posted To' dates are required.")
        elif (posted_to - posted_from).days > 365:
            st.error("The date range cannot be more than 1 year.")
        else:
            # --- Build API Request ---
            base_url = "https://api.sam.gov/opportunities/v2/search"
            params = {
                'api_key': api_key,
                'postedFrom': posted_from.strftime('%m/%d/%Y'),
                'postedTo': posted_to.strftime('%m/%d/%Y'),
                'limit': limit
            }
            if ptype[1]: params['ptype'] = ptype[1]
            if set_aside[1]: params['typeOfSetAside'] = set_aside[1]
            if title: params['title'] = title
            if org_name: params['organizationName'] = org_name
            if naics_code: params['ncode'] = naics_code

            # --- API Call ---
            try:
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()

                if 'opportunitiesData' in data and data['opportunitiesData']:
                    opportunities = data['opportunitiesData']
                    parsed_data = []
                    for opp in opportunities:
                        poc_list = opp.get('pointOfContact') or []
                        poc_info = ' | '.join([f"{p.get('fullname', 'N/A')}" for p in poc_list])
                        
                        perf_loc = opp.get('placeOfPerformance') or {}
                        city_obj, state_obj = perf_loc.get('city') or {}, perf_loc.get('state') or {}
                        loc_str = f"{city_obj.get('name', 'N/A')}, {state_obj.get('name', 'N/A')}"

                        parsed_data.append({
                            'Posted Date': opp.get('postedDate'),
                            'Title': opp.get('title'),
                            'Solicitation #': opp.get('solicitationNumber'),
                            'Agency': opp.get('fullParentPathName', '').split('.')[0],
                            'Set Aside': opp.get('setAside'),
                            'Response Deadline': opp.get('reponseDeadLine'),
                            'Status': 'Active' if opp.get('active') == 'Yes' else 'Archived',
                            'NAICS': opp.get('naicsCode'),
                            'Location': loc_str,
                            'Point of Contact': poc_info,
                            'UI Link': opp.get('uiLink')
                        })
                    st.session_state.results_df = pd.DataFrame(parsed_data)
                    st.success(f"Success! Found {data.get('totalRecords', 0)} total records. Displaying the first {len(parsed_data)}.")
                else:
                    st.warning("No opportunities found for your search criteria.")
                    st.session_state.results_df = pd.DataFrame()

            except requests.exceptions.HTTPError as e:
                st.error(f"API Error: {e.response.status_code}")
                try:
                    st.error(f"Details: {e.response.json().get('error', {}).get('message', 'No details provided.')}")
                except:
                    pass
                st.session_state.results_df = pd.DataFrame()
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
                st.session_state.results_df = pd.DataFrame()

# --- Display Results ---
if not st.session_state.results_df.empty:
    st.subheader("Search Results")
    # Make link clickable
    st.dataframe(
        st.session_state.results_df,
        column_config={
            "UI Link": st.column_config.LinkColumn(
                "UI Link",
                display_text="View on SAM.gov"
            )
        },
        use_container_width=True
    )
    
    csv_data = convert_df_to_csv(st.session_state.results_df)
    st.download_button(
       label="Download Data as CSV",
       data=csv_data,
       file_name=f"sam_opportunities_{today.strftime('%Y-%m-%d')}.csv",
       mime="text/csv",
       use_container_width=True
    )
else:
    st.info("Use the sidebar to start a new search.")
