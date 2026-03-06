# donation_feedback.py
"""
Donation Feedback Model - Reviews and ratings for donations
"""

from datetime import datetime
from sqlalchemy.exc import IntegrityError
from __init__ import app, db


class DonationFeedback(db.Model):
    """
    Donation Feedback Model
    
    Stores feedback and ratings for donations from receivers/organizations.
    Multiple feedback entries per donation allowed.
    
    Attributes:
        id (Column): Integer, Primary Key
        donation_id (Column): String(50), Foreign Key to donations.id
        reviewer_id (Column): Integer, Foreign Key to users.id
        food_quality_rating (Column): Integer (1-5 stars)
        timeliness_rating (Column): Integer (1-5 stars) - On-time delivery
        overall_rating (Column): Integer (1-5 stars)
        comments (Column): Text - Feedback comments
        reported_issues (Column): JSON - List of issues encountered
        created_at (Column): DateTime
        updated_at (Column): DateTime
    """
    __tablename__ = 'donation_feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    donation_id = db.Column(db.String(50), db.ForeignKey('donations.id'), nullable=False, index=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Ratings (1-5 stars)
    food_quality_rating = db.Column(db.Integer, nullable=True)  # 1-5: Condition, freshness, quality
    timeliness_rating = db.Column(db.Integer, nullable=True)  # 1-5: On-time, timely arrival
    overall_rating = db.Column(db.Integer, nullable=True)  # 1-5: Overall satisfaction
    
    # Feedback
    comments = db.Column(db.Text, nullable=True)  # Open feedback comments
    reported_issues = db.Column(db.JSON, nullable=True)  # ["contamination", "damaged_packaging", ...]
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    donation = db.relationship('Donation', backref='feedback', lazy=True)
    reviewer = db.relationship('User', backref='donation_feedback', lazy=True)

    def __init__(self, donation_id, reviewer_id, food_quality_rating=None,
                 timeliness_rating=None, overall_rating=None, comments=None,
                 reported_issues=None):
        """
        Constructor for DonationFeedback.
        
        Args:
            donation_id (str): ID of donation being reviewed
            reviewer_id (int): User ID of reviewer
            food_quality_rating (int): 1-5 rating
            timeliness_rating (int): 1-5 rating
            overall_rating (int): 1-5 rating
            comments (str): Feedback text
            reported_issues (list): Issues like ["contamination", "wrong_quantity", ...]
        """
        self.donation_id = donation_id
        self.reviewer_id = reviewer_id
        self.food_quality_rating = food_quality_rating
        self.timeliness_rating = timeliness_rating
        self.overall_rating = overall_rating
        self.comments = comments
        self.reported_issues = reported_issues or []

    def create(self):
        """
        Add feedback to database.
        
        Returns:
            DonationFeedback: Created feedback or None on error
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
        Convert feedback to dictionary.
        
        Returns:
            dict: Feedback data
        """
        return {
            'id': self.id,
            'donation_id': self.donation_id,
            'reviewer_id': self.reviewer_id,
            'reviewer_name': self.reviewer.name if self.reviewer else None,
            'ratings': {
                'food_quality': self.food_quality_rating,
                'timeliness': self.timeliness_rating,
                'overall': self.overall_rating
            },
            'comments': self.comments,
            'reported_issues': self.reported_issues,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def update(self, data):
        """
        Update feedback with new data.
        
        Args:
            data (dict): Fields to update
        
        Returns:
            DonationFeedback: Updated feedback or None on error
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
        Delete feedback from database.
        
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

    def validate_ratings(self):
        """
        Validate that all ratings are in valid range (1-5).
        
        Returns:
            tuple: (is_valid, error_message)
        """
        for rating_value in [self.food_quality_rating, self.timeliness_rating, self.overall_rating]:
            if rating_value is not None and (rating_value < 1 or rating_value > 5):
                return False, f"Ratings must be between 1 and 5, got {rating_value}"
        return True, ""

    def get_rating_summary(self):
        """
        Get average rating across all categories.
        
        Returns:
            float: Average of all ratings, or None if no ratings
        """
        ratings = [r for r in [self.food_quality_rating, self.timeliness_rating, 
                              self.overall_rating] if r is not None]
        if not ratings:
            return None
        return sum(ratings) / len(ratings)

    def has_issues(self):
        """
        Check if feedback reports any issues.
        
        Returns:
            bool: True if issues reported
        """
        return bool(self.reported_issues)

    def __repr__(self):
        return f"DonationFeedback(donation_id={self.donation_id}, overall_rating={self.overall_rating})"


def initDonationFeedback():
    """
    Initialize donation feedback table.
    """
    with app.app_context():
        db.create_all()
