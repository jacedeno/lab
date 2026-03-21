import requests
import pandas as pd
from datetime import datetime
from flask import current_app

class SAMGovAPIClient:
    """Client for interacting with the SAM.gov API"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or current_app.config.get('SAM_API_KEY')
        self.base_url = "https://api.sam.gov/opportunities/v2/search"
        self.alpha_url = "https://api-alpha.sam.gov/opportunities/v2/search"
    
    def test_connection(self, api_key=None):
        """
        Test if the API key is valid by making a minimal request
        
        Args:
            api_key (str): Optional API key to test
            
        Returns:
            dict: Result with success status and message
        """
        test_key = api_key or self.api_key
        if not test_key:
            return {'success': False, 'message': 'API key is required'}
        
        try:
            params = {
                'api_key': test_key,
                'postedFrom': '01/01/2024',
                'postedTo': '01/02/2024',
                'limit': 1
            }
            response = requests.get(self.base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                return {'success': True, 'message': 'API key is valid'}
            elif response.status_code == 401:
                return {'success': False, 'message': 'Invalid API key'}
            elif response.status_code == 403:
                return {'success': False, 'message': 'API key does not have permission'}
            else:
                return {'success': False, 'message': f'Error: {response.status_code}'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': f'Connection failed: {str(e)}'}
    
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
        
        params = search_params.copy()
        params['api_key'] = self.api_key
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
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
        Process raw opportunities data into a structured format with ALL fields
        
        Args:
            opportunities_data (list): Raw opportunities data from API
            
        Returns:
            list: Processed opportunities data with all available fields
        """
        processed_opportunities = []
        
        for opp in opportunities_data:
            processed_opp = self._process_single_opportunity(opp)
            processed_opportunities.append(processed_opp)
        
        return processed_opportunities
    
    def _process_single_opportunity(self, opp):
        """
        Process a single opportunity record with all fields
        
        Args:
            opp (dict): Raw opportunity data from API
            
        Returns:
            dict: Fully processed opportunity with all fields
        """
        poc_list = opp.get('pointOfContact') or []
        
        poc_names = []
        poc_emails = []
        poc_phones = []
        for p in poc_list:
            if p.get('fullname'):
                poc_names.append(p.get('fullname'))
            if p.get('email'):
                poc_emails.append(p.get('email'))
            if p.get('phone'):
                poc_phones.append(p.get('phone'))
        
        perf_loc = opp.get('placeOfPerformance') or {}
        city_obj = perf_loc.get('city') or {}
        state_obj = perf_loc.get('state') or {}
        country_obj = perf_loc.get('country') or {}
        
        award_data = opp.get('award') or {}
        awardee_data = award_data.get('awardee') or {}
        awardee_location = awardee_data.get('location') or {}
        awardee_city = awardee_location.get('city') or {}
        awardee_state = awardee_location.get('state') or {}
        awardee_country = awardee_location.get('country') or {}
        
        office_addr = opp.get('officeAddress') or {}
        
        processed_opp = {
            'notice_id': opp.get('noticeId', 'N/A'),
            'title': opp.get('title', 'N/A'),
            'solicitation_number': opp.get('solicitationNumber', 'N/A'),
            'full_parent_path_name': opp.get('fullParentPathName', 'N/A'),
            'full_parent_path_code': opp.get('fullParentPathCode', 'N/A'),
            'posted_date': self._format_date(opp.get('postedDate')),
            'type': opp.get('type', 'N/A'),
            'base_type': opp.get('baseType', 'N/A'),
            'archive_type': opp.get('archiveType', 'N/A'),
            'archive_date': self._format_date(opp.get('archiveDate')),
            'set_aside': opp.get('setAside', 'N/A'),
            'set_aside_code': opp.get('setAsideCode', 'N/A'),
            'response_deadline': self._format_date(opp.get('reponseDeadLine')),
            'naics_code': opp.get('naicsCode', 'N/A'),
            'classification_code': opp.get('classificationCode', 'N/A'),
            'status': 'Active' if opp.get('active') == 'Yes' else 'Archived',
            'active': opp.get('active', 'N/A'),
            
            'award_number': award_data.get('number', 'N/A'),
            'award_amount': award_data.get('amount', 'N/A'),
            'award_date': self._format_date(award_data.get('date')),
            'awardee_name': awardee_data.get('name', 'N/A'),
            'awardee_uei': awardee_data.get('ueiSAM', 'N/A'),
            'awardee_city': awardee_city.get('name', 'N/A') if isinstance(awardee_city, dict) else awardee_city,
            'awardee_state': awardee_state.get('name', 'N/A') if isinstance(awardee_state, dict) else awardee_state,
            'awardee_country': awardee_country.get('name', 'N/A') if isinstance(awardee_country, dict) else awardee_country,
            
            'poc_name': ' | '.join(poc_names) if poc_names else 'N/A',
            'poc_email': ' | '.join(poc_emails) if poc_emails else 'N/A',
            'poc_phone': ' | '.join(poc_phones) if poc_phones else 'N/A',
            
            'description': opp.get('description', 'N/A'),
            'additional_info_link': opp.get('additionalInfoLink', 'N/A'),
            'ui_link': opp.get('uiLink', 'N/A'),
            'resource_links': ' | '.join(opp.get('resourceLinks', []) or ['N/A']),
            
            'location_city': city_obj.get('name', 'N/A') if isinstance(city_obj, dict) else city_obj,
            'location_state': state_obj.get('name', 'N/A') if isinstance(state_obj, dict) else state_obj,
            'location_country': country_obj.get('name', 'N/A') if isinstance(country_obj, dict) else country_obj,
            'location_zip': perf_loc.get('zip', 'N/A'),
            
            'office_city': office_addr.get('city', 'N/A'),
            'office_state': office_addr.get('state', 'N/A'),
            'office_zip': office_addr.get('zipcode', 'N/A'),
            
            'organization_type': opp.get('organizationType', 'N/A'),
        }
        
        return processed_opp
    
    def _format_date(self, date_string):
        """Format date string for display"""
        if not date_string:
            return 'N/A'
        
        try:
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y', '%m-%d-%Y']:
                try:
                    date_obj = datetime.strptime(date_string, fmt)
                    return date_obj.strftime('%m/%d/%Y')
                except ValueError:
                    continue
            return date_string
        except:
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
        
        df_data = []
        for opp in opportunities:
            df_data.append({
                'Notice ID': opp.get('notice_id', 'N/A'),
                'Title': opp.get('title', 'N/A'),
                'Solicitation Number': opp.get('solicitation_number', 'N/A'),
                'Status': opp.get('status', 'N/A'),
                'Posted Date': opp.get('posted_date', 'N/A'),
                'Response Deadline': opp.get('response_deadline', 'N/A'),
                'Agency': opp.get('full_parent_path_name', 'N/A'),
                'Set-Aside': opp.get('set_aside', 'N/A'),
                'Set-Aside Code': opp.get('set_aside_code', 'N/A'),
                'NAICS Code': opp.get('naics_code', 'N/A'),
                'Classification Code': opp.get('classification_code', 'N/A'),
                'Procurement Type': opp.get('type', 'N/A'),
                'Base Type': opp.get('base_type', 'N/A'),
                'Location City': opp.get('location_city', 'N/A'),
                'Location State': opp.get('location_state', 'N/A'),
                'Location Zip': opp.get('location_zip', 'N/A'),
                'POC Name': opp.get('poc_name', 'N/A'),
                'POC Email': opp.get('poc_email', 'N/A'),
                'POC Phone': opp.get('poc_phone', 'N/A'),
                'Award Number': opp.get('award_number', 'N/A'),
                'Award Amount': opp.get('award_amount', 'N/A'),
                'Award Date': opp.get('award_date', 'N/A'),
                'Awardee Name': opp.get('awardee_name', 'N/A'),
                'Awardee UEI': opp.get('awardee_uei', 'N/A'),
                'Office City': opp.get('office_city', 'N/A'),
                'Office State': opp.get('office_state', 'N/A'),
                'Description': opp.get('description', 'N/A'),
                'UI Link': opp.get('ui_link', 'N/A'),
            })
        
        return pd.DataFrame(df_data)
    
    def export_to_csv(self, opportunities):
        """Export opportunities to CSV format"""
        df = self.opportunities_to_dataframe(opportunities)
        return df.to_csv(index=False)
    
    def export_to_excel(self, opportunities, sheet_names=None):
        """
        Export opportunities to Excel format
        
        Args:
            opportunities (list): List of processed opportunities
            sheet_names (list): List of sheet names (unused, kept for compatibility)
            
        Returns:
            bytes: Excel file content
        """
        from io import BytesIO
        
        df = self.opportunities_to_dataframe(opportunities)
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Data', index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Data']
            
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        return output.getvalue()

def get_api_client(api_key=None):
    """Get a configured API client instance"""
    return SAMGovAPIClient(api_key)
