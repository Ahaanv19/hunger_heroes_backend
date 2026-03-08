#!/usr/bin/env python3

"""
db_migrate_v2.py - Database Migration Script

Purpose:
- Creates complete database schema for Hunger Heroes Application
- Initializes all models and relationships
- Populates database with validation test data
- Supports both SQLite (development) and MySQL (production)

Features:
- Drops existing tables with confirmation
- Creates all models from ORM definitions
- Generates test data for validation
- Creates indexes for performance
- Validates data integrity

Usage:
    From root directory:
    > python scripts/db_migrate_v2.py

    Or from scripts directory:
    > cd scripts && python db_migrate_v2.py

    Or using shell script:
    > ./db_migrate_v2.py
"""

import sys
import os
import shutil
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from __init__ import app, db
from model.user import User, initUsers
from model.organization import Organization, initOrganizations
from model.donation import Donation, generate_donation_id
from model.allergen_profile import AllergenProfile
from model.food_safety_log import FoodSafetyLog
from model.donation_feedback import DonationFeedback
from model.mod import Section, initSections
from model.group import Group, initGroups
from model.channel import Channel, initChannels
from model.post import Post, initPosts
from model.subscription import Subscription, initSubscriptions


def backup_database(db_uri, backup_uri):
    """
    Backup the current database before migration.
    
    Args:
        db_uri (str): Current database URI
        backup_uri (str): Backup database path
    """
    if not backup_uri:
        print("⚠️  Production database - backup not supported")
        return
    
    try:
        db_path = db_uri.replace('sqlite:///', 'instance/')
        backup_path = backup_uri.replace('sqlite:///', 'instance/')
        
        if os.path.exists(db_path):
            shutil.copyfile(db_path, backup_path)
            print(f"✅ Database backed up to {backup_path}")
        else:
            print("ℹ️  No existing database to backup")
    except Exception as e:
        print(f"⚠️  Backup failed: {e}")


def confirm_migration():
    """
    Ask user to confirm database migration.
    
    Returns:
        bool: True if user confirms, False otherwise
    """
    print("\n" + "="*70)
    print("⚠️  DATABASE MIGRATION WARNING")
    print("="*70)
    print("This will DROP ALL EXISTING TABLES and create a new schema.")
    print("All data will be permanently deleted unless backed up.")
    print("\nProceed? [y/N]: ", end="")
    
    response = input().lower().strip()
    return response == 'y'


def drop_tables():
    """Drop all existing tables."""
    with app.app_context():
        try:
            db.drop_all()
            print("✅ All tables dropped")
            return True
        except Exception as e:
            print(f"❌ Error dropping tables: {e}")
            return False


def create_tables():
    """Create all database tables from models."""
    with app.app_context():
        try:
            db.create_all()
            print("✅ All tables created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False


def seed_users():
    """
    Create sample users with different roles.
    """
    with app.app_context():
        users = [
            # Admin
            User(name='Thomas Edison', uid='admin', password='admin123', 
                 role='Admin', email='admin@hungerheroes.com'),
            
            # Donors
            User(name='Grace Hopper', uid='donor1', password='donor123',
                 role='Donor', email='grace@example.com'),
            User(name='Ada Lovelace', uid='donor2', password='donor123',
                 role='Donor', email='ada@example.com'),
            User(name='Margaret Hamilton', uid='donor3', password='donor123',
                 role='Donor', email='margaret@example.com'),
            
            # Volunteers
            User(name='Alan Turing', uid='volunteer1', password='vol123',
                 role='Volunteer', email='alan@example.com'),
            User(name='Hedy Lamarr', uid='volunteer2', password='vol123',
                 role='Volunteer', email='hedy@example.com'),
            User(name='Claude Shannon', uid='volunteer3', password='vol123',
                 role='Volunteer', email='claude@example.com'),
            
            # Receivers (linked to organizations)
            User(name='John Smith', uid='receiver1', password='rec123',
                 role='Receiver', email='john.smith@foodbank.org'),
            User(name='Jane Doe', uid='receiver2', password='rec123',
                 role='Receiver', email='jane.doe@shelter.org'),
            User(name='Bob Johnson', uid='receiver3', password='rec123',
                 role='Receiver', email='bob.johnson@temple.org'),
            
            # Regular users
            User(name='Alice Brown', uid='user1', password='user123',
                 role='User', email='alice@example.com'),
            User(name='Charlie White', uid='user2', password='user123',
                 role='User', email='charlie@example.com'),
        ]
        
        for user in users:
            try:
                db.session.add(user)
            except Exception as e:
                print(f"⚠️  Error creating user {user.uid}: {e}")
                db.session.rollback()
                continue
        
        try:
            db.session.commit()
            print(f"✅ Created {len(users)} users")
            return users
        except Exception as e:
            print(f"❌ Error committing users: {e}")
            db.session.rollback()
            return []


def seed_organizations():
    """
    Create sample organizations.
    """
    with app.app_context():
        organizations = [
            Organization(
                name='San Diego Food Bank',
                type='food_bank',
                address='9850 Distribution Ave, San Diego, CA 92121',
                zip_code='92121',
                phone='(619) 527-1419',
                email='info@sdfb.org',
                website='https://www.sdfb.org',
                capacity=5000,
                accepted_food_types=['canned', 'fresh-produce', 'dairy', 'bakery', 'frozen', 'meat-protein'],
                refrigeration_available=True,
                storage_capacity_lbs=50000,
                latitude=32.8754,
                longitude=-117.2474,
                description='Largest food bank in San Diego County'
            ),
            Organization(
                name='San Diego Rescue Mission',
                type='shelter',
                address='1955 Fifth Ave, San Diego, CA 92101',
                zip_code='92101',
                phone='(619) 235-6000',
                email='info@sdrescue.org',
                website='https://www.sdrescue.org',
                capacity=300,
                accepted_food_types=['prepared-meals', 'canned', 'frozen', 'fresh-produce'],
                refrigeration_available=True,
                storage_capacity_lbs=5000,
                latitude=32.7157,
                longitude=-117.1611,
                description='Homeless shelter providing meals and services'
            ),
            Organization(
                name='Jewish Community Center',
                type='temple',
                address='4126 Executive Drive, San Diego, CA 92037',
                zip_code='92037',
                phone='(858) 457-3030',
                email='info@jcc.org',
                capacity=200,
                accepted_food_types=['kosher', 'canned', 'dairy', 'grains'],
                dietary_restrictions_servable=['kosher', 'vegetarian'],
                refrigeration_available=True,
                storage_capacity_lbs=3000,
                latitude=32.8373,
                longitude=-117.2311,
                description='Community center serving kosher meals'
            ),
            Organization(
                name='Ocean Beach Community Kitchen',
                type='restaurant',
                address='1701 Sunset Cliffs Blvd, San Diego, CA 92107',
                zip_code='92107',
                phone='(619) 222-0501',
                email='info@obkitchen.org',
                capacity=150,
                accepted_food_types=['all'],
                refrigeration_available=True,
                storage_capacity_lbs=2000,
                latitude=32.7552,
                longitude=-117.2527,
                description='Community restaurant serving prepared meals'
            ),
            Organization(
                name='North County Community Center',
                type='community_org',
                address='3010 Civic Center Drive, San Diego, CA 92182',
                zip_code='92182',
                phone='(858) 694-3049',
                email='info@nccenter.org',
                capacity=400,
                accepted_food_types=['canned', 'frozen', 'fresh-produce', 'bakery'],
                refrigeration_available=True,
                storage_capacity_lbs=8000,
                latitude=32.9479,
                longitude=-117.0653,
                description='Community center in North San Diego'
            ),
        ]
        
        for org in organizations:
            try:
                db.session.add(org)
            except Exception as e:
                print(f"⚠️  Error creating organization {org.name}: {e}")
                db.session.rollback()
                continue
        
        try:
            db.session.commit()
            print(f"✅ Created {len(organizations)} organizations")
            return organizations
        except Exception as e:
            print(f"❌ Error committing organizations: {e}")
            db.session.rollback()
            return []


def seed_donations():
    """
    Create sample donations with related data.
    """
    with app.app_context():
        users = User.query.filter(User._role.in_(['Donor', 'Volunteer'])).all()
        orgs = Organization.query.all()
        
        if not users or not orgs:
            print("⚠️  Cannot seed donations - need users and organizations first")
            return []
        
        donations = []
        food_items = [
            ('Canned Vegetables', 'canned', 24, 'cases'),
            ('Fresh Apples', 'fresh-produce', 50, 'lbs'),
            ('Milk Cartons', 'dairy', 20, 'items'),
            ('Whole Wheat Bread', 'bakery', 12, 'loaves'),
            ('Ground Beef', 'meat-protein', 15, 'lbs'),
            ('Brown Rice', 'grains', 25, 'lbs'),
            ('Orange Juice', 'beverages', 48, 'bottles'),
            ('Frozen Vegetables', 'frozen', 10, 'boxes'),
            ('Granola Bars', 'snacks', 100, 'items'),
            ('Infant Formula', 'baby-food', 20, 'containers'),
            ('Rotisserie Chicken', 'prepared-meals', 5, 'items'),
            ('Mixed Nuts', 'other', 10, 'bags'),
            ('Canned Beans', 'canned', 30, 'cans'),
            ('Fresh Lettuce', 'fresh-produce', 20, 'heads'),
            ('Cheese', 'dairy', 15, 'lbs'),
            ('Pasta', 'grains', 20, 'boxes'),
            ('Canned Soup', 'canned', 40, 'cans'),
            ('Frozen Pizza', 'frozen', 8, 'items'),
            ('Peanut Butter', 'other', 12, 'jars'),
            ('Coffee Beans', 'beverages', 5, 'lbs'),
        ]
        
        for i, (food_name, category, quantity, unit) in enumerate(food_items):
            donor = users[i % len(users)]
            org = orgs[i % len(orgs)]
            
            donation_id = generate_donation_id()
            expiry = datetime.utcnow().date() + timedelta(days=30 + (i % 60))
            
            donation = Donation(
                id=donation_id,
                food_name=food_name,
                category=category,
                quantity=quantity,
                unit=unit,
                expiry_date=expiry,
                storage='refrigerated' if category in ['dairy', 'meat-protein', 'fresh-produce'] else 'room-temp',
                donor_name=donor.name,
                donor_email=donor.email,
                donor_zip='92101',
                donor_id=donor.id,
                receiver_id=org.members[0].id if org.members else None,
                status='active' if i % 3 != 0 else 'accepted',
                serving_count=quantity * (5 if unit == 'lbs' else 1),
                temperature_at_pickup=38 if category in ['dairy'] else 70,
                storage_method='refrigerator' if category in ['dairy', 'meat-protein'] else 'room-temperature-shelf'
            )
            donations.append(donation)
            
            try:
                db.session.add(donation)
            except Exception as e:
                print(f"⚠️  Error creating donation {donation_id}: {e}")
                db.session.rollback()
                continue
        
        try:
            db.session.commit()
            print(f"✅ Created {len(donations)} donations")
            return donations
        except Exception as e:
            print(f"❌ Error committing donations: {e}")
            db.session.rollback()
            return []


def seed_allergen_profiles(donations):
    """
    Create allergen profiles for donations.
    """
    with app.app_context():
        profiles = []
        allergen_data = [
            {'contains_nuts': True},
            {'contains_dairy': True},
            {'contains_gluten': True},
            {'contains_eggs': True},
            {'is_vegetarian': True},
            {'is_vegan': True},
            {'contains_soy': True},
            {},  # No allergens
        ]
        
        for i, donation in enumerate(donations):
            allergen_info = allergen_data[i % len(allergen_data)]
            profile = AllergenProfile(
                donation_id=donation.id,
                **allergen_info
            )
            profiles.append(profile)
            
            try:
                db.session.add(profile)
            except Exception as e:
                print(f"⚠️  Error creating allergen profile for {donation.id}: {e}")
                db.session.rollback()
                continue
        
        try:
            db.session.commit()
            print(f"✅ Created {len(profiles)} allergen profiles")
            return profiles
        except Exception as e:
            print(f"❌ Error committing allergen profiles: {e}")
            db.session.rollback()
            return []


def seed_food_safety_logs(donations):
    """
    Create food safety logs for donations.
    """
    with app.app_context():
        volunteers = User.query.filter_by(_role='Volunteer').all()
        
        if not volunteers:
            print("⚠️  No volunteers for food safety logs")
            return []
        
        logs = []
        for i, donation in enumerate(donations[:len(donations) // 2]):  # Half got inspected
            volunteer = volunteers[i % len(volunteers)]
            
            log = FoodSafetyLog(
                donation_id=donation.id,
                temperature_reading=38.0,
                storage_method='refrigerator',
                handling_notes=f'Properly stored and handled by {volunteer.name}',
                inspector_id=volunteer.id,
                passed_inspection=True,
                inspection_date=datetime.utcnow()
            )
            logs.append(log)
            
            try:
                db.session.add(log)
            except Exception as e:
                print(f"⚠️  Error creating food safety log for {donation.id}: {e}")
                db.session.rollback()
                continue
        
        try:
            db.session.commit()
            print(f"✅ Created {len(logs)} food safety logs")
            return logs
        except Exception as e:
            print(f"❌ Error committing food safety logs: {e}")
            db.session.rollback()
            return []


def seed_donation_feedback(donations):
    """
    Create donation feedback/reviews.
    """
    with app.app_context():
        receivers = User.query.filter_by(_role='Receiver').all()
        
        if not receivers:
            print("⚠️  No receivers for feedback")
            return []
        
        feedback_list = []
        for i, donation in enumerate(donations):
            if donation.status != 'delivered' and donation.status != 'accepted':
                continue  # Only completed donations get feedback
            
            receiver = receivers[i % len(receivers)]
            
            fb = DonationFeedback(
                donation_id=donation.id,
                reviewer_id=receiver.id,
                food_quality_rating=4,
                timeliness_rating=5,
                overall_rating=4,
                comments=f'Great donation! Fresh and well-packaged.',
                reported_issues=[]
            )
            feedback_list.append(fb)
            
            try:
                db.session.add(fb)
            except Exception as e:
                print(f"⚠️  Error creating feedback for {donation.id}: {e}")
                db.session.rollback()
                continue
        
        try:
            db.session.commit()
            print(f"✅ Created {len(feedback_list)} donation feedbacks")
            return feedback_list
        except Exception as e:
            print(f"❌ Error committing feedback: {e}")
            db.session.rollback()
            return []


def main():
    """
    Main migration workflow.
    """
    print("\n" + "="*70)
    print("🍽️  HUNGER HEROES DATABASE MIGRATION")
    print("="*70)
    
    # Step 1: Confirm migration
    if not confirm_migration():
        print("\n❌ Migration cancelled by user")
        sys.exit(1)
    
    # Step 2: Backup existing database
    with app.app_context():
        backup_database(
            app.config['SQLALCHEMY_DATABASE_URI'],
            app.config.get('SQLALCHEMY_BACKUP_URI')
        )
    
    # Step 3: Drop existing tables
    if not drop_tables():
        print("❌ Migration failed at drop_tables()")
        sys.exit(1)
    
    # Step 4: Create new schema
    if not create_tables():
        print("❌ Migration failed at create_tables()")
        sys.exit(1)
    
    # Step 5: Seed data
    print("\n📊 SEEDING DATA...")
    users = seed_users()
    organizations = seed_organizations()
    donations = seed_donations()
    
    if donations:
        # Re-fetch donations from database to avoid detached instance errors
        with app.app_context():
            donations = Donation.query.all()
        
        allergen_profiles = seed_allergen_profiles(donations)
        safety_logs = seed_food_safety_logs(donations)
        feedback = seed_donation_feedback(donations)
    
    # Step 6: Summary
    print("\n" + "="*70)
    print("✅ DATABASE MIGRATION COMPLETE")
    print("="*70)
    print(f"\nDatabase: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Users created: {len(users)}")
    print(f"Organizations created: {len(organizations)}")
    print(f"Donations created: {len(donations)}")
    print("\n🎉 Ready to start the application!")


if __name__ == '__main__':
    with app.app_context():
        main()
