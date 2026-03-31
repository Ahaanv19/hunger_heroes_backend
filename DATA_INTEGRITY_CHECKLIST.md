# Data Integrity Implementation

## ✅ Completed Features

### 1. Database Constraints ✓
- [x] Unique ID constraints on Donation, Flag, Organization, User
- [x] NOT NULL constraints on required fields
- [x] CHECK constraints (e.g., safety_score 0-100, quantity > 0)
- [x] Foreign key relationships with CASCADE delete
- [x] Documented in `utils/database_constraints.py`
- [x] Validation function to check orphaned records

**File**: `utils/database_constraints.py`
**What it does**: Defines and validates database-level constraints

---

### 2. Request Validation ✓
- [x] Marshmallow schemas for all POST/PATCH operations
- [x] Field-level validation (email, ZIP code, dates, ranges, enums)
- [x] Custom validators for business logic (future expiry dates, quantities)
- [x] Error responses with detailed field-level error messages
- [x] Type coercion (strings to ints, dates, etc.)

**File**: `api/validators.py`
**Schemas**: 
- CreateDonationSchema
- UpdateDonationSchema
- CreateOrganizationSchema
- VerifyOrganizationSchema
- FlagSchema
- ResolveFlagSchema
- SuspendUserSchema

**Usage**:
```python
from api.validators import validate_request_data, UpdateDonationSchema

validated_data, errors = validate_request_data(UpdateDonationSchema, request.get_json())
if errors:
    return {'error': errors}, 400
```

---

### 3. Rate Limiting ✓
- [x] Sliding window algorithm (accurate rate limiting)
- [x] Per-user and per-IP tracking
- [x] Thread-safe implementation (RLock for concurrent requests)
- [x] 3 preset limits:
  - **Default**: 100 requests/min (general endpoints)
  - **Strict**: 10 requests/min (auth endpoints)
  - **Admin**: 200 requests/min (admin endpoints)
- [x] Custom limits support
- [x] Automatic cleanup of old request history
- [x] 429 status code with reset time when exceeded

**File**: `api/rate_limiter.py`

**Applied to endpoints**:
- All GET /api/admin/* endpoints
- All PATCH /api/admin/* endpoints

**Usage**:
```python
from api.rate_limiter import rate_limit, admin_limiter

@app.route('/api/protected')
@rate_limit(limiter=admin_limiter)
def protected_endpoint():
    pass
```

---

### 4. API Logging ✓
- [x] Comprehensive request/response logging
- [x] Unique request ID tracking (for correlating logs)
- [x] Request duration measurement (performance tracking)
- [x] Rotating file handler (10MB max, 10 backups)
- [x] Console + file output
- [x] Admin action audit trail
- [x] Security event logging
- [x] Error logging with context

**File**: `api/api_logger.py`

**Log Location**: `logs/api.log`

**Log Events**:
- REQUEST_START: When request begins processing
- REQUEST_END: When request completes with status code
- ADMIN_ACTION: When admin makes changes (donation status, flag resolution, etc.)
- SECURITY_EVENT: Unauthorized access, self-action attempts, validation errors
- ERROR: Database errors, unexpected exceptions

**Usage**:
```python
from api.api_logger import api_logger

api_logger.log_admin_action('UPDATE_STATUS', 'Donation', donation_id, {
    'old_status': 'posted',
    'new_status': 'confirmed'
})

api_logger.log_security_event('UNAUTHORIZED', {
    'endpoint': '/api/admin/flags',
    'reason': 'Missing JWT token'
})
```

---

## 📋 Integration Status

### Main.py Updates ✓
- [x] Imports for validators, rate_limiter, api_logger, database_constraints
- [x] Logger initialized: `setup_api_logging(app, 'logs/api.log')`
- [x] Rate limit headers middleware: `app.after_request(add_rate_limit_headers)`
- [x] Logs directory auto-created if missing

### Admin.py Endpoint Updates ✓

#### GET Endpoints
- [x] `/api/admin/donations` - @rate_limit decorator
- [x] `/api/admin/organizations` - @rate_limit decorator
- [x] `/api/admin/flags` - @rate_limit decorator
- [x] `/api/admin/users` - @rate_limit decorator
- [x] `/api/admin/users/{id}` - @rate_limit decorator
- [x] `/api/admin/stats` - @rate_limit decorator

#### PATCH Endpoints (Enhanced)
- [x] `/api/admin/donations/{id}` - validation + logging + rate limit
- [x] `/api/admin/organizations/{id}/verify` - validation + logging + rate limit
- [x] `/api/admin/flags/{id}/resolve` - validation + logging + rate limit
- [x] `/api/admin/users/{id}/suspend` - validation + security check + logging + rate limit

**Validation Pattern in PATCH endpoints**:
```python
validated_data, errors = validate_request_data(UpdateDonationSchema, data)
if errors:
    api_logger.log_security_event('VALIDATION_ERROR', {'errors': errors})
    return {'error': errors}, 400

# Log the admin action
api_logger.log_admin_action('UPDATE_STATUS', 'Donation', id, {
    'old_status': old_value,
    'new_status': new_value
})

# Process request...
```

---

## 🚀 How to Test

### 1. Verify Installation
```bash
cd /home/anonymous-dyce/hunger_heroes/hunger_heroes_backend
python scripts/verify_data_integrity.py
```

### 2. Test Validation
```bash
# Test invalid data (should reject)
curl -X PATCH "http://localhost:5000/api/admin/donations/HH-001" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "invalid_status",
    "safety_score": 150
  }'

# Expected: 400 with validation errors
```

### 3. Test Rate Limiting
```bash
# Make 101 requests rapidly (exceeds 100/min limit)
for i in {1..101}; do
  curl -s "http://localhost:5000/api/admin/donations" > /dev/null
done

# Last request should return 429 (Too Many Requests)
```

### 4. Check Logs
```bash
# View recent logs
tail -f logs/api.log

# Expected pattern:
# [req_id] START PATCH /api/admin/donations/{id}
# [req_id] ADMIN_ACTION UPDATE_STATUS Donation#HH-001
# [req_id] END PATCH /api/admin/donations/{id} - Status: 200
```

---

## 📊 Request/Response Flow

```
1. Request arrives
   ↓
2. Rate limit check
   ├─ Allowed → Continue
   └─ Denied → Return 429
   ↓
3. Authentication check (JWT)
   ├─ Valid → Continue
   └─ Invalid → Return 401
   ↓
4. Authorization check (Admin role)
   ├─ Admin → Continue
   └─ Not Admin → Return 403
   ↓
5. Request validation (Marshmallow schema)
   ├─ Valid → Continue
   └─ Invalid → Return 400 + errors
   ↓
6. Business logic (Process request)
   ├─ Success → Log admin action
   └─ Error → Log error, Return error status
   ↓
7. Response sent
   ├─ Log request end
   └─ Add rate limit headers
   ↓
8. Request complete
```

---

## Request Validation

### Files
- `api/validators.py` - Marshmallow schemas for all endpoints

### Available Schemas

#### CreateDonationSchema
Validation for POST donation endpoints:
- food_name: required, 1-200 chars
- category: required, must be valid category
- quantity: required, > 0, max 100,000
- unit: required, must be valid unit
- expiry_date: required, must be future date
- storage: required, valid storage method
- donor_email: required, valid email format
- donor_zip: required, valid ZIP format
- safety_score: 0-100
- All other fields validated with appropriate constraints

#### UpdateDonationSchema
Validation for PATCH donation endpoints (partial updates):
- status: optional, valid status value
- safety_score: optional, 0-100
- requires_review: optional, boolean

#### VerifyOrganizationSchema
- is_verified: required, boolean

#### ResolveFlagSchema
- status: optional, valid status value
- resolution_notes: required, 10-2000 chars

#### SuspendUserSchema
- is_active: required, boolean
- reason: optional, max 500 chars

### Usage Example
```python
from api.validators import validate_request_data, UpdateDonationSchema

data = request.get_json()
validated_data, errors = validate_request_data(UpdateDonationSchema, data)

if errors:
    return {'success': False, 'error': errors}, 400

# Use validated_data which is type-safe
```

---

## Rate Limiting

### Files
- `api/rate_limiter.py` - Rate limiting implementation

### Features
- **Sliding Window Algorithm** - Accurate rate limiting across time windows
- **Per-User and Per-IP** - Tracks by user ID or IP address
- **Thread-Safe** - Uses locks for concurrent requests
- **Automatic Cleanup** - Removes old entries every hour

### Rate Limit Presets

| Limit | Requests | Window |
|-------|----------|--------|
| General | 100/min | 60s |
| Strict (Auth) | 10/min | 60s |
| Admin | 200/min | 60s |

### Usage

#### Basic Rate Limiting
```python
from api.rate_limiter import rate_limit

@app.route('/api/endpoint')
@rate_limit()  # Uses default_limiter (100 req/min)
def endpoint():
    pass
```

#### Specific Limiter
```python
@app.route('/api/strict')
@rate_limit(limiter=strict_limiter)  # 10 req/min
def strict_endpoint():
    pass
```

#### Custom Limit
```python
@app.route('/api/custom')
@rate_limit(custom_limit=(50, 300))  # 50 requests per 5 minutes
def custom_endpoint():
    pass
```

### Response When Rate Limited
```json
{
  "success": false,
  "message": "Rate limit exceeded",
  "error": "Too many requests. Try again after 2026-03-23 16:45:00",
  "data": {
    "limit": 100,
    "remaining": 0,
    "reset": 1742814300,
    "window_seconds": 60
  },
  "status": 429
}
```

### Response Headers
- `X-RateLimit-Remaining` - Requests remaining in current window
- `X-RateLimit-Reset` - Unix timestamp when limit resets

---

## API Logging

### Files
- `api/api_logger.py` - Comprehensive logging system

### Features
- **Request/Response Logging** - Automatic logging of all requests
- **File & Console Output** - Rotating file handler + console
- **Request IDs** - Unique ID for tracing requests through logs
- **Admin Action Logging** - Special logging for admin operations
- **Security Event Logging** - Logs unauthorized/suspicious activity
- **Performance Metrics** - Tracks request duration

### Implemented Logging

#### Request Start
```
[req_id] START GET /api/admin/donations - User: user_123 - IP: 192.168.1.1
```

#### Request End
```
[req_id] END GET /api/admin/donations - Status: 200 - Duration: 0.342s - User: user_123
```

#### Admin Actions
```
[req_id] ADMIN_ACTION UPDATE_STATUS Donation#HH-ABC123 - Admin: user_5 - Details: {"old_status": "posted", "new_status": "confirmed"}
```

#### Security Events
```
[req_id] SECURITY_EVENT UNAUTHORIZED - Endpoint: /api/admin/flags - User: anonymous - IP: 192.168.1.x - Details: {"reason": "Missing token"}
```

#### Database Operations
```
[req_id] DB UPDATE Donation - SUCCESS - User: user_123 (0.125s)
```

### Usage

#### In Endpoints
```python
from api.api_logger import api_logger

# Automatic per-request logging
# But you can also add manual logging:

api_logger.log_admin_action('VERIFY', 'Organization', org_id, {
    'details': 'Organization verified'
})

api_logger.log_security_event('SUSPICIOUS_LOGIN', {
    'user': 'username',
    'ip': '192.168.x.x'
})

api_logger.log_error(error, context={'endpoint': '/api/...', 'user_id': 123})
```

#### Log Files
- Location: `logs/api.log`
- Rotation: 10MB max size, 10 backup files
- Automatically created if directory doesn't exist

## Data Validation Flow

```
Request
  ↓
Rate Limit Check
  ├─ Allowed? Continue
  └─ Denied? Return 429
  ↓
Authentication Check
  ├─ Valid? Continue
  └─ Invalid? Return 401
  ↓
Authorization Check (Admin)
  ├─ Admin? Continue
  └─ Not Admin? Return 403
  ↓
Request Validation (Marshmallow)
  ├─ Valid? Continue
  └─ Invalid? Return 400 + errors
  ↓
Process Request
  ├─ Success? Log admin action
  └─ Error? Log error with context
  ↓
Response
```

---

## Data Integrity Checks

### Verify Constraints
```bash
python -c "from utils.database_constraints import DatabaseConstraints; DatabaseConstraints.print_constraints()"
```

### Validate Database Integrity
```bash
python -c "
from utils.database_constraints import validate_data_integrity
issues = validate_data_integrity()
for table, problems in issues.items():
    if problems:
        print(f'{table}: {problems}')
"
```

---

## Setup Instructions

### In main.py
Already integrated:
```python
from api.api_logger import setup_api_logging
from api.rate_limiter import add_rate_limit_headers

# Initialize logging
setup_api_logging(app, log_file='logs/api.log')

# Add rate limit headers to responses
app.after_request(add_rate_limit_headers)
```

### Create Logs Directory
```bash
mkdir -p logs
```

### Test Constraints
```bash
python scripts/init_admin_db.py  # Creates Flag table with constraints
```

---

## Example: Full Request Flow

### Request
```bash
curl -X PATCH "http://localhost:5000/api/admin/donations/HH-ABC123" \
  -H "Cookie: jwt_python_flask=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "confirmed",
    "safety_score": 90
  }'
```

### Logs Generated

1. **Request Start**:
   ```
   [a1b2c3d4] START PATCH /api/admin/donations - User: user_5 - IP: 192.168.1.1
   ```

2. **Rate Limit Check**: Passed (admin_limiter: 200/min)

3. **Auth Check**: Admin verified

4. **Validation**: Data validated with UpdateDonationSchema

5. **Admin Action Log**:
   ```
   [a1b2c3d4] ADMIN_ACTION UPDATE_STATUS Donation#HH-ABC123 - Admin: user_5 - Details: {"old_status": "posted", "new_status": "confirmed", "old_score": 80, "new_score": 90}
   ```

6. **Request End**:
   ```
   [a1b2c3d4] END PATCH /api/admin/donations - Status: 200 - Duration: 0.189s - User: user_5
   ```

---

## 🔍 Log Examples

### Successful Admin Action
```
[a1b2c3d4] START PATCH /api/admin/donations/HH-ABC123 - User: user_5 - IP: 192.168.1.1
[a1b2c3d4] ADMIN_ACTION UPDATE_STATUS Donation#HH-ABC123 - User: user_5 - Details: {"old_status": "posted", "new_status": "confirmed", "old_score": 80, "new_score": 95}
[a1b2c3d4] END PATCH /api/admin/donations/HH-ABC123 - Status: 200 - Duration: 0.234s - User: user_5
```

### Validation Error
```
[b2c3d4e5] START PATCH /api/admin/donations/HH-XYZ789 - User: user_5
[b2c3d4e5] SECURITY_EVENT VALIDATION_ERROR - Details: {"field_errors": {"safety_score": ["Must be between 0 and 100"]}}
[b2c3d4e5] END PATCH /api/admin/donations/HH-XYZ789 - Status: 400 - Duration: 0.045s
```

### Rate Limit Exceeded
```
[c3d4e5f6] START GET /api/admin/donations - User: user_5
[c3d4e5f6] Rate limit exceeded (100 req/min)
[c3d4e5f6] END GET /api/admin/donations - Status: 429 - Duration: 0.008s
```

---

## ⚙️ Configuration

### Default Rate Limits (in api/rate_limiter.py)
```python
default_limiter = RateLimiter(limit=100, window=60)      # 100 req/min
strict_limiter = RateLimiter(limit=10, window=60)        # 10 req/min
admin_limiter = RateLimiter(limit=200, window=60)        # 200 req/min
```

### Log Configuration (in api/api_logger.py)
```python
max_bytes = 10 * 1024 * 1024  # 10MB per file
backup_count = 10              # Keep 10 backup files
log_level = logging.INFO       # Log level
```