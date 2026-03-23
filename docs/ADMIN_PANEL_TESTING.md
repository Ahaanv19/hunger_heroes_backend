# Admin Panel API - Testing Guide

## Quick Start

### 1. Initialize Database
```bash
cd /home/anonymous-dyce/hunger_heroes/hunger_heroes_backend
python scripts/init_admin_db.py
```

### 2. Get Admin Token
First, authenticate as an admin user:

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "your_admin_password"
  }'
```

Save the JWT token from the response.

---

## Test Scenarios

### Scenario 1: List Donations with Filters

**Test**: Get all flagged donations with low safety scores

```bash
ADMIN_TOKEN="your_token_here"

curl -X GET "http://localhost:5000/api/admin/donations?flagged=true&safety_score=low_score&page=1" \
  -H "Cookie: jwt_python_flask=$ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected**: Status 200, returns list of flagged donations with safety score < 70

---

### Scenario 2: Update Donation Status

**Test**: Approve a donation by updating its status and safety score

```bash
ADMIN_TOKEN="your_token_here"
DONATION_ID="HH-M3X7K9-AB2F"

curl -X PATCH "http://localhost:5000/api/admin/donations/$DONATION_ID" \
  -H "Cookie: jwt_python_flask=$ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "confirmed",
    "safety_score": 95,
    "requires_review": false
  }'
```

**Expected**: Status 200, donation updated

---

### Scenario 3: List Unverified Organizations

**Test**: Get all unverified organizations for verification review

```bash
ADMIN_TOKEN="your_token_here"

curl -X GET "http://localhost:5000/api/admin/organizations?verified=false&page=1" \
  -H "Cookie: jwt_python_flask=$ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected**: Status 200, returns list of unverified organizations

---

### Scenario 4: Verify Organization

**Test**: Verify an organization

```bash
ADMIN_TOKEN="your_token_here"
ORG_ID="1"

curl -X PATCH "http://localhost:5000/api/admin/organizations/$ORG_ID/verify" \
  -H "Cookie: jwt_python_flask=$ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_verified": true
  }'
```

**Expected**: Status 200, organization marked as verified

---

### Scenario 5: Get Critical Issues

**Test**: Get all critical/high priority flags that need immediate action

```bash
ADMIN_TOKEN="your_token_here"

curl -X GET "http://localhost:5000/api/admin/flags?status=open&severity=critical" \
  -H "Cookie: jwt_python_flask=$ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected**: Status 200, returns critical open flags

---

### Scenario 6: Resolve a Flag

**Test**: Mark a flag as resolved with notes

```bash
ADMIN_TOKEN="your_token_here"
FLAG_ID="1"

curl -X PATCH "http://localhost:5000/api/admin/flags/$FLAG_ID/resolve" \
  -H "Cookie: jwt_python_flask=$ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved",
    "resolution_notes": "Reviewed food safety documentation. Donation approved for distribution."
  }'
```

**Expected**: Status 200, flag marked as resolved

---

### Scenario 7: List Active Users

**Test**: Get all active donors

```bash
ADMIN_TOKEN="your_token_here"

curl -X GET "http://localhost:5000/api/admin/users?role=Donor&status=active&page=1" \
  -H "Cookie: jwt_python_flask=$ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected**: Status 200, returns active donors with activity metrics

---

### Scenario 8: Get User Details

**Test**: Get detailed information about a specific user

```bash
ADMIN_TOKEN="your_token_here"
USER_ID="42"

curl -X GET "http://localhost:5000/api/admin/users/$USER_ID" \
  -H "Cookie: jwt_python_flask=$ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected**: Status 200, returns detailed user info with flags

---

### Scenario 9: Suspend User

**Test**: Suspend a user account for violations

```bash
ADMIN_TOKEN="your_token_here"
USER_ID="42"

curl -X PATCH "http://localhost:5000/api/admin/users/$USER_ID/suspend" \
  -H "Cookie: jwt_python_flask=$ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false,
    "reason": "Multiple food safety violations"
  }'
```

**Expected**: Status 200, user account suspended

---

### Scenario 10: Get Dashboard Stats

**Test**: Get platform statistics for admin dashboard

```bash
ADMIN_TOKEN="your_token_here"

curl -X GET "http://localhost:5000/api/admin/stats" \
  -H "Cookie: jwt_python_flask=$ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected**: Status 200, returns comprehensive platform statistics

---

## Error Testing

### Test 1: Missing Authentication Token

```bash
curl -X GET "http://localhost:5000/api/admin/donations"
```

**Expected**: Status 401, "Authentication token is missing"

---

### Test 2: Invalid Token

```bash
curl -X GET "http://localhost:5000/api/admin/donations" \
  -H "Cookie: jwt_python_flask=invalid_token_here"
```

**Expected**: Status 401, "Invalid authentication token"

---

### Test 3: Non-Admin User

```bash
# Use token from a regular user (non-admin)
curl -X GET "http://localhost:5000/api/admin/donations" \
  -H "Cookie: jwt_python_flask=$USER_TOKEN"
```

**Expected**: Status 403, "Admin access required"

---

### Test 4: Not Found

```bash
ADMIN_TOKEN="your_token_here"

curl -X GET "http://localhost:5000/api/admin/donations/NONEXISTENT-ID-9999" \
  -H "Cookie: jwt_python_flask=$ADMIN_TOKEN"
```

**Expected**: Status 404, "Donation not found"

---

## Pagination Testing

### Test Pagination

```bash
ADMIN_TOKEN="your_token_here"

# Page 2, 10 items per page
curl -X GET "http://localhost:5000/api/admin/users?page=2&per_page=10" \
  -H "Cookie: jwt_python_flask=$ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected**: Returns items 11-20, page info shows page=2

---

## Filter Testing

### Test Multiple Filters

```bash
ADMIN_TOKEN="your_token_here"

# Donations: posted status, low safety score, flagged, page 1
curl -X GET "http://localhost:5000/api/admin/donations?status=posted&safety_score=low_score&flagged=true&page=1" \
  -H "Cookie: jwt_python_flask=$ADMIN_TOKEN"
```

**Expected**: Filters applied correctly

---

## Integration Tests

### Test: Flag a Donation and Resolve It

1. **Create a flag for a donation**:
   ```bash
   # This would be done via another endpoint or directly in code
   # For now, test manual resolution process
   ```

2. **Verify flag appears in admin list**:
   ```bash
   curl -X GET "http://localhost:5000/api/admin/flags?status=open" \
     -H "Cookie: jwt_python_flask=$ADMIN_TOKEN"
   ```

3. **Resolve the flag**:
   ```bash
   curl -X PATCH "http://localhost:5000/api/admin/flags/1/resolve" \
     -H "Cookie: jwt_python_flask=$ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"status": "resolved", "resolution_notes": "Issue addressed"}'
   ```

4. **Verify flag is resolved**:
   ```bash
   curl -X GET "http://localhost:5000/api/admin/flags?status=resolved" \
     -H "Cookie: jwt_python_flask=$ADMIN_TOKEN"
   ```

---

## Performance Testing

### Load Test: List 1000s of Donations

```bash
ADMIN_TOKEN="your_token_here"

# Test pagination with large result set
time curl -X GET "http://localhost:5000/api/admin/donations?page=50&per_page=20" \
  -H "Cookie: jwt_python_flask=$ADMIN_TOKEN"
```

**Expected**: Response time < 2 seconds

---

## Postman Collection

You can import this collection into Postman:

```json
{
  "info": {
    "name": "Admin Panel API",
    "version": "1.0"
  },
  "items": [
    {
      "name": "Get Donations",
      "request": {
        "method": "GET",
        "url": "{{base_url}}/api/admin/donations?page=1",
        "header": [
          {"key": "Cookie", "value": "jwt_python_flask={{admin_token}}"}
        ]
      }
    }
  ]
}
```

---

## Troubleshooting

### Issue: 401 Unauthorized
- ✓ Check token is not expired
- ✓ Verify user is Admin role
- ✓ Check JWT token name matches config (default: `jwt_python_flask`)

### Issue: 500 Internal Server Error
- ✓ Check database connection
- ✓ Verify Flag table exists
- ✓ Check logs for SQL errors

### Issue: Empty Results
- ✓ Verify filters are correct
- ✓ Check data exists before filtering
- ✓ Try without filters first

---

## Next Steps

1. **Create sample data**: Generate test donations, organizations, flags
2. **UI Dashboard**: Build web interface for admin panel
3. **Audit Logging**: Log all admin actions for compliance
4. **Notifications**: Alert admins of critical flags
5. **Bulk Operations**: Support batch actions for efficiency

---
