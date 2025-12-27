#!/usr/bin/env python3
"""
Database initialization script for SAM.gov Flask App
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from utils.models import db, User

def init_database():
    """Initialize the database with tables and default user"""
    
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        
        # Drop all tables and recreate (for fresh start)
        db.drop_all()
        db.create_all()
        
        print("Database tables created successfully!")
        
        # Create users with specified credentials
        users_to_create = [
            "cedenoj@excemca.com",
            "hernandezt@excemca.com", 
            "shaheins@excemca.com"
        ]
        password = "excemca#2025"
        
        for email in users_to_create:
            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                user = User(
                    email=email,
                    password_hash=generate_password_hash(password)
                )
                db.session.add(user)
                print(f"User created: {email}")
            else:
                print(f"User already exists: {email}")
        
        # Create the 'guest' user with a specific password
        guest_email = "guest@excemca.com"
        guest_password = "12345"

        existing_guest_user = User.query.filter_by(email=guest_email).first()
        if not existing_guest_user:
            guest_user = User(
                email=guest_email,
                password_hash=generate_password_hash(guest_password)
            )
            db.session.add(guest_user)
            print(f"User created: {guest_email}")
        else:
            print(f"User already exists: {guest_email}")

        db.session.commit()
        
        print(f"\nAll users created with password: {password}")
        
        print("\nDatabase initialization completed!")
        print("\nTo start the application:")
        print("1. Set your environment variables (copy .env.example to .env)")
        print("2. Run: python app.py")
        print("3. Open your browser to: http://localhost:5000")

def create_sample_user():
    """Create a sample user for testing"""
    
    app = create_app()
    
    with app.app_context():
        sample_email = "user@example.com"
        sample_password = "user123"
        
        existing_user = User.query.filter_by(email=sample_email).first()
        if not existing_user:
            sample_user = User(
                email=sample_email,
                password_hash=generate_password_hash(sample_password)
            )
            db.session.add(sample_user)
            db.session.commit()
            
            print(f"Sample user created:")
            print(f"  Email: {sample_email}")
            print(f"  Password: {sample_password}")
        else:
            print(f"Sample user already exists: {sample_email}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--sample-user":
        create_sample_user()
    else:
        init_database()
