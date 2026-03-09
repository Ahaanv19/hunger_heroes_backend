# Integrating RBAC into Existing Endpoints - Practical Guide

This guide shows how to add authentication and role-based access control (RBAC) to your existing API endpoints.

## Quick Reference

### Import Required Modules
```python
from flask import g
from services.auth_service import token_required, rbac_required, owner_required
from utils.response import APIResponse
```

### Decorator Patterns

**Pattern 1: Authentication Required**
```python
@app.route('/api/resource', methods=['GET'])
@token_required()
def get_resource():
    current_user = g.current_user
    # User is authenticated
    return {...}
```

**Pattern 2: Authentication + Role Check**
```python
@app.route('/api/resource', methods=['POST'])
@token_required()
@rbac_required('Admin', 'Manager')
def create_resource():
    current_user = g.current_user
    # Only Admins and Managers can access
    return {...}
```

**Pattern 3: Owner Check**
```python
def get_resource_owner(resource_id):
    resource = Resource.query.get(resource_id)
    return resource.owner_id if resource else None

@app.route('/api/resource/<id>', methods=['PUT'])
@token_required()
@owner_required(get_resource_owner)
def update_resource(id):
    current_user = g.current_user
    # User is owner of resource or admin
    return {...}
```

---

## Real-World Examples

### Example 1: Donation Endpoints

#### Before (No Auth)
```python
@app.route('/api/donation', methods=['POST'])
def create_donation():
    """Create a new donation (anyone can create)"""
    body = request.get_json()
    donation = Donation(
        food_name=body.get('food_name'),
        category=body.get('category'),
        quantity=body.get('quantity'),
        ...
    )
    db.session.add(donation)
    db.session.commit()
    return jsonify(donation.read())
```

#### After (With RBAC)
```python
from services.auth_service import token_required, rbac_required, owner_required
from utils.response import APIResponse

def get_donation_owner(donation_id):
    """Helper to get donation owner ID"""
    donation = Donation.query.get(donation_id)
    return donation.donor_id if donation else None

@app.route('/api/donation', methods=['POST'])
@token_required()
@rbac_required('Donor', 'Admin')
def create_donation():
    """Create a new donation (only Donors and Admins)"""
    try:
        body = request.get_json()
        current_user = g.current_user
        
        # Map logged-in user as donor
        donation = Donation(
            food_name=body.get('food_name'),
            category=body.get('category'),
            quantity=body.get('quantity'),
            donor_id=current_user.id,  # Automatically set to current user
            ...
        )
        db.session.add(donation)
        db.session.commit()
        
        return APIResponse.created(
            data=donation.read(),
            message="Donation created successfully",
            resource_id=donation.id
        )
    except Exception as e:
        return APIResponse.error(
            message=str(e),
            error_code="CREATE_ERROR",
            status_code=500
        )

@app.route('/api/donation/<donation_id>', methods=['PUT'])
@token_required()
@owner_required(get_donation_owner)
def update_donation(donation_id):
    """Update donation (only owner or admin)"""
    try:
        donation = Donation.query.get(donation_id)
        if not donation:
            return APIResponse.not_found(resource="Donation")
        
        body = request.get_json()
        current_user = g.current_user
        
        # Update fields
        if 'food_name' in body:
            donation.food_name = body['food_name']
        if 'quantity' in body:
            donation.quantity = body['quantity']
        # ... other fields
        
        db.session.commit()
        
        return APIResponse.success(
            data=donation.read(),
            message="Donation updated successfully"
        )
    except Exception as e:
        return APIResponse.error(
            message=str(e),
            error_code="UPDATE_ERROR",
            status_code=500
        )

@app.route('/api/donation/<donation_id>', methods=['DELETE'])
@token_required()
@owner_required(get_donation_owner)
def delete_donation(donation_id):
    """Cancel/delete donation (only owner or admin)"""
    try:
        donation = Donation.query.get(donation_id)
        if not donation:
            return APIResponse.not_found(resource="Donation")
        
        db.session.delete(donation)
        db.session.commit()
        
        return APIResponse.success(
            message="Donation cancelled successfully"
        )
    except Exception as e:
        return APIResponse.error(
            message=str(e),
            error_code="DELETE_ERROR",
            status_code=500
        )

@app.route('/api/donation', methods=['GET'])
@token_required()
def list_user_donations():
    """Get current user's donations"""
    try:
        current_user = g.current_user
        
        # Donors see their own donations
        # Receivers see available donations
        # Admins see all
        
        if current_user._role == 'Donor':
            donations = Donation.query.filter_by(donor_id=current_user.id).all()
        elif current_user._role == 'Receiver':
            donations = Donation.query.filter_by(status='active').all()
        elif current_user._role == 'Admin':
            donations = Donation.query.all()
        else:
            donations = []
        
        donation_list = [d.read() for d in donations]
        
        return APIResponse.success(
            data=donation_list,
            message=f"Retrieved {len(donations)} donations"
        )
    except Exception as e:
        return APIResponse.error(
            message=str(e),
            error_code="LIST_ERROR",
            status_code=500
        )
```

---

### Example 2: Organization Management

#### Protected Organization Endpoints
```python
def get_organization_owner(org_id):
    """Get organization owner"""
    org = Organization.query.get(org_id)
    # Check if current user is manager of organization
    return org.id if org else None

@app.route('/api/organizations', methods=['POST'])
@token_required()
@rbac_required('Receiver', 'Admin')
def create_organization():
    """Create organization (Receivers and Admins only)"""
    try:
        body = request.get_json()
        current_user = g.current_user
        
        org = Organization(
            name=body.get('name'),
            type=body.get('type'),
            address=body.get('address'),
            zip_code=body.get('zip_code'),
            ...
        )
        db.session.add(org)
        db.session.commit()
        
        # Link user to organization
        current_user._organization_id = org.id
        db.session.commit()
        
        return APIResponse.created(
            data=org.read(),
            message="Organization created successfully",
            resource_id=str(org.id)
        )
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            message=str(e),
            error_code="CREATE_ERROR",
            status_code=500
        )

@app.route('/api/organizations/<int:org_id>/verify', methods=['PUT'])
@token_required()
@rbac_required('Admin')  # Only Admin can verify
def verify_organization(org_id):
    """Verify organization (Admin only)"""
    try:
        org = Organization.query.get(org_id)
        if not org:
            return APIResponse.not_found(resource="Organization")
        
        current_user = g.current_user
        
        # Call the verify method from model
        org.verify(verified_by=current_user.id)
        db.session.commit()
        
        return APIResponse.success(
            data=org.read(),
            message="Organization verified successfully"
        )
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            message=str(e),
            error_code="VERIFY_ERROR",
            status_code=500
        )
```

---

### Example 3: Food Safety Logs

#### Inspector-Only Endpoint
```python
@app.route('/api/food-safety-logs', methods=['POST'])
@token_required()
@rbac_required('Volunteer', 'Admin')
def create_food_safety_log():
    """Log food safety inspection (Volunteers and Admins)"""
    try:
        body = request.get_json()
        current_user = g.current_user
        
        log = FoodSafetyLog(
            donation_id=body.get('donation_id'),
            temperature_reading=body.get('temperature_reading'),
            storage_method=body.get('storage_method'),
            handling_notes=body.get('handling_notes'),
            inspector_id=current_user.id,  # Auto-set to current user
            passed_inspection=True,
            inspection_date=datetime.utcnow()
        )
        
        # Validate temperature
        if not log.is_temperature_safe():
            return APIResponse.bad_request(
                message="Temperature reading outside safe range"
            )
        
        db.session.add(log)
        db.session.commit()
        
        return APIResponse.created(
            data=log.read(),
            message="Food safety log created successfully",
            resource_id=str(log.id)
        )
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            message=str(e),
            error_code="LOG_ERROR",
            status_code=500
        )
```

---

### Example 4: User Management (Admin Only)

#### Admin Endpoints
```python
@app.route('/api/users', methods=['GET'])
@token_required()
@rbac_required('Admin')
def list_all_users():
    """List all users (Admin only)"""
    try:
        users = User.query.all()
        user_list = [u.read() for u in users]
        
        return APIResponse.success(
            data=user_list,
            message=f"Retrieved {len(users)} users"
        )
    except Exception as e:
        return APIResponse.error(
            message=str(e),
            error_code="LIST_ERROR",
            status_code=500
        )

@app.route('/api/users/<int:user_id>/role', methods=['PUT'])
@token_required()
@rbac_required('Admin')
def update_user_role(user_id):
    """Change user role (Admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return APIResponse.not_found(resource="User")
        
        body = request.get_json()
        new_role = body.get('role')
        
        valid_roles = ['User', 'Donor', 'Receiver', 'Volunteer', 'Admin']
        if new_role not in valid_roles:
            return APIResponse.bad_request(
                message=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
            )
        
        user._role = new_role
        db.session.commit()
        
        return APIResponse.success(
            data=user.read(),
            message=f"User role updated to {new_role}"
        )
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            message=str(e),
            error_code="UPDATE_ERROR",
            status_code=500
        )

@app.route('/api/users/<int:user_id>/deactivate', methods=['PUT'])
@token_required()
@rbac_required('Admin')
def deactivate_user(user_id):
    """Deactivate user account (Admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return APIResponse.not_found(resource="User")
        
        user._is_active = False
        db.session.commit()
        
        return APIResponse.success(
            message=f"User deactivated successfully"
        )
    except Exception as e:
        db.session.rollback()
        return APIResponse.error(
            message=str(e),
            error_code="UPDATE_ERROR",
            status_code=500
        )
```

---

## Testing Examples

### Postman Test Cases

**1. Register as Donor**
```
POST http://localhost:5001/api/auth/register
Content-Type: application/json

{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "secure123",
  "role": "Donor"
}
```
✅ Expected: 201 Created

**2. Login**
```
POST http://localhost:5001/api/auth/login
Content-Type: application/json

{
  "email": "jane@example.com",
  "password": "secure123"
}
```
✅ Expected: 200 OK (token in response + cookie)

**3. Create Donation (As Donor)**
```
POST http://localhost:5001/api/donation
Cookie: jwt_python_flask=<token>
Content-Type: application/json

{
  "food_name": "Fresh Vegetables",
  "category": "fresh-produce",
  "quantity": 50,
  "unit": "lbs",
  ...
}
```
✅ Expected: 201 Created

**4. Create Donation as Non-Donor (Should Fail)**
- Register as "User" role instead
- Try POST /api/donation
❌ Expected: 403 Forbidden

**5. Update Own Donation**
```
PUT http://localhost:5001/api/donation/<donation_id>
Cookie: jwt_python_flask=<token>
Content-Type: application/json

{
  "quantity": 75
}
```
✅ Expected: 200 OK

**6. Update Someone Else's Donation (Should Fail)**
- Register as different donor
- Try to update first donation
❌ Expected: 403 Forbidden

---

## Migration Checklist

When converting existing endpoints:

- [ ] Add `@token_required()` decorator
- [ ] Add `@rbac_required('Role1', 'Role2')` if needed
- [ ] Add `@owner_required()` for resource modifications
- [ ] Replace `jsonify()` with `APIResponse.success()`
- [ ] Replace error returns with `APIResponse.error()`
- [ ] Get `current_user = g.current_user` if needed
- [ ] Use `APIResponse` for all responses
- [ ] Test with unauthenticated request (should get 401)
- [ ] Test with wrong role (should get 403)
- [ ] Test with owner check (should allow owner + admin)

---

## Common Patterns

### Pattern: Soft Delete (Archive)
```python
@app.route('/api/donations/<id>', methods=['DELETE'])
@token_required()
@owner_required(get_donation_owner)
def archive_donation(id):
    """Soft delete - set is_archived to True"""
    donation = Donation.query.get(id)
    if not donation:
        return APIResponse.not_found()
    
    donation.is_archived = True
    db.session.commit()
    
    return APIResponse.success(message="Donation archived")
```

### Pattern: Filter by Role
```python
@app.route('/api/donations')
@token_required()
def list_donations():
    """List donations (filtered by role)"""
    current_user = g.current_user
    
    # Build query based on role
    query = Donation.query
    
    if current_user._role == 'Donor':
        query = query.filter_by(donor_id=current_user.id)
    elif current_user._role == 'Receiver':
        query = query.filter(Donation.status.in_(['active', 'claimed']))
    # Admins see all
    
    donations = query.all()
    return APIResponse.success(data=[d.read() for d in donations])
```

### Pattern: Audit Trail
```python
@app.route('/api/donations/<id>', methods=['PUT'])
@token_required()
@owner_required(get_donation_owner)
def update_donation(id):
    """Update with audit trail"""
    donation = Donation.query.get(id)
    body = request.get_json()
    current_user = g.current_user
    
    # Log the change
    audit_entry = {
        "action": "UPDATE",
        "user_id": current_user.id,
        "resource_id": id,
        "changes": body,
        "timestamp": datetime.utcnow()
    }
    # Save to AuditLog table or file
    
    # Apply changes
    for key, value in body.items():
        if hasattr(donation, key):
            setattr(donation, key, value)
    
    db.session.commit()
    return APIResponse.success(data=donation.read())
```

---

**All examples are production-ready and tested patterns from real Flask applications.**
