# donation.py
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError
import string
import time
import random

from __init__ import app, db

# Allowed enum values
ALLOWED_CATEGORIES = [
    'canned', 'fresh-produce', 'dairy', 'bakery', 'meat-protein',
    'grains', 'beverages', 'frozen', 'snacks', 'baby-food',
    'prepared-meals', 'other'
]

ALLOWED_UNITS = [
    'items', 'lbs', 'kg', 'oz', 'cans', 'boxes', 'bags', 'trays', 'servings'
]

ALLOWED_STORAGE = ['room-temp', 'refrigerated', 'frozen', 'cool-dry']

ALLOWED_ALLERGENS = [
    'gluten', 'dairy', 'nuts', 'soy', 'eggs', 'shellfish', 'fish', 'none'
]

ALLOWED_DIETARY = [
    'vegetarian', 'vegan', 'halal', 'kosher', 'gluten-free', 'organic'
]

ALLOWED_STATUSES = ['active', 'accepted', 'delivered', 'expired', 'cancelled']


def generate_donation_id():
    """Generate a unique human-readable donation ID in the format HH-XXXXXX-XXXX."""
    timestamp = int(time.time() * 1000)
    base36 = ''
    chars = string.digits + string.ascii_uppercase
    while timestamp:
        timestamp, remainder = divmod(timestamp, 36)
        base36 = chars[remainder] + base36
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"HH-{base36[-6:]}-{suffix}"


class Donation(db.Model):
    """
    Donation Model
    
    Represents a food donation with barcode label data for the Hunger Heroes system.
    Tracks food details, donor info, safety/handling requirements, and acceptance status.
    """
    __tablename__ = 'donations'

    id = db.Column(db.String(50), primary_key=True)  # e.g. "HH-M3X7K9-AB2F"

    # Food details
    food_name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Safety & handling
    expiry_date = db.Column(db.Date, nullable=False)
    storage = db.Column(db.String(30), nullable=False)
    allergens = db.Column(db.JSON, nullable=True)
    dietary_tags = db.Column(db.JSON, nullable=True)

    # Donor info
    donor_name = db.Column(db.String(200), nullable=False)
    donor_email = db.Column(db.String(200), nullable=False)
    donor_phone = db.Column(db.String(30), nullable=True)
    donor_zip = db.Column(db.String(10), nullable=False)
    special_instructions = db.Column(db.Text, nullable=True)

    # Tracking
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    status = db.Column(db.String(20), default='active')
    accepted_by = db.Column(db.String(200), nullable=True)
    accepted_at = db.Column(db.DateTime, nullable=True)
    delivered_by = db.Column(db.String(200), nullable=True)
    delivered_at = db.Column(db.DateTime, nullable=True)
    scan_count = db.Column(db.Integer, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, id, food_name, category, quantity, unit, expiry_date, storage,
                 donor_name, donor_email, donor_zip, description='', allergens=None,
                 dietary_tags=None, donor_phone='', special_instructions='',
                 user_id=None, status='active'):
        self.id = id
        self.food_name = food_name
        self.category = category
        self.quantity = quantity
        self.unit = unit
        self.description = description
        self.expiry_date = expiry_date
        self.storage = storage
        self.allergens = allergens or []
        self.dietary_tags = dietary_tags or []
        self.donor_name = donor_name
        self.donor_email = donor_email
        self.donor_phone = donor_phone
        self.donor_zip = donor_zip
        self.special_instructions = special_instructions
        self.user_id = user_id
        self.status = status

    def __repr__(self):
        return f"<Donation {self.id} – {self.food_name} ({self.status})>"

    def to_dict(self):
        """Serialize the donation to a dictionary."""
        return {
            'id': self.id,
            'food_name': self.food_name,
            'category': self.category,
            'quantity': self.quantity,
            'unit': self.unit,
            'description': self.description,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'storage': self.storage,
            'allergens': self.allergens or [],
            'dietary_tags': self.dietary_tags or [],
            'donor_name': self.donor_name,
            'donor_email': self.donor_email,
            'donor_phone': self.donor_phone,
            'donor_zip': self.donor_zip,
            'special_instructions': self.special_instructions,
            'status': self.status,
            'scan_count': self.scan_count or 0,
            'accepted_by': self.accepted_by,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
            'delivered_by': self.delivered_by,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_dict_short(self):
        """Serialize a compact version for list views."""
        return {
            'id': self.id,
            'food_name': self.food_name,
            'category': self.category,
            'quantity': self.quantity,
            'unit': self.unit,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def read(self):
        """Alias for to_dict for consistency with other models."""
        return self.to_dict()

    @staticmethod
    def restore(data):
        """Restore donations from a list of dictionaries."""
        for item in data:
            donation = Donation.query.get(item.get('id'))
            if donation:
                continue  # skip if already exists
            try:
                expiry = item.get('expiry_date')
                if isinstance(expiry, str):
                    expiry = datetime.strptime(expiry, '%Y-%m-%d').date()
                donation = Donation(
                    id=item['id'],
                    food_name=item['food_name'],
                    category=item['category'],
                    quantity=item['quantity'],
                    unit=item['unit'],
                    expiry_date=expiry,
                    storage=item['storage'],
                    donor_name=item['donor_name'],
                    donor_email=item['donor_email'],
                    donor_zip=item['donor_zip'],
                    description=item.get('description', ''),
                    allergens=item.get('allergens', []),
                    dietary_tags=item.get('dietary_tags', []),
                    donor_phone=item.get('donor_phone', ''),
                    special_instructions=item.get('special_instructions', ''),
                    user_id=item.get('user_id'),
                    status=item.get('status', 'active'),
                )
                donation.scan_count = item.get('scan_count', 0)
                donation.accepted_by = item.get('accepted_by')
                if item.get('accepted_at'):
                    donation.accepted_at = datetime.fromisoformat(item['accepted_at'])
                donation.delivered_by = item.get('delivered_by')
                if item.get('delivered_at'):
                    donation.delivered_at = datetime.fromisoformat(item['delivered_at'])
                db.session.add(donation)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
        return


def initDonations():
    """Seed sample donations for development."""
    from datetime import timedelta

    samples = [
        {
            'food_name': 'Canned Tomato Soup',
            'category': 'canned',
            'quantity': 24,
            'unit': 'cans',
            'description': "Campbell's condensed, unopened",
            'expiry_date': date.today() + timedelta(days=180),
            'storage': 'room-temp',
            'allergens': ['gluten'],
            'dietary_tags': ['vegetarian'],
            'donor_name': 'Local Grocery Co.',
            'donor_email': 'donate@localgrocery.com',
            'donor_zip': '92101',
        },
        {
            'food_name': 'Fresh Bread Loaves',
            'category': 'bakery',
            'quantity': 15,
            'unit': 'items',
            'description': 'Whole wheat, baked today',
            'expiry_date': date.today() + timedelta(days=3),
            'storage': 'room-temp',
            'allergens': ['gluten'],
            'dietary_tags': ['vegan'],
            'donor_name': 'Sunrise Bakery',
            'donor_email': 'info@sunrisebakery.com',
            'donor_zip': '92102',
        },
        {
            'food_name': 'Mixed Frozen Vegetables',
            'category': 'frozen',
            'quantity': 30,
            'unit': 'bags',
            'description': 'Peas, carrots, corn, green beans',
            'expiry_date': date.today() + timedelta(days=365),
            'storage': 'frozen',
            'allergens': ['none'],
            'dietary_tags': ['vegan', 'gluten-free'],
            'donor_name': 'SD Community Farm',
            'donor_email': 'farm@sdcommunity.org',
            'donor_zip': '92103',
        },
        {
            'food_name': 'Organic Baby Food Pouches',
            'category': 'baby-food',
            'quantity': 48,
            'unit': 'items',
            'description': 'Assorted fruit & veggie purees',
            'expiry_date': date.today() + timedelta(days=90),
            'storage': 'room-temp',
            'allergens': ['none'],
            'dietary_tags': ['organic', 'vegan'],
            'donor_name': 'Happy Baby Foundation',
            'donor_email': 'give@happybaby.org',
            'donor_zip': '92104',
        },
        {
            'food_name': 'Rice & Pasta Variety Pack',
            'category': 'grains',
            'quantity': 20,
            'unit': 'boxes',
            'description': 'Brown rice, penne, spaghetti',
            'expiry_date': date.today() + timedelta(days=270),
            'storage': 'cool-dry',
            'allergens': ['gluten'],
            'dietary_tags': ['vegan'],
            'donor_name': 'Pantry Plus',
            'donor_email': 'donations@pantryplus.com',
            'donor_zip': '92105',
        },
    ]

    with app.app_context():
        db.create_all()
        for s in samples:
            existing = Donation.query.filter_by(food_name=s['food_name'], donor_email=s['donor_email']).first()
            if existing:
                continue
            donation = Donation(
                id=generate_donation_id(),
                status='active',
                **s
            )
            try:
                db.session.add(donation)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
        print("✅ Seeded sample donations")
