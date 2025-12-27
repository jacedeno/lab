from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationship with search history
    search_history = db.relationship('SearchHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def get_search_count(self):
        """Get total number of searches by this user"""
        return len(self.search_history)
    
    def get_recent_searches(self, limit=5):
        """Get recent searches by this user"""
        return SearchHistory.query.filter_by(user_id=self.id)\
                                 .order_by(SearchHistory.search_date.desc())\
                                 .limit(limit).all()
    
    def __repr__(self):
        return f'<User {self.email}>'

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    search_params = db.Column(db.Text, nullable=False)  # JSON string of search parameters
    results_count = db.Column(db.Integer, default=0)
    search_date = db.Column(db.DateTime, default=datetime.utcnow)
    export_count = db.Column(db.Integer, default=0)
    
    def set_search_params(self, params_dict):
        """Store search parameters as JSON"""
        self.search_params = json.dumps(params_dict)
    
    def get_search_params(self):
        """Retrieve search parameters as dictionary"""
        try:
            return json.loads(self.search_params)
        except:
            return {}
    
    def increment_export_count(self):
        """Increment the export count"""
        self.export_count += 1
        db.session.commit()
    
    def get_search_summary(self):
        """Get a human-readable summary of the search"""
        params = self.get_search_params()
        summary_parts = []
        
        if params.get('title'):
            summary_parts.append(f"Title: '{params['title']}'")
        if params.get('organizationName'):
            summary_parts.append(f"Org: '{params['organizationName']}'")
        if params.get('ncode'):
            summary_parts.append(f"NAICS: {params['ncode']}")
        if params.get('ptype'):
            summary_parts.append(f"Type: {params['ptype']}")
        
        date_range = f"{params.get('postedFrom', '')} to {params.get('postedTo', '')}"
        summary_parts.append(f"Dates: {date_range}")
        
        return " | ".join(summary_parts) if summary_parts else "General Search"
    
    def __repr__(self):
        return f'<SearchHistory {self.id} - User {self.user_id}>'

def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default users if they don't exist
        create_default_users()

def create_default_users():
    """Create the pre-configured user accounts"""
    default_users = [
        'shaheins@excemca.com',
        'hernandezt@excemca.com',
        'cedenoj@excemca.com'
    ]
    
    default_password = 'excemca#2025'
    
    for email in default_users:
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            user = User(email=email)
            user.set_password(default_password)
            db.session.add(user)
            print(f"Created user: {email}")
    
    try:
        db.session.commit()
        print("Default users created successfully")
    except Exception as e:
        db.session.rollback()
        print(f"Error creating default users: {e}")
