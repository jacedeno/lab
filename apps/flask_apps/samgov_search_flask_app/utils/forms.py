from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField, IntegerField, TextAreaField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional
from wtforms.widgets import CheckboxInput, ListWidget
from datetime import date, timedelta

US_STATES = [
    ('', 'All States'), ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'),
    ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'),
    ('DE', 'Delaware'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'),
    ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'),
    ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'),
    ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'),
    ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'),
    ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'),
    ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'),
    ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'),
    ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'),
    ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'),
    ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming'),
    ('DC', 'District of Columbia'), ('PR', 'Puerto Rico'), ('VI', 'Virgin Islands')
]

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])

class SettingsForm(FlaskForm):
    sam_api_key = PasswordField('SAM.gov API Key', validators=[
        Optional(),
        Length(min=10, max=100, message='API key must be between 10 and 100 characters')
    ])
    submit = SubmitField('Save API Key')

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

    # New filters - State
    state = SelectField('State', choices=US_STATES, default='')

    # Classification Code
    classification_code = StringField('Classification Code', validators=[Optional(), Length(max=10)])

    # Status filter
    status = SelectField('Status', choices=[
        ('', 'All'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived')
    ], default='')

    # Response deadline range
    rdl_from = DateField('Response Deadline From', validators=[Optional()])
    rdl_to = DateField('Response Deadline To', validators=[Optional()])
    
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
        
        # Validate response deadline range if provided
        if self.rdl_from.data and self.rdl_to.data:
            if self.rdl_from.data > self.rdl_to.data:
                self.rdl_to.errors.append('Response deadline end date must be after start date')
                return False
            if (self.rdl_to.data - self.rdl_from.data).days > 365:
                self.rdl_to.errors.append('Response deadline range cannot be more than 1 year')
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
        if self.state.data:
            params['state'] = self.state.data
        if self.classification_code.data:
            params['ccode'] = self.classification_code.data
        if self.status.data:
            params['status'] = self.status.data
        
        naics_code = self.get_naics_code()
        if naics_code:
            params['ncode'] = naics_code
        
        # Response deadline range
        if self.rdl_from.data:
            params['rdlfrom'] = self.rdl_from.data.strftime('%m/%d/%Y')
        if self.rdl_to.data:
            params['rdlto'] = self.rdl_to.data.strftime('%m/%d/%Y')
        
        return params
