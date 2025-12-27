import requests
import pandas as pd
from datetime import datetime
from flask import current_app

class SAMGovAPIClient:
    """Client for interacting with the SAM.gov API"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or current_app.config.get('SAM_API_KEY')
        self.base_url = "https://api.sam.gov/opportunities/v2/search"
    
    def search_opportunities(self, search_params):
        """
        Search for opportunities using the SAM.gov API
        
        Args:
            search_params (dict): Dictionary of search parameters
            
        Returns:
            dict: API response with opportunities data and metadata
        """
        if not self.api_key:
            raise ValueError("SAM.gov API key is required")
        
        # Add API key to parameters
        params = search_params.copy()
        params['api_key'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Process the response
            result = {
                'success': True,
                'total_records': data.get('totalRecords', 0),
                'opportunities': [],
                'error': None
            }
            
            if 'opportunitiesData' in data and data['opportunitiesData']:
                result['opportunities'] = self._process_opportunities(data['opportunitiesData'])
            
            return result
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"API Error: {e.response.status_code}"
            try:
                error_detail = e.response.json().get('error', {}).get('message', 'No details provided')
                error_msg += f" - {error_detail}"
            except:
                pass
            
            return {
                'success': False,
                'total_records': 0,
                'opportunities': [],
                'error': error_msg
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'total_records': 0,
                'opportunities': [],
                'error': f"Request failed: {str(e)}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'total_records': 0,
                'opportunities': [],
                'error': f"Unexpected error: {str(e)}"
            }
    
    def _process_opportunities(self, opportunities_data):
        """
        Process raw opportunities data into a structured format
        
        Args:
            opportunities_data (list): Raw opportunities data from API
            
        Returns:
            list: Processed opportunities data
        """
        processed_opportunities = []
        
        for opp in opportunities_data:
            # Process point of contact information
            poc_list = opp.get('pointOfContact') or []
            poc_info = ' | '.join([
                f"{p.get('fullname', 'N/A')}" for p in poc_list
            ])
            
            # Process place of performance
            perf_loc = opp.get('placeOfPerformance') or {}
            city_obj = perf_loc.get('city') or {}
            state_obj = perf_loc.get('state') or {}
            location = f"{city_obj.get('name', 'N/A')}, {state_obj.get('name', 'N/A')}"
            
            # Process agency information
            agency = opp.get('fullParentPathName', '').split('.')[0] if opp.get('fullParentPathName') else 'N/A'
            
            # Format dates
            posted_date = self._format_date(opp.get('postedDate'))
            response_deadline = self._format_date(opp.get('reponseDeadLine'))
            
            processed_opp = {
                'posted_date': posted_date,
                'title': opp.get('title', 'N/A'),
                'solicitation_number': opp.get('solicitationNumber', 'N/A'),
                'agency': agency,
                'set_aside': opp.get('setAside', 'N/A'),
                'response_deadline': response_deadline,
                'status': 'Active' if opp.get('active') == 'Yes' else 'Archived',
                'naics_code': opp.get('naicsCode', 'N/A'),
                'location': location,
                'point_of_contact': poc_info or 'N/A',
                'ui_link': opp.get('uiLink', ''),
                'description': opp.get('description', 'N/A')[:200] + '...' if opp.get('description') and len(opp.get('description', '')) > 200 else opp.get('description', 'N/A')
            }
            
            processed_opportunities.append(processed_opp)
        
        return processed_opportunities
    
    def _format_date(self, date_string):
        """
        Format date string for display
        
        Args:
            date_string (str): Date string from API
            
        Returns:
            str: Formatted date string
        """
        if not date_string:
            return 'N/A'
        
        try:
            # Try to parse and reformat the date
            # SAM.gov typically returns dates in various formats
            for fmt in ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y']:
                try:
                    date_obj = datetime.strptime(date_string, fmt)
                    return date_obj.strftime('%m/%d/%Y')
                except ValueError:
                    continue
            
            # If no format matches, return as-is
            return date_string
            
        except Exception:
            return date_string
    
    def opportunities_to_dataframe(self, opportunities):
        """
        Convert opportunities list to pandas DataFrame for easy export
        
        Args:
            opportunities (list): List of processed opportunities
            
        Returns:
            pandas.DataFrame: DataFrame with opportunities data
        """
        if not opportunities:
            return pd.DataFrame()
        
        # Create DataFrame with proper column names for export
        df_data = []
        for opp in opportunities:
            df_data.append({
                'Posted Date': opp['posted_date'],
                'Title': opp['title'],
                'Solicitation #': opp['solicitation_number'],
                'Agency': opp['agency'],
                'Set Aside': opp['set_aside'],
                'Response Deadline': opp['response_deadline'],
                'Status': opp['status'],
                'NAICS': opp['naics_code'],
                'Location': opp['location'],
                'Point of Contact': opp['point_of_contact'],
                'UI Link': opp['ui_link'],
                'Description': opp['description']
            })
        
        return pd.DataFrame(df_data)
    
    def export_to_csv(self, opportunities, filename=None):
        """
        Export opportunities to CSV format
        
        Args:
            opportunities (list): List of processed opportunities
            filename (str): Optional filename for the export
            
        Returns:
            str: CSV data as string
        """
        df = self.opportunities_to_dataframe(opportunities)
        return df.to_csv(index=False)

def get_api_client():
    """Get a configured API client instance"""
    return SAMGovAPIClient()
