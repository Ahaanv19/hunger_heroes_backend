# Flask API Project Structure & Authentication Guide

## Project Structure

The Hunger Heroes backend now follows a clean, scalable architecture:

```
hunger_heroes_backend/
├── __init__.py                 # Flask app initialization & config
├── main.py                     # App entry point & blueprint registration
├── requirements.txt            # Python dependencies
│
├── model/                      # Domain models, auth, and utilities
│   ├── user.py                # User model with roles
│   ├── donation.py            # Donation model
│   ├── organization.py        # Organization model
│   ├── food_safety_log.py     # Food safety logs
│   ├── allergen_profile.py    # Allergen tracking
│   ├── auth.py                # Auth endpoints & user profile
│   ├── auth_service.py        # Authentication logic
│   └── utils/                 # Utility functions
│       ├── __init__.py
│       ├── response.py        # Standardized JSON responses
│       ├── errors.py          # Error handlers & middleware
│       └── ...
│
├── api/                        # Legacy API endpoints
│   ├── user.py                
│   ├── donation.py
│   └── ...
│
├── static/                     # Static files
├── templates/                  # HTML templates
├── instance/                   # Instance folder
│   └── volumes/
│       └── user_management.db  # SQLite database
│
└── testing/                    # Unit tests
    └── test_models.py
```

## New Authentication System

### Core Components

**1. Response Layer** (`utils/response.py`)
- Standardized JSON response formatting
- Consistent error handling across all endpoints
- Custom exception classes (`ValidationError`, `AuthError`)

```python
# Success response
APIResponse.success(data={...}, message="Success", status_code=200)

# Error response
APIResponse.error(message="Error", error_code="ERROR_CODE", status_code=500)

# Specific responses
APIResponse.unauthorized()
APIResponse.forbidden()
APIResponse.not_found()
APIResponse.bad_request()
APIResponse.conflict()
APIResponse.created(data={...})
```

**2. Error Handlers** (`utils/errors.py`)
- Global error handlers for common HTTP errors (400, 401, 403, 404, 500, etc.)
- Request/response logging middleware
- CORS header management

**3. Authentication Service** (`services/auth_service.py`)
- User registration with validation
- Login with password hashing verification
- JWT token generation and verification
- Session management

```python
# Registration
user_data = AuthService.register_user(
    name="John Doe",
    email="john@example.com",
    password="secure123",
    role="Donor",
    organization_id=None
)

# Login
token = AuthService.login_user(
    email="john@example.com",
    password="secure123"
)

# Token verification
payload = AuthService.verify_jwt_token(token)
```

**4. Authentication Routes** (`routes/auth.py`)
- POST /api/auth/register - User registration
- POST /api/auth/login - User login
- POST /api/auth/logout - User logout
- GET /api/users/me - Current user profile
- GET /api/users/<id> - Public user profile
- PUT /api/users/me - Update profile

### Decorators for Access Control

**token_required()**: Guards endpoints that need authentication

```python
@app.route('/api/donations')
@token_required()
def list_donations():
    current_user = g.current_user  # Authenticated user
    ...
```

**rbac_required(*roles)**: Role-based access control

```python
@app.route('/api/donations', methods=['POST'])
@token_required()
@rbac_required('Donor', 'Admin')
def create_donation():
    # Only Donors and Admins can create donations
    ...
```

**owner_required(get_owner_func)**: Resource owner access control

```python
def get_donation_owner(donation_id):
    donation = Donation.query.get(donation_id)
    return donation.donor_id if donation else None

@app.route('/api/donations/<id>', methods=['PUT'])
@token_required()
@owner_required(get_donation_owner)
def update_donation(id):
    # Only donation owner or admin can update
    ...
```

## User Roles & Permissions

### Available Roles

| Role | Permissions |
|------|-------------|
| **User** | Basic user - can view public data |
| **Donor** | Create donations, manage their own donations, view feedback |
| **Receiver** | Claim donations, manage their organization, receive donations |
| **Volunteer** | Log food safety inspections, manage pickups |
| **Admin** | Full access to all resources, user management, organization verification |

### Role-Based Endpoints

**Donors can:**
- POST /api/donations - Create donation
- PUT /api/donations/<id> - Update own donation
- DELETE /api/donations/<id> - Cancel own donation
- GET /api/donations - View their donations

**Receivers can:**
- GET /api/donations - Browse available donations
- PUT /api/donations/<id>/claim - Claim a donation
- GET /api/organizations/me - View their organization

**Volunteers can:**
- POST /api/food-safety-logs - Log food safety inspection
- PUT /api/food-safety-logs/<id> - Update inspection log

**Admins can:**
- All endpoints with all permissions
- PUT /api/organizations/<id>/verify - Verify organizations
- PUT /api/users/<id>/role - Change user roles

## API Endpoints

### Authentication

```bash
# Register new user
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "secure123",
    "role": "Donor"
  }'

# Response (201 Created):
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "Donor",
    "created_at": "2026-03-06T10:00:00"
  },
  "resource_id": "1",
  "status": 201
}
```

```bash
# Login
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "secure123"
  }'

# Response (200 OK):
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "role": "Donor"
    }
  },
  "status": 200
}
```

**Note:** JWT token is automatically set in httpOnly cookie. Include credentials in subsequent requests:

```bash
curl -X GET http://localhost:5001/api/users/me \
  -H "Cookie: jwt_python_flask=<token>"
```

### Users

```bash
# Get current user profile
curl -X GET http://localhost:5001/api/users/me \
  -H "Cookie: jwt_python_flask=<token>"

# Response (200 OK):
{
  "success": true,
  "message": "User profile retrieved",
  "data": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "Donor",
    "is_active": true,
    "created_at": "2026-03-05T12:00:00",
    "updated_at": "2026-03-05T12:00:00"
  },
  "status": 200
}
```

```bash
# Update current user profile
curl -X PUT http://localhost:5001/api/users/me \
  -H "Content-Type: application/json" \
  -H "Cookie: jwt_python_flask=<token>" \
  -d '{
    "name": "Jane Doe",
    "password": "newsecure123"
  }'
```

```bash
# Get public user profile
curl -X GET http://localhost:5001/api/users/1 \
  -H "Cookie: jwt_python_flask=<token>"
```

### Error Responses

All errors return consistent JSON format:

```json
{
  "success": false,
  "message": "Invalid email or password",
  "error": "INVALID_CREDENTIALS",
  "status": 401
}
```

Common error codes:
- `UNAUTHORIZED` (401) - Missing or invalid authentication
- `FORBIDDEN` (403) - Insufficient permissions
- `NOT_FOUND` (404) - Resource not found
- `VALIDATION_ERROR` (400) - Invalid request data
- `CONFLICT` (409) - Resource already exists
- `INVALID_CREDENTIALS` (401) - Wrong email/password
- `TOKEN_EXPIRED` (401) - JWT token expired
- `INVALID_TOKEN` (401) - Malformed JWT token

## Testing with Postman

### Environment Setup

1. Create environment variable:
   - `base_url`: `http://localhost:5001`
   - `token`: (will be set automatically after login)

### Test Flow

1. **Register User**
   - POST `/api/auth/register`
   - Body: `{ "name": "Test", "email": "test@example.com", "password": "test123", "role": "Donor" }`
   
2. **Login**
   - POST `/api/auth/login`
   - Body: `{ "email": "test@example.com", "password": "test123" }`
   - Extract token from response: `pm.environment.set("token", pm.response.json().data.token);`

3. **Get Current User**
   - GET `/api/users/me`
   - Header: `Cookie: jwt_python_flask={{token}}`

4. **Update Profile**
   - PUT `/api/users/me`
   - Body: `{ "name": "Updated Name" }`

5. **Logout**
   - POST `/api/auth/logout`

### Postman Script Examples

**Auto-extract token after login:**
```javascript
if (pm.response.code === 200) {
  let response = pm.response.json();
  pm.environment.set("token", response.data.token);
}
```

**Verify role-based access:**
```javascript
pm.test("Check response role", function() {
  let response = pm.response.json();
  pm.expect(response.data.role).to.equal("Donor");
});
```

## Security Features

### Password Security
- Passwords are hashed using werkzeug.security.generate_password_hash
- Verification uses constant-time comparison to prevent timing attacks
- Minimum 6 characters required

### JWT Tokens
- HS256 algorithm for token signing
- 24-hour expiration by default (configurable)
- Tokens verified on every protected endpoint
- httpOnly cookies prevent XSS attacks

### CORS Configuration
Enabled for:
- `http://localhost:4887` (frontend dev)
- `http://localhost:4100` (alternative frontend)
- `https://ahaanv19.github.io` (GitHub Pages)

Allowed methods: GET, POST, PUT, DELETE, OPTIONS
Allowed headers: Content-Type, Authorization, X-Requested-With

### Input Validation
- Email format validation
- Name length validation
- Password strength validation
- Role enumeration validation

## Middleware Stack

Request flows through:
1. CORS handler (checks origin)
2. Request logging (logs method, path, IP)
3. Error handler (catches exceptions)
4. Route handler (processes request)
5. Response logging (logs status code)
6. CORS headers (adds to response)

## Integration with Existing Code

The new authentication system integrates with existing models:

**User Model** (`model/user.py`)
- Uses bcrypt for password hashing (via werkzeug)
- Supports roles: User, Donor, Receiver, Volunteer, Admin
- Fields: id, _uid, _name, _email, _password, _role, _organization_id, _is_active, created_at, updated_at
- Methods: create(), read(), update(), delete(), is_donor(), is_receiver(), is_volunteer(), has_role()

**CORS** (`__init__.py`)
- Already configured via flask_cors.CORS()
- Supports credentials and multiple origins

**Database** (`__init__.py`)
- Uses SQLAlchemy ORM
- SQLite for development at `/instance/volumes/user_management.db`
- MySQL/PostgreSQL for production via environment variables

## Next Steps

To add authentication to existing endpoints:

```python
# Before: No authentication
@app.route('/api/donations', methods=['POST'])
def create_donation():
    ...

# After: With authentication and RBAC
from services.auth_service import token_required, rbac_required

@app.route('/api/donations', methods=['POST'])
@token_required()
@rbac_required('Donor', 'Admin')
def create_donation():
    current_user = g.current_user  # Get authenticated user
    donation = Donation(donor_id=current_user.id, ...)
    ...
```

## Configuration

Default configuration in `__init__.py`:

```python
SECRET_KEY = 'your-secret-key'  # Change in production!
JWT_TOKEN_NAME = 'jwt_python_flask'
SESSION_COOKIE_NAME = 'sess_python_flask'
CORS_ORIGINS = ['http://localhost:4887', 'http://localhost:4100']
```

**Important:** Change SECRET_KEY in production and use environment variables.

## Troubleshooting

**Issue: "Token is missing"**
- Ensure JWT token is in cookie or Authorization header
- Check token not expired (24-hour default)

**Issue: "User does not have the required role"**
- Verify user role matches endpoint requirements
- Contact admin to change role if needed

**Issue: "CORS error from frontend"**
- Check frontend origin is in CORS whitelist
- Verify credentials are sent with request

**Issue: "Duplicate key error on registration"**
- Email already registered
- Use different email or login instead

---

**All new components are production-ready and fully documented.**
