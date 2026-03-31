# validators.py
"""
Request validation schema using marshmallow
Validates all POST/PATCH endpoints to ensure data integrity
"""

from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load
from datetime import datetime, timedelta
import re


class BaseDonationSchema(Schema):
    """Base schema for donation validation"""
    
    food_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={'required': 'Food name is required'}
    )
    category = fields.String(
        required=True,
        validate=validate.OneOf([
            'canned', 'fresh-produce', 'dairy', 'bakery', 'meat-protein',
            'grains', 'beverages', 'frozen', 'snacks', 'baby-food',
            'prepared-meals', 'other'
        ]),
        error_messages={'required': 'Category is required'}
    )
    food_type = fields.String(
        validate=validate.OneOf([
            'cooked', 'raw', 'packaged', 'perishable', 'non-perishable',
            'baked', 'frozen-prepared', 'canned-goods', 'beverage', 'other'
        ]),
        allow_none=True
    )
    quantity = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        error_messages={'required': 'Quantity is required and must be > 0'}
    )
    unit = fields.String(
        required=True,
        validate=validate.OneOf([
            'items', 'lbs', 'kg', 'oz', 'cans', 'boxes', 'bags', 'trays', 'servings'
        ]),
        error_messages={'required': 'Unit is required'}
    )
    serving_count = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=1)
    )
    weight_lbs = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0.1)
    )
    description = fields.String(
        validate=validate.Length(max=1000),
        allow_none=True
    )
    expiry_date = fields.Date(
        required=True,
        error_messages={'required': 'Expiry date is required'}
    )
    storage = fields.String(
        required=True,
        validate=validate.OneOf(['room-temp', 'refrigerated', 'frozen', 'cool-dry']),
        error_messages={'required': 'Storage method is required'}
    )
    allergens = fields.List(
        fields.String(validate=validate.OneOf([
            'gluten', 'dairy', 'nuts', 'soy', 'eggs', 'shellfish', 'fish', 'none'
        ])),
        allow_none=True
    )
    dietary_tags = fields.List(
        fields.String(validate=validate.OneOf([
            'vegetarian', 'vegan', 'halal', 'kosher', 'gluten-free', 'organic'
        ])),
        allow_none=True
    )
    donor_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200),
        error_messages={'required': 'Donor name is required'}
    )
    donor_email = fields.Email(
        required=True,
        error_messages={'required': 'Valid donor email is required'}
    )
    donor_phone = fields.String(
        validate=validate.Regexp(r'^[\d\-\+\(\)\s]{10,}$', error='Invalid phone format'),
        allow_none=True
    )
    donor_zip = fields.String(
        required=True,
        validate=validate.Regexp(r'^\d{5}(-\d{4})?$', error='Invalid ZIP code format'),
        error_messages={'required': 'Donor ZIP code is required'}
    )
    special_instructions = fields.String(
        validate=validate.Length(max=1000),
        allow_none=True
    )
    pickup_location = fields.String(
        validate=validate.Length(max=500),
        allow_none=True
    )
    zip_code = fields.String(
        validate=validate.Regexp(r'^\d{5}(-\d{4})?$', error='Invalid ZIP code format'),
        allow_none=True
    )
    pickup_window_start = fields.DateTime(allow_none=True)
    pickup_window_end = fields.DateTime(allow_none=True)
    
    @validates('expiry_date')
    def validate_expiry_date(self, value):
        """Expiry date must be in future"""
        if value <= datetime.utcnow().date():
            raise ValidationError('Expiry date must be in the future')
    
    @validates('quantity')
    def validate_quantity(self, value):
        """Quantity must be reasonable"""
        if value > 100000:
            raise ValidationError('Quantity seems unreasonably large')
    
    @validates('safety_score')
    def validate_safety_score(self, value):
        """Safety score must be 0-100"""
        if value is not None and not (0 <= value <= 100):
            raise ValidationError('Safety score must be between 0 and 100')


class CreateDonationSchema(BaseDonationSchema):
    """Schema for creating donations"""
    safety_score = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0, max=100)
    )
    requires_review = fields.Boolean(allow_none=True)


class UpdateDonationSchema(Schema):
    """Schema for updating donations (partial updates)"""
    status = fields.String(
        validate=validate.OneOf([
            'posted', 'claimed', 'in_transit', 'delivered', 'confirmed',
            'expired', 'cancelled'
        ]),
        allow_none=True
    )
    safety_score = fields.Float(
        validate=validate.Range(min=0, max=100),
        allow_none=True
    )
    requires_review = fields.Boolean(allow_none=True)


class CreateOrganizationSchema(Schema):
    """Schema for creating organizations"""
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255),
        error_messages={'required': 'Organization name is required'}
    )
    type = fields.String(
        required=True,
        validate=validate.OneOf([
            'shelter', 'food_bank', 'restaurant', 'temple', 'community_org'
        ]),
        error_messages={'required': 'Organization type is required'}
    )
    address = fields.String(
        required=True,
        validate=validate.Length(min=5, max=500),
        error_messages={'required': 'Address is required'}
    )
    zip_code = fields.String(
        required=True,
        validate=validate.Regexp(r'^\d{5}(-\d{4})?$', error='Invalid ZIP code format'),
        error_messages={'required': 'Valid ZIP code is required'}
    )
    capacity = fields.Integer(
        allow_none=True,
        validate=validate.Range(min=1)
    )
    phone = fields.String(
        validate=validate.Regexp(r'^[\d\-\+\(\)\s]{10,}$', error='Invalid phone format'),
        allow_none=True
    )
    email = fields.Email(allow_none=True)
    website = fields.URL(allow_none=True)
    refrigeration_available = fields.Boolean(allow_none=True)
    storage_capacity_lbs = fields.Float(
        allow_none=True,
        validate=validate.Range(min=0)
    )


class VerifyOrganizationSchema(Schema):
    """Schema for verifying organizations"""
    is_verified = fields.Boolean(
        required=True,
        error_messages={'required': 'is_verified field is required'}
    )
    verification_notes = fields.String(
        validate=validate.Length(max=1000),
        allow_none=True
    )


class FlagSchema(Schema):
    """Schema for creating flags"""
    flag_type = fields.String(
        required=True,
        validate=validate.OneOf([
            'safety_concern', 'donation_issue', 'organization_issue', 'user_violation'
        ]),
        error_messages={'required': 'Flag type is required'}
    )
    severity = fields.String(
        required=True,
        validate=validate.OneOf(['low', 'medium', 'high', 'critical']),
        error_messages={'required': 'Severity level is required'}
    )
    title = fields.String(
        required=True,
        validate=validate.Length(min=5, max=255),
        error_messages={'required': 'Flag title is required (5-255 chars)'}
    )
    description = fields.String(
        required=True,
        validate=validate.Length(min=10, max=2000),
        error_messages={'required': 'Description is required (10-2000 chars)'}
    )
    donation_id = fields.String(allow_none=True)
    organization_id = fields.Integer(allow_none=True)
    user_id = fields.Integer(allow_none=True)
    reporter_id = fields.Integer(allow_none=True)


class ResolveFlagSchema(Schema):
    """Schema for resolving flags"""
    status = fields.String(
        validate=validate.OneOf(['open', 'in_review', 'resolved', 'dismissed']),
        allow_none=True
    )
    resolution_notes = fields.String(
        required=True,
        validate=validate.Length(min=10, max=2000),
        error_messages={'required': 'Resolution notes required (10-2000 chars)'}
    )


class SuspendUserSchema(Schema):
    """Schema for suspending/activating users"""
    is_active = fields.Boolean(
        required=True,
        error_messages={'required': 'is_active field is required'}
    )
    reason = fields.String(
        validate=validate.Length(max=500),
        allow_none=True
    )


class CreateUserSchema(Schema):
    """Schema for creating users"""
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255),
        error_messages={'required': 'User name is required'}
    )
    email = fields.Email(
        required=True,
        error_messages={'required': 'Valid email is required'}
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=8, max=255),
        error_messages={'required': 'Password must be 8+ characters'}
    )
    role = fields.String(
        validate=validate.OneOf(['Admin', 'Donor', 'Receiver', 'Volunteer', 'User']),
        allow_none=True
    )
    organization_id = fields.Integer(allow_none=True)


def validate_request_data(schema_class, data):
    """
    Validate request data against schema
    
    Args:
        schema_class: Marshmallow schema class
        data: Data to validate
    
    Returns:
        Tuple: (validated_data, errors)
        errors is a dict, empty if no errors
    """
    try:
        schema = schema_class()
        validated = schema.load(data)
        return validated, {}
    except ValidationError as err:
        return None, err.messages
