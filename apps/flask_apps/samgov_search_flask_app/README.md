# SAM.gov Federal Contract Opportunity Search - Flask Application

A professional Flask web application for searching federal contract opportunities using the official SAM.gov API. This application provides a modern, user-friendly interface that improves upon the basic Streamlit version with enhanced functionality, better design, and enterprise-grade features.

## Features

### 🔑 Multi-API Key Management
- **Personal API Keys**: Each user can store multiple SAM.gov API keys
- **Custom Nicknames**: Assign friendly names to identify each API key
- **Easy Switching**: Set any key as active with one click
- **Per-User Storage**: API keys are stored securely in user profile

### 🔍 Advanced Search Capabilities
- **Date Range Filtering**: Search opportunities by posting date range
- **Procurement Type Selection**: Filter by various procurement types (solicitations, awards, etc.)
- **Set-Aside Type Filtering**: Target specific set-aside categories (small business, 8(a), etc.)
- **NAICS Code Support**: Filter by industry codes with predefined options or custom codes
- **Keyword Search**: Search by title keywords and organization names
- **Results Limiting**: Control the number of results returned

### 👤 User Management
- **Secure Authentication**: Login system with password hashing
- **User Sessions**: Persistent login sessions with remember me functionality
- **Search History**: Track and manage previous searches
- **Personal Dashboard**: User-specific statistics and recent activity
- **Multiple API Keys**: Each user can store and manage several API keys with nicknames

### 📊 Professional Interface
- **SAM.gov Inspired Design**: Professional government-style interface
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Interactive Tables**: Sortable columns and detailed opportunity views
- **Export Functionality**: Download search results as CSV files
- **Real-time Validation**: Form validation with helpful error messages

### 🔧 Technical Features
- **Database Integration**: SQLite database for user data and search history
- **API Integration**: Direct connection to SAM.gov opportunities API
- **Error Handling**: Comprehensive error handling and user feedback
- **Security**: CSRF protection, secure sessions, and input validation
- **Performance**: Optimized queries and efficient data processing

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- SAM.gov API key (free registration required)

### Quick Start

1. **Clone or download the application**
   ```bash
   cd samgov_search_flask_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit the `.env` file and add your SAM.gov API key:
   ```
   SAM_API_KEY=your_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

4. **Initialize the database**
   ```bash
   python init_db.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser to: http://localhost:5000

## Default Login Credentials

User accounts are statically defined in `init_db.py` and created when the database is initialized. There is no self-registration — only the following accounts exist:

| Email | Password |
|-------|----------|
| cedenoj@excemca.com | excemca#2025 |
| hernandezt@excemca.com | excemca#2025 |
| shaheins@excemca.com | excemca#2025 |
| guest@excemca.com | 12345 |

> **Note:** Passwords cannot be changed from the UI. To add or modify users, update `init_db.py` and re-run the initialization script.

### Initialize the database (first time or after reset)

```bash
docker exec -it samgov-app python init_db.py
```

> **Warning:** `init_db.py` drops and recreates all tables. Running it again will erase all search history.

## Getting a SAM.gov API Key

1. Visit [SAM.gov](https://sam.gov/content/api)
2. Create a free account
3. Request an API key for the Opportunities API
4. Add the API key to your user profile in the Settings page

**Adding API Keys in Settings:**
- Navigate to Settings
- Enter a nickname (e.g., "Work Account", "Personal")
- Paste your SAM.gov API key
- Click "Test Connection" to validate
- Click "Add API Key" to save

You can add multiple API keys and switch between them at any time.

## Configuration

### Environment Variables

The application uses the following environment variables:

- `SAM_API_KEY`: Fallback SAM.gov API key (optional, for backward compatibility)
- `SECRET_KEY`: Flask secret key for sessions (required)
- `DATABASE_URL`: Database connection string (optional, defaults to SQLite)
- `FLASK_ENV`: Environment mode (development/production)

**Note:** Users can add their own API keys from the Settings page. The global `SAM_API_KEY` is only used as a fallback when a user has not added their own key.

### Database Configuration

By default, the application uses SQLite for simplicity. For production use, you can configure PostgreSQL or MySQL by setting the `DATABASE_URL` environment variable.

## Usage Guide

### 1. Login
- Navigate to the application URL
- Enter your email and password
- Click "Sign In"

### 2. Dashboard
- View your search statistics
- Access recent searches
- Check API connection status

### 3. Performing Searches
- Set date range (required)
- Choose procurement and set-aside types (optional)
- Enter keywords for title or organization (optional)
- Select NAICS codes or enter custom code (optional)
- Set results limit (1-1000)
- Click "Search Opportunities"

### 4. Viewing Results
- Browse opportunities in the interactive table
- Sort by any column
- View detailed information in modal popups
- Click external links to view full details on SAM.gov

### 5. Exporting Data
- Click "Export to CSV" on the results page
- Download includes all search results with full details

### 6. Search History
- View all previous searches
- See search parameters and result counts
- Repeat previous searches with one click
- Track export activity

## API Integration

The application integrates with the SAM.gov Opportunities API v2:
- **Base URL**: https://api.sam.gov/opportunities/v2/search
- **Authentication**: API key required
- **Rate Limits**: Follows SAM.gov API guidelines
- **Data Processing**: Automatic parsing and formatting of opportunity data

## File Structure

```
samgov_search_flask_app/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── init_db.py            # Database initialization script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── utils/
│   ├── __init__.py
│   ├── models.py         # Database models (User, SearchHistory, UserAPIKey)
│   ├── forms.py          # WTForms form definitions
│   └── api_client.py     # SAM.gov API client
├── templates/
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── dashboard.html    # Main dashboard
│   ├── results.html      # Search results
│   ├── history.html      # Search history
│   ├── settings.html     # User settings and API key management
│   └── errors/
│       ├── 404.html      # 404 error page
│       └── 500.html      # 500 error page
└── static/
    ├── css/
    │   └── style.css     # Custom styles
    └── js/
        └── main.js       # JavaScript functionality
```

## Security Features

- **Password Hashing**: Secure password storage using Werkzeug
- **CSRF Protection**: Forms protected against cross-site request forgery
- **Session Security**: Secure session management with Flask-Login
- **Input Validation**: Server-side validation of all user inputs
- **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection
- **XSS Protection**: Template escaping prevents cross-site scripting

## Troubleshooting

### Common Issues

1. **API Key Not Working**
   - Verify your API key is correct in the `.env` file
   - Check that your SAM.gov account is active
   - Ensure you have access to the Opportunities API

2. **Database Errors**
   - Run `python init_db.py` to recreate the database
   - Check file permissions in the application directory

3. **Import Errors**
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

4. **Search Returns No Results**
   - Verify your search parameters aren't too restrictive
   - Check the date range (opportunities may not exist for all dates)
   - Ensure your API key has proper permissions

### Debug Mode

To run in debug mode for development:
```bash
export FLASK_ENV=development
python app.py
```

## Contributing

This application is designed to be easily extensible. Key areas for enhancement:

- Additional search filters
- Advanced data visualization
- Email notifications for new opportunities
- Integration with other government APIs
- Enhanced user management features

## License

This project is provided as-is for educational and professional use. Please ensure compliance with SAM.gov API terms of service when using this application.

## Support

For issues related to:
- **SAM.gov API**: Contact SAM.gov support
- **Application bugs**: Check the error logs and verify your configuration
- **Feature requests**: Consider contributing to the codebase

## Comparison with Streamlit Version

This Flask application provides several advantages over the basic Streamlit version:

### Enhanced Features
- **User Authentication**: Multi-user support with secure login
- **Data Persistence**: Search history and user preferences saved
- **Professional UI**: Government-grade interface design
- **Better Performance**: Optimized database queries and caching
- **Export Options**: Multiple data export formats
- **Error Handling**: Comprehensive error management and user feedback

### Enterprise Ready
- **Security**: Production-ready security features
- **Scalability**: Database-backed architecture
- **Customization**: Easily customizable and extensible
- **Deployment**: Ready for production deployment
- **Monitoring**: Built-in logging and performance tracking

This Flask application is ideal for organizations that need a professional, secure, and scalable solution for federal contract opportunity research.
