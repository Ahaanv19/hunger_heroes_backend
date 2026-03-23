#!/usr/bin/env python
"""
Initialize Admin Panel Database
Run this script to create the Flag table for the admin panel
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from __init__ import app, db
from model.flag import Flag

def init_admin_db():
    """Initialize the admin database tables"""
    with app.app_context():
        print("Creating admin database tables...")
        
        try:
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Verify Flag table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'flags' in tables:
                print("✓ Flag table verified in database")
                columns = [col['name'] for col in inspector.get_columns('flags')]
                print(f"✓ Flag table columns: {', '.join(columns)}")
            else:
                print("✗ Flag table not found in database")
                return False
            
            print("\n✓ Admin panel database initialization complete!")
            return True
            
        except Exception as e:
            print(f"✗ Error creating database tables: {e}")
            return False

if __name__ == '__main__':
    success = init_admin_db()
    sys.exit(0 if success else 1)
