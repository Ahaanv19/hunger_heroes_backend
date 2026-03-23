# Admin Panel API Documentation

## Overview

The Admin Panel API provides comprehensive tools for platform administrators to manage donations, organizations, flags/issues, and users. All endpoints are protected by admin-only middleware that requires a valid JWT token and Admin role.

**Base URL**: `/api/admin`

**Authentication**: Required - JWT token via cookies + Admin role

---

## Authentication & Authorization

### Admin Middleware

All admin endpoints are protected by the `@admin_required` decorator from `api/admin_middleware.py`.

**Requirements**:
- Valid JWT token in cookies (name configurable via `JWT_TOKEN_NAME`)
- User must have `_role == 'Admin'`
- Token must not be expired

**Response Codes**:
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - User lacks Admin role
- `200 OK` - Request successful

---

## Response Format

All endpoints return responses in this standardized format:

```json
{
  "success": true/false,
  "message": "Human-readable message",
  "data": { /* ... */ },
  "status": 200
}
```

---

## Endpoints

### 📊 DONATIONS

#### GET /api/admin/donations
List all donations with admin filters

**Query Parameters**:
- `status` (optional): Filter by status - one of: `posted`, `claimed`, `in_transit`, `delivered`, `confirmed`, `expired`, `cancelled`
- `safety_score` (optional): Filter by safety level
  - `requires_review` - Donations flagged for review (safety_score < specified threshold)
  - `low_score` - Safety score < 70
  - `high_score` - Safety score >= 80
- `flagged` (optional): Filter by flags - `true` or `false`
- `page` (optional): Page number, default: 1
- `per_page` (optional): Items per page, default: 20

**Example Request**:
```bash
curl -X GET "http://localhost:5000/api/admin/donations?status=posted&safety_score=low_score&page=1&per_page=10" \
  -H "Cookie: jwt_python_flask=<token>" \
  -H "Content-Type: application/json"
```

**Example Response**:
```json
{
  "success": true,
  "message": "Donations retrieved successfully",
  "data": {
    "donations": [
      {
        "id": "HH-M3X7K9-AB2F",
        "food_name": "Fresh Apples",
        "category": "fresh-produce",
        "quantity": 50,
        "unit": "lbs",
        "status": "posted",
        "safety_score": 65,
        "requires_review": true,
        "donor_name": "John Doe",
        "donor_email": "john@example.com",
        "expiry_date": "2026-03-30",
        "created_at": "2026-03-23T10:30:00",
        "is_flagged": true,
        "flag_count": 1
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 45,
      "pages": 5
    }
  },
  "status": 200
}
```

---

#### PATCH /api/admin/donations/{id}
Admin override for donation status (update status, safety score, review flag)

**Request Body**:
```json
{
  "status": "confirmed",
  "safety_score": 85,
  "requires_review": false,
  "admin_notes": "Safety check passed. Approved for distribution."
}
```

**Parameters**:
- `status` (optional): New status for donation
- `safety_score` (optional): Updated safety score (0-100)
- `requires_review` (optional): Whether donation requires review (boolean)

**Example Request**:
```bash
curl -X PATCH "http://localhost:5000/api/admin/donations/HH-M3X7K9-AB2F" \
  -H "Cookie: jwt_python_flask=<token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "confirmed",
    "safety_score": 90,
    "requires_review": false
  }'
```

**Example Response**:
```json
{
  "success": true,
  "message": "Donation updated successfully",
  "data": {
    "id": "HH-M3X7K9-AB2F",
    "food_name": "Fresh Apples",
    "status": "confirmed",
    "safety_score": 90,
    "requires_review": false,
    /* ... full donation details ... */
  },
  "status": 200
}
```

---

### 🏢 ORGANIZATIONS

#### GET /api/admin/organizations
List all registered organizations with verification status

**Query Parameters**:
- `verified` (optional): Filter by verification status - `true` or `false`
- `type` (optional): Filter by organization type - one of: `shelter`, `food_bank`, `restaurant`, `temple`, `community_org`
- `page` (optional): Page number, default: 1
- `per_page` (optional): Items per page, default: 20

**Example Request**:
```bash
curl -X GET "http://localhost:5000/api/admin/organizations?verified=false&type=shelter" \
  -H "Cookie: jwt_python_flask=<token>" \
  -H "Content-Type: application/json"
```

**Example Response**:
```json
{
  "success": true,
  "message": "Organizations retrieved successfully",
  "data": {
    "organizations": [
      {
        "id": 1,
        "name": "Community Food Bank",
        "type": "food_bank",
        "address": "123 Main St, City, State 12345",
        "zip_code": "12345",
        "is_verified": false,
        "verification_date": null,
        "verified_by": null,
        "capacity": 500,
        "refrigeration_available": true,
        "phone": "555-1234",
        "email": "info@foodbank.org",
        "member_count": 15,
        "is_active": true,
        "created_at": "2026-01-15T12:00:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 8,
      "pages": 1
    }
  },
  "status": 200
}
```

---

#### PATCH /api/admin/organizations/{id}/verify
Verify or unverify an organization

**Request Body**:
```json
{
  "is_verified": true,
  "verification_notes": "Verified address and tax-exempt status."
}
```

**Parameters**:
- `is_verified` (required): Verification status (boolean)
- `verification_notes` (optional): Notes about verification

**Example Request**:
```bash
curl -X PATCH "http://localhost:5000/api/admin/organizations/1/verify" \
  -H "Cookie: jwt_python_flask=<token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_verified": true
  }'
```

**Example Response**:
```json
{
  "success": true,
  "message": "Organization verified successfully",
  "data": {
    "id": 1,
    "name": "Community Food Bank",
    "is_verified": true,
    "verification_date": "2026-03-23T14:30:00",
    "verified_by": "admin_uid_123",
    /* ... rest of organization data ... */
  },
  "status": 200
}
```

---

### 🚩 FLAGS/ISSUES

#### GET /api/admin/flags
List all flagged donations and reported issues

**Query Parameters**:
- `status` (optional): Filter by status - `open`, `in_review`, `resolved`, `dismissed`
- `severity` (optional): Filter by severity - `low`, `medium`, `high`, `critical`
- `type` (optional): Filter by type - `safety_concern`, `donation_issue`, `organization_issue`, `user_violation`
- `page` (optional): Page number, default: 1
- `per_page` (optional): Items per page, default: 20

**Example Request**:
```bash
curl -X GET "http://localhost:5000/api/admin/flags?status=open&severity=critical" \
  -H "Cookie: jwt_python_flask=<token>" \
  -H "Content-Type: application/json"
```

**Example Response**:
```json
{
  "success": true,
  "message": "Flags retrieved successfully",
  "data": {
    "flags": [
      {
        "id": 1,
        "flag_type": "safety_concern",
        "severity": "critical",
        "status": "open",
        "title": "Expired Food Detected",
        "description": "Donation HH-M3X7K9-AB2F contains food past expiration date",
        "donation_id": "HH-M3X7K9-AB2F",
        "donation_food_name": "Fresh Apples",
        "organization_id": null,
        "user_id": null,
        "reporter_id": 5,
        "reporter_name": "Sarah Admin",
        "resolution_notes": null,
        "resolved_by": null,
        "resolver_name": null,
        "resolved_at": null,
        "created_at": "2026-03-23T10:15:00",
        "updated_at": "2026-03-23T10:15:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 3,
      "pages": 1
    },
    "summary": {
      "total_open": 3,
      "total_critical": 1,
      "total_high": 2
    }
  },
  "status": 200
}
```

---

#### PATCH /api/admin/flags/{id}/resolve
Resolve a flagged issue with notes

**Request Body**:
```json
{
  "status": "resolved",
  "resolution_notes": "Donation rejected and removed from system. Donor notified about food safety requirements.",
  "action_taken": "Donation quarantined, vendor education session scheduled"
}
```

**Parameters**:
- `status` (optional): New status - default: `resolved`
- `resolution_notes` (required): Detailed notes about resolution
- `action_taken` (optional): Description of corrective action

**Example Request**:
```bash
curl -X PATCH "http://localhost:5000/api/admin/flags/1/resolve" \
  -H "Cookie: jwt_python_flask=<token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved",
    "resolution_notes": "Donation rejected. Expired food detected and removed from system."
  }'
```

**Example Response**:
```json
{
  "success": true,
  "message": "Flag resolved successfully",
  "data": {
    "id": 1,
    "flag_type": "safety_concern",
    "status": "resolved",
    "severity": "critical",
    "title": "Expired Food Detected",
    "resolution_notes": "Donation rejected. Expired food detected and removed from system.",
    "resolved_by": 2,
    "resolved_at": "2026-03-23T14:45:00",
    /* ... full flag data ... */
  },
  "status": 200
}
```

---

### 👥 USERS

#### GET /api/admin/users
List all users with role, status, and activity metrics

**Query Parameters**:
- `role` (optional): Filter by role - `Admin`, `Donor`, `Receiver`, `Volunteer`, `User`
- `status` (optional): Filter by status - `active`, `inactive`
- `page` (optional): Page number, default: 1
- `per_page` (optional): Items per page, default: 20

**Example Request**:
```bash
curl -X GET "http://localhost:5000/api/admin/users?role=Donor&status=active&page=1" \
  -H "Cookie: jwt_python_flask=<token>" \
  -H "Content-Type: application/json"
```

**Example Response**:
```json
{
  "success": true,
  "message": "Users retrieved successfully",
  "data": {
    "users": [
      {
        "id": 1,
        "name": "John Donor",
        "email": "john@example.com",
        "role": "Donor",
        "status": "active",
        "organization_id": null,
        "created_at": "2026-02-01T08:00:00",
        "last_activity": "2026-03-23T16:30:00",
        "activity_metrics": {
          "donations_created": 12,
          "donations_received": 0,
          "account_age_days": 50
        }
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 125,
      "pages": 7
    },
    "summary": {
      "total_users": 125,
      "active_users": 110,
      "admin_count": 3,
      "donor_count": 45,
      "receiver_count": 32,
      "volunteer_count": 20
    }
  },
  "status": 200
}
```

---

#### GET /api/admin/users/{id}
Get detailed user information for admin review

**Example Request**:
```bash
curl -X GET "http://localhost:5000/api/admin/users/1" \
  -H "Cookie: jwt_python_flask=<token>" \
  -H "Content-Type: application/json"
```

**Example Response**:
```json
{
  "success": true,
  "message": "User details retrieved successfully",
  "data": {
    "id": 1,
    "name": "John Donor",
    "email": "john@example.com",
    "role": "Donor",
    "status": "active",
    "activity_metrics": {
      "donations_created": 12,
      "donations_received": 0,
      "account_age_days": 50
    },
    "organization": null,
    "flags_count": 0,
    "recent_flags": []
  },
  "status": 200
}
```

---

#### PATCH /api/admin/users/{id}/suspend
Suspend or activate a user account

**Request Body**:
```json
{
  "is_active": false,
  "reason": "Multiple food safety violations"
}
```

**Parameters**:
- `is_active` (required): Activation status (boolean)
- `reason` (optional): Reason for suspension/activation

**Example Request**:
```bash
curl -X PATCH "http://localhost:5000/api/admin/users/15/suspend" \
  -H "Cookie: jwt_python_flask=<token>" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false,
    "reason": "Repeated food safety violations"
  }'
```

**Example Response**:
```json
{
  "success": true,
  "message": "User suspended successfully",
  "data": {
    "id": 15,
    "name": "Problem User",
    "email": "problem@example.com",
    "role": "Donor",
    "status": "inactive",
    /* ... full user data ... */
  },
  "status": 200
}
```

---

### 📈 DASHBOARD/Statistics

#### GET /api/admin/stats
Get admin dashboard statistics and platform metrics

**Example Request**:
```bash
curl -X GET "http://localhost:5000/api/admin/stats" \
  -H "Cookie: jwt_python_flask=<token>" \
  -H "Content-Type: application/json"
```

**Example Response**:
```json
{
  "success": true,
  "message": "Admin statistics retrieved successfully",
  "data": {
    "users": {
      "total": 125,
      "active": 110,
      "inactive": 15
    },
    "donations": {
      "total": 342,
      "pending": 23,
      "flagged": 4,
      "low_safety": 2
    },
    "organizations": {
      "total": 8,
      "verified": 7,
      "unverified": 1
    },
    "flags": {
      "open": 3,
      "critical": 1,
      "resolved": 45,
      "total": 49
    }
  },
  "status": 200
}
```

---

## Data Models

### Flag Model
```python
class Flag(db.Model):
    id: int (primary key)
    flag_type: str (safety_concern, donation_issue, organization_issue, user_violation)
    severity: str (low, medium, high, critical)
    status: str (open, in_review, resolved, dismissed)
    title: str
    description: text
    donation_id: str (FK, optional)
    organization_id: int (FK, optional)
    user_id: int (FK, optional)
    reporter_id: int (FK, optional)
    resolution_notes: text
    resolved_by: int (FK, optional)
    resolved_at: datetime
    created_at: datetime
    updated_at: datetime
```

---

## Error Responses

### Common Error Codes

**400 Bad Request**:
```json
{
  "success": false,
  "message": "Invalid request parameters",
  "error": "Missing required field: status",
  "status": 400
}
```

**401 Unauthorized**:
```json
{
  "success": false,
  "message": "Authentication token is missing",
  "error": "Unauthorized",
  "status": 401
}
```

**403 Forbidden**:
```json
{
  "success": false,
  "message": "Admin access required",
  "error": "Forbidden",
  "status": 403
}
```

**404 Not Found**:
```json
{
  "success": false,
  "message": "Donation not found",
  "status": 404
}
```

**500 Internal Server Error**:
```json
{
  "success": false,
  "message": "Error updating donation",
  "error": "Database connection failed",
  "status": 500
}
```

---

## Setup & Installation

### 1. Database Migration
Create the Flag table using Flask-Migrate:

```bash
# Generate migration
flask db migrate -m "Add Flag model for admin panel"

# Apply migration
flask db upgrade
```

### 2. Import Files
The following files have been added:
- `model/flag.py` - Flag/Issue database model
- `api/admin_middleware.py` - Admin authentication middleware
- `api/admin.py` - Admin API endpoints blueprint
- `main.py` - Updated to import and register admin blueprint

### 3. Verify Installation
Check that the admin API is accessible:

```bash
# Should return 401 (no token) or 403 (not admin)
curl http://localhost:5000/api/admin/donations
```

---

## Usage Examples

### Example: Flag a Donation for Safety Review

Create a new flag programmatically from another endpoint:

```python
from model.flag import Flag
from __init__ import db

# Create flag
flag = Flag(
    flag_type='safety_concern',
    severity='high',
    title='Low Safety Score',
    description='Donation has safety score of 65, requires review',
    donation_id='HH-M3X7K9-AB2F',
    reporter_id=5
)
flag.create()
```

### Example: List Critical Issues

```bash
curl -X GET "http://localhost:5000/api/admin/flags?status=open&severity=critical" \
  -H "Cookie: jwt_python_flask=YOUR_ADMIN_TOKEN"
```

---

## File Locations

- **Model**: `/model/flag.py`
- **Middleware**: `/api/admin_middleware.py`
- **Blueprint**: `/api/admin.py`
- **Documentation**: `/docs/ADMIN_PANEL_API.md`

---

## Testing

### Test Admin Authentication

```bash
# Get valid admin token first (from login endpoint)
ADMIN_TOKEN=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin_password"}' \
  | jq -r '.data.token')

# Test admin endpoint
curl -X GET "http://localhost:5000/api/admin/stats" \
  -H "Cookie: jwt_python_flask=$ADMIN_TOKEN"
```

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Pagination defaults to 20 items per page
- Admin actions are logged via the `updated_at` timestamp
- Donations can have multiple flags
- Flags can reference donations, organizations, or users
- All admin operations require both token validity and Admin role

---

## Future Enhancements

- Audit logging for all admin actions
- Bulk operations (flag multiple donations, ban multiple users)
- Export reports functionality
- Advanced analytics by time period
- Automated flagging rules based on safety scores
- Notification system for critical flags
