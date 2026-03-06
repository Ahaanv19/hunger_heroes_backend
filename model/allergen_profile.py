# allergen_profile.py
"""
Allergen Profile Model - Detailed allergen and dietary information for donations
"""

from datetime import datetime
from sqlalchemy.exc import IntegrityError
from __init__ import app, db


class AllergenProfile(db.Model):
    """
    Allergen Profile Model
    
    Stores detailed allergen and dietary information for each donation.
    Uses a 1:1 relationship with Donation for detailed allergen data.
    
    Attributes:
        id (Column): Integer, Primary Key
        donation_id (Column): String(50), Foreign Key to donations.id, UNIQUE
        contains_nuts (Column): Boolean
        contains_dairy (Column): Boolean
        contains_gluten (Column): Boolean
        contains_soy (Column): Boolean
        contains_shellfish (Column): Boolean
        contains_eggs (Column): Boolean
        other_allergens (Column): JSON, Custom/other allergens
        is_vegetarian (Column): Boolean
        is_vegan (Column): Boolean
        is_halal (Column): Boolean
        is_kosher (Column): Boolean
        created_at (Column): DateTime
        updated_at (Column): DateTime
    """
    __tablename__ = 'allergen_profiles'

    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.String(50), db.ForeignKey('donations.id'), unique=True, nullable=False)
    
    # Major allergens (binary flags)
    contains_nuts = db.Column(db.Boolean, default=False, nullable=False)
    contains_dairy = db.Column(db.Boolean, default=False, nullable=False)
    contains_gluten = db.Column(db.Boolean, default=False, nullable=False)
    contains_soy = db.Column(db.Boolean, default=False, nullable=False)
    contains_shellfish = db.Column(db.Boolean, default=False, nullable=False)
    contains_eggs = db.Column(db.Boolean, default=False, nullable=False)
    other_allergens = db.Column(db.JSON, nullable=True)  # ["sesame", "mustard", ...]
    
    # Dietary flags
    is_vegetarian = db.Column(db.Boolean, default=False, nullable=False)
    is_vegan = db.Column(db.Boolean, default=False, nullable=False)
    is_halal = db.Column(db.Boolean, default=False, nullable=False)
    is_kosher = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __init__(self, donation_id, contains_nuts=False, contains_dairy=False, 
                 contains_gluten=False, contains_soy=False, contains_shellfish=False,
                 contains_eggs=False, other_allergens=None,
                 is_vegetarian=False, is_vegan=False, is_halal=False, is_kosher=False):
        """
        Constructor for AllergenProfile.
        
        Args:
            donation_id (str): ID of related donation
            contains_nuts (bool): Contains tree nuts/peanuts
            contains_dairy (bool): Contains milk/dairy products
            contains_gluten (bool): Contains wheat/gluten
            contains_soy (bool): Contains soy
            contains_shellfish (bool): Contains shellfish
            contains_eggs (bool): Contains eggs
            other_allergens (list): Other allergens
            is_vegetarian (bool): Vegetarian (no meat)
            is_vegan (bool): Vegan (no animal products)
            is_halal (bool): Halal certified
            is_kosher (bool): Kosher certified
        """
        self.donation_id = donation_id
        self.contains_nuts = contains_nuts
        self.contains_dairy = contains_dairy
        self.contains_gluten = contains_gluten
        self.contains_soy = contains_soy
        self.contains_shellfish = contains_shellfish
        self.contains_eggs = contains_eggs
        self.other_allergens = other_allergens or []
        self.is_vegetarian = is_vegetarian
        self.is_vegan = is_vegan
        self.is_halal = is_halal
        self.is_kosher = is_kosher

    def create(self):
        """
        Add allergen profile to database.
        
        Returns:
            AllergenProfile: Created profile or None on error
        """
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def read(self):
        """
        Convert allergen profile to dictionary.
        
        Returns:
            dict: Profile data
        """
        return {
            'id': self.id,
            'donation_id': self.donation_id,
            'allergens': {
                'contains_nuts': self.contains_nuts,
                'contains_dairy': self.contains_dairy,
                'contains_gluten': self.contains_gluten,
                'contains_soy': self.contains_soy,
                'contains_shellfish': self.contains_shellfish,
                'contains_eggs': self.contains_eggs,
                'other': self.other_allergens
            },
            'dietary': {
                'is_vegetarian': self.is_vegetarian,
                'is_vegan': self.is_vegan,
                'is_halal': self.is_halal,
                'is_kosher': self.is_kosher
            },
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def update(self, data):
        """
        Update allergen profile with new data.
        
        Args:
            data (dict): Fields to update
        
        Returns:
            AllergenProfile: Updated profile or None on error
        """
        try:
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            db.session.commit()
            return self
        except IntegrityError:
            db.session.rollback()
            return None

    def delete(self):
        """
        Delete allergen profile from database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

    def has_allergen(self):
        """
        Check if donation has any allergen.
        
        Returns:
            bool: True if any allergen is present
        """
        return (self.contains_nuts or self.contains_dairy or 
                self.contains_gluten or self.contains_soy or 
                self.contains_shellfish or self.contains_eggs or 
                bool(self.other_allergens))

    def get_allergen_summary(self):
        """
        Get human-readable allergen summary.
        
        Returns:
            str: Comma-separated list of allergens
        """
        allergens = []
        if self.contains_nuts:
            allergens.append('Nuts')
        if self.contains_dairy:
            allergens.append('Dairy')
        if self.contains_gluten:
            allergens.append('Gluten')
        if self.contains_soy:
            allergens.append('Soy')
        if self.contains_shellfish:
            allergens.append('Shellfish')
        if self.contains_eggs:
            allergens.append('Eggs')
        if self.other_allergens:
            allergens.extend([a.capitalize() for a in self.other_allergens])
        
        return ', '.join(allergens) if allergens else 'No known allergens'

    def get_dietary_summary(self):
        """
        Get human-readable dietary restriction summary.
        
        Returns:
            str: Comma-separated list of dietary tags
        """
        dietary = []
        if self.is_vegetarian:
            dietary.append('Vegetarian')
        if self.is_vegan:
            dietary.append('Vegan')
        if self.is_halal:
            dietary.append('Halal')
        if self.is_kosher:
            dietary.append('Kosher')
        
        return ', '.join(dietary) if dietary else 'No special dietary tags'

    def __repr__(self):
        return f"AllergenProfile(donation_id={self.donation_id}, has_allergen={self.has_allergen()})"


def initAllergenProfiles():
    """
    Initialize allergen profiles table.
    """
    with app.app_context():
        db.create_all()
