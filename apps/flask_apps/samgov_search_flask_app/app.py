from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect, CSRFError  # Add CSRFProtect and CSRFError
from datetime import datetime, date
import os

# Import our custom modules
from config import config
from utils.models import db, User, SearchHistory, init_db
from utils.forms import LoginForm, SearchForm
from utils.api_client import get_api_client

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.environ.get('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])

    # Initialize CSRF protection
    csrf = CSRFProtect(app)    
    
    # Initialize extensions
    init_db(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Routes
    @app.route('/')
    def index():
        """Redirect to login if not authenticated, otherwise to dashboard"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data.lower()).first()
            
            if user and user.check_password(form.password.data):
                login_user(user, remember=True)
                user.update_last_login()
                flash(f'Welcome back, {user.email}!', 'success')
                
                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password. Please try again.', 'danger')
        
        return render_template('login.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        """Logout user"""
        logout_user()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('login'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard with search form"""
        form = SearchForm()
        
        # Get user statistics
        search_count = current_user.get_search_count()
        recent_searches = current_user.get_recent_searches(limit=5)
        
        return render_template('dashboard.html', 
                             form=form, 
                             search_count=search_count,
                             recent_searches=recent_searches)
    
    @app.route('/search', methods=['POST'])
    @login_required
    def search():
        """Handle search requests"""
        form = SearchForm()
        
        if form.validate_on_submit():
            try:
                # Get API client
                api_client = get_api_client()
                
                # Get search parameters from form
                search_params = form.get_search_params()
                
                # Perform the search
                result = api_client.search_opportunities(search_params)
                
                if result['success']:
                    # Save search to history
                    search_history = SearchHistory(
                        user_id=current_user.id,
                        results_count=result['total_records']
                    )
                    search_history.set_search_params(search_params)
                    db.session.add(search_history)
                    db.session.commit()
                    
                    # Store results in session for display and export
                    session['last_search_results'] = result['opportunities']
                    session['last_search_params'] = search_params
                    session['last_search_total'] = result['total_records']
                    session['last_search_id'] = search_history.id
                    
                    flash(f'Search completed! Found {result["total_records"]} total records. Displaying the first {len(result["opportunities"])}.', 'success')
                    
                    return render_template('results.html', 
                                         opportunities=result['opportunities'],
                                         total_records=result['total_records'],
                                         search_params=search_params)
                else:
                    flash(f'Search failed: {result["error"]}', 'danger')
                    
            except Exception as e:
                flash(f'An unexpected error occurred: {str(e)}', 'danger')
        
        else:
            # Form validation failed
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field}: {error}', 'danger')
        
        # Return to dashboard with form errors
        search_count = current_user.get_search_count()
        recent_searches = current_user.get_recent_searches(limit=5)
        
        return render_template('dashboard.html', 
                             form=form, 
                             search_count=search_count,
                             recent_searches=recent_searches)
    
    @app.route('/export/csv')
    @login_required
    def export_csv():
        """Export last search results to CSV"""
        opportunities = session.get('last_search_results', [])
        search_id = session.get('last_search_id')
        
        if not opportunities:
            flash('No search results to export. Please perform a search first.', 'warning')
            return redirect(url_for('dashboard'))
        
        try:
            # Get API client for export functionality
            api_client = get_api_client()
            csv_data = api_client.export_to_csv(opportunities)
            
            # Update export count in search history
            if search_id:
                search_history = SearchHistory.query.get(search_id)
                if search_history and search_history.user_id == current_user.id:
                    search_history.increment_export_count()
            
            # Create response
            response = make_response(csv_data)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=sam_opportunities_{date.today().strftime("%Y-%m-%d")}.csv'
            
            flash('CSV export completed successfully.', 'success')
            return response
            
        except Exception as e:
            flash(f'Export failed: {str(e)}', 'danger')
            return redirect(url_for('dashboard'))
    
    @app.route('/history')
    @login_required
    def search_history():
        """Display user's search history"""
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        searches = SearchHistory.query.filter_by(user_id=current_user.id)\
                                    .order_by(SearchHistory.search_date.desc())\
                                    .paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('history.html', searches=searches)
    
    @app.route('/repeat_search/<int:search_id>')
    @login_required
    def repeat_search(search_id):
        """Repeat a previous search"""
        search_history = SearchHistory.query.get_or_404(search_id)
        
        # Verify the search belongs to the current user
        if search_history.user_id != current_user.id:
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        try:
            # Get the search parameters
            search_params = search_history.get_search_params()
            
            # Get API client and perform search
            api_client = get_api_client()
            result = api_client.search_opportunities(search_params)
            
            if result['success']:
                # Create new search history entry
                new_search = SearchHistory(
                    user_id=current_user.id,
                    results_count=result['total_records']
                )
                new_search.set_search_params(search_params)
                db.session.add(new_search)
                db.session.commit()
                
                # Store results in session
                session['last_search_results'] = result['opportunities']
                session['last_search_params'] = search_params
                session['last_search_total'] = result['total_records']
                session['last_search_id'] = new_search.id
                
                flash(f'Search repeated successfully! Found {result["total_records"]} total records.', 'success')
                
                return render_template('results.html', 
                                     opportunities=result['opportunities'],
                                     total_records=result['total_records'],
                                     search_params=search_params)
            else:
                flash(f'Search failed: {result["error"]}', 'danger')
                
        except Exception as e:
            flash(f'An error occurred while repeating the search: {str(e)}', 'danger')
        
        return redirect(url_for('search_history'))
    
    @app.route('/api/check_api_key')
    @login_required
    def check_api_key():
        """Check if SAM.gov API key is configured"""
        api_key = app.config.get('SAM_API_KEY')
        return jsonify({
            'configured': bool(api_key),
            'message': 'API key is configured' if api_key else 'SAM.gov API key not found. Please configure it in your environment variables.'
        })
    
    # Error handlers
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        flash('Your session has expired. Please refresh the page and try again.', 'warning')
        return redirect(request.referrer or url_for('dashboard'))    

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Template filters
    @app.template_filter('datetime')
    def datetime_filter(value):
        """Format datetime for display"""
        if value is None:
            return 'N/A'
        return value.strftime('%m/%d/%Y %I:%M %p')
    
    @app.template_filter('date')
    def date_filter(value):
        """Format date for display"""
        if value is None:
            return 'N/A'
        return value.strftime('%m/%d/%Y')
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)