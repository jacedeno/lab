from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField, IntegerField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from wtforms.widgets import CheckboxInput, ListWidget
from datetime import date, timedelta

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])

class MultiCheckboxField(SelectMultipleField):
    """Custom field for multiple checkboxes"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class SearchForm(FlaskForm):
    # Date fields (required)
    posted_from = DateField('Posted From', validators=[DataRequired()], default=lambda: date.today() - timedelta(days=7))
    posted_to = DateField('Posted To', validators=[DataRequired()], default=date.today)
    
    # Procurement type dropdown
    ptype = SelectField('Procurement Type', choices=[
        ('', 'All'),
        ('u', 'Justification (J&A)'),
        ('p', 'Pre-solicitation'),
        ('a', 'Award Notice'),
        ('r', 'Sources Sought'),
        ('s', 'Special Notice'),
        ('o', 'Solicitation'),
        ('g', 'Sale of Surplus Property'),
        ('k', 'Combined Synopsis/Solicitation'),
        ('i', 'Intent to Bundle (DoD)')
    ], default='')
    
    # Set-aside type dropdown
    set_aside = SelectField('Set-Aside Type', choices=[
        ('', 'Any'),
        ('SBA', 'Total Small Business'),
        ('SBP', 'Partial Small Business'),
        ('8A', '8(a)'),
        ('8AN', '8(a) Sole Source'),
        ('HZC', 'HUBZone'),
        ('HZS', 'HUBZone Sole Source'),
        ('SDVOSBC', 'SDVOSB'),
        ('SDVOSBSS', 'SDVOSB Sole Source'),
        ('WOSB', 'WOSB'),
        ('WOSBSS', 'WOSB Sole Source')
    ], default='')
    
    # Optional text inputs
    title = StringField('Title Keywords', validators=[Optional(), Length(max=200)])
    org_name = StringField('Organization Name', validators=[Optional(), Length(max=200)])
    
    # NAICS code selection
    naics_mode = SelectField('NAICS Filtering', choices=[
        ('all', 'All NAICS Codes'),
        ('default', 'Default Codes'),
        ('custom', 'Custom Code')
    ], default='all')
    
    # Default NAICS codes (multiple selection)
    default_naics = MultiCheckboxField('Default NAICS Codes', choices=[
        ('None', 'None - No NAICS Code Specified'),
        ('423840', '423840 - Industrial Supplies Merchant Wholesalers'),
        ('423420', '423420 - Office Equipment Merchant Wholesalers'),
        ('423430', '423430 - Computer and Computer Peripheral Equipment and Software Merchant Wholesalers'),
        ('423850', '423850 - Service Establishment Equipment and Supplies Wholesalers'),
        ('424120', '424120 - Stationery and Office Supplies Merchant Wholesalers'),
        ('423710', '423710 - Hardware Merchant Wholesalers')
    ])
    
    # Custom NAICS code
    custom_naics = StringField('Custom NAICS Code', validators=[
        Optional(), 
        Length(min=6, max=6, message='NAICS code must be exactly 6 digits')
    ])
    
    # Results limit
    limit = IntegerField('Max Records per Page', validators=[
        DataRequired(),
        NumberRange(min=1, max=1000, message='Limit must be between 1 and 1000')
    ], default=100)
    
    def validate(self, extra_validators=None):
        """Custom validation for the search form"""
        if not super().validate(extra_validators):
            return False
        
        # Validate date range
        if self.posted_from.data and self.posted_to.data:
            if self.posted_from.data > self.posted_to.data:
                self.posted_to.errors.append('End date must be after start date')
                return False
            
            # Check if date range is more than 1 year
            if (self.posted_to.data - self.posted_from.data).days > 365:
                self.posted_to.errors.append('Date range cannot be more than 1 year')
                return False
        
        # Validate custom NAICS code if selected
        if self.naics_mode.data == 'custom' and self.custom_naics.data:
            if not self.custom_naics.data.isdigit():
                self.custom_naics.errors.append('NAICS code must contain only digits')
                return False
        
        return True
    
    def get_naics_code(self):
        """Get the appropriate NAICS code based on the selected mode"""
        if self.naics_mode.data == 'all':
            return ''
        elif self.naics_mode.data == 'default':
            if self.default_naics.data:
                return ','.join(self.default_naics.data)
            return ''
        elif self.naics_mode.data == 'custom':
            return self.custom_naics.data or ''
        return ''
    
    def get_search_params(self):
        """Get all search parameters as a dictionary for API call"""
        params = {
            'postedFrom': self.posted_from.data.strftime('%m/%d/%Y') if self.posted_from.data else '',
            'postedTo': self.posted_to.data.strftime('%m/%d/%Y') if self.posted_to.data else '',
            'limit': self.limit.data
        }
        
        # Add optional parameters if they have values
        if self.ptype.data:
            params['ptype'] = self.ptype.data
        if self.set_aside.data:
            params['typeOfSetAside'] = self.set_aside.data
        if self.title.data:
            params['title'] = self.title.data
        if self.org_name.data:
            params['organizationName'] = self.org_name.data
        
        naics_code = self.get_naics_code()
        if naics_code:
            params['ncode'] = naics_code
        
        return params
