# Postman API Testing Guide for Hunger Heroes

## Overview

This guide explains how to test all Hunger Heroes API endpoints using Postman. Follow these steps to test each endpoint and verify data changes in the SQLite database.

## Testing Workflow

### Phase 1: Authentication & Login

#### 1.1 Get User JWT Token

**Endpoint:** POST `/api/user`

```
POST http://localhost:5001/api/user
Content-Type: application/json

{
  "name": "Test Donor",
  "uid": "test_donor_{{$timestamp}}",
  "password": "secure123",
  "email": "testdonor@example.com",
  "role": "Donor"
}
```

**Expected Response (200):**
```json
{
  "id": 1,
  "uid": "test_donor_1234567890",
  "name": "Test Donor",
  "email": "testdonor@example.com",
  "role": "Donor"
}
```

#### 1.2 Login and Get JWT Cookie

**Note:** The Flask app uses cookies for authentication. Postman automatically handles cookies. When you make requests, Postman stores JWT tokens in cookies.

**Manual Token Debug:**
1. Open browser and navigate to `http://localhost:5001/login`
2. Login with username/password
3. Open browser DevTools → Application → Cookies
4. Look for `jwt_python_flask` cookie

---

### Phase 2: User Management

#### 2.1 Create Different User Roles

Create users with each role (`Donor`, `Receiver`, `Volunteer`, `Admin`):

**POST /api/user - Create Admin User**
```json
{
  "name": "Admin User",
  "uid": "admin_test",
  "password": "admin123",
  "email": "admin@hungerheroes.com",
  "role": "Admin"
}
```

**POST /api/user - Create Receiver User**
```json
{
  "name": "Food Bank Receiver",
  "uid": "receiver_test",
  "password": "recv123",
  "email": "receiver@foodbank.org",
  "role": "Receiver"
}
```

**POST /api/user - Create Volunteer User**
```json
{
  "name": "Jane Volunteer",
  "uid": "volunteer_test",
  "password": "vol123",
  "email": "volunteer@hungerheroes.com",
  "role": "Volunteer"
}
```

#### 2.2 Get All Users

**GET /api/users** (requires auth)

```
GET http://localhost:5001/api/users
```

---

### Phase 3: Organizations

#### 3.1 Create Organization

**POST /api/organizations** (if endpoint exists, or POST /api directly)

```json
{
  "name": "Downtown Food Bank",
  "type": "food_bank",
  "address": "456 Main St, San Diego, CA 92101",
  "zip_code": "92101",
  "phone": "(619) 555-1234",
  "email": "info@dtfoodbank.org",
  "capacity": 2000,
  "accepted_food_types": ["canned", "fresh-produce", "dairy", "frozen"],
  "storage_capacity_lbs": 25000,
  "refrigeration_available": true,
  "dietary_restrictions_servable": ["vegan", "vegetarian"]
}
```

#### 3.2 Get Organizations

**GET /api/businesses** (public endpoint for businesses/organizations)

```
GET http://localhost:5001/api/businesses
```

---

### Phase 4: Donations

#### 4.1 Create a Donation

**POST /api/donation** (no auth required initially)

```json
{
  "food_name": "Organic Apples",
  "category": "fresh-produce",
  "food_type": "raw",
  "quantity": 50,
  "unit": "lbs",
  "expiry_date": "2026-04-05",
  "storage": "refrigerated",
  "allergens": [],
  "dietary_tags": ["vegan"],
  "donor_name": "Apple Farm Co",
  "donor_email": "farm@apples.com",
  "donor_phone": "(619) 555-5555",
  "donor_zip": "92101",
  "special_instructions": "Keep refrigerated, do not freeze",
  "allergen_info": "None",
  "serving_count": 250,
  "temperature_at_pickup": 38.0,
  "storage_method": "refrigerator",
  "pickup_location": "456 Farm Road, San Diego, CA",
  "pickup_window_start": "2026-03-05T09:00:00",
  "pickup_window_end": "2026-03-05T17:00:00"
}
```

**Expected Response (201):**
```json
{
  "message": "Donation created successfully",
  "donation": {
    "id": "HH-XXXXX-XXXX",
    "food_name": "Organic Apples",
    "status": "active",
    "created_at": "2026-03-05T12:00:00"
  }
}
```

#### 4.2 Get Current User's Donations

**GET /api/donation** (requires auth)

```
GET http://localhost:5001/api/donation
Cookie: jwt=<JWT_TOKEN>
```

**Response:**
```json
{
  "donations": [
    {
      "id": "HH-XXXXX-XXXX",
      "food_name": "Organic Apples",
      "status": "active",
      "quantity": 50,
      "unit": "lbs",
      "expiry_date": "2026-04-05"
    }
  ],
  "count": 1
}
```

#### 4.3 Update Donation Status

**PUT /api/donation/<id>** or custom endpoint

```
PUT http://localhost:5001/api/donation/HH-XXXXX-XXXX
Content-Type: application/json

{
  "status": "accepted",
  "accepted_by": "Food Bank Manager"
}
```

---

### Phase 5: Allergen Profiles

#### 5.1 Create Allergen Profile

**POST /api/allergen-profiles**

```json
{
  "donation_id": "HH-XXXXX-XXXX",
  "contains_nuts": true,
  "contains_dairy": false,
  "contains_gluten": false,
  "contains_soy": false,
  "contains_shellfish": false,
  "contains_eggs": false,
  "is_vegetarian": true,
  "is_vegan": false,
  "is_halal": false,
  "is_kosher": false
}
```

#### 5.2 Get Allergen Profile for Donation

**GET /api/allergen-profiles/<donation_id>**

```
GET http://localhost:5001/api/allergen-profiles/HH-XXXXX-XXXX
```

---

### Phase 6: Food Safety Logs

#### 6.1 Create Food Safety Log (Inspector)

**POST /api/food-safety-logs**

```json
{
  "donation_id": "HH-XXXXX-XXXX",
  "temperature_reading": 38.5,
  "storage_method": "refrigerator",
  "handling_notes": "Food properly packaged and labeled. Temperature maintained at 38.5°F",
  "inspector_id": 1,
  "passed_inspection": true,
  "inspection_date": "2026-03-05T14:00:00"
}
```

#### 6.2 View Food Safety Logs for Donation

**GET /api/food-safety-logs/<donation_id>**

```
GET http://localhost:5001/api/food-safety-logs/HH-XXXXX-XXXX
```

---

### Phase 7: Donation Feedback

#### 7.1 Submit Donation Feedback

**POST /api/donation-feedback**

```json
{
  "donation_id": "HH-XXXXX-XXXX",
  "reviewer_id": 2,
  "food_quality_rating": 4,
  "timeliness_rating": 5,
  "overall_rating": 4,
  "comments": "Great donation! Fresh produce arrived on time. Well packaged.",
  "reported_issues": []
}
```

#### 7.2 Get Feedback for Donation

**GET /api/donation-feedback/<donation_id>**

```
GET http://localhost:5001/api/donation-feedback/HH-XXXXX-XXXX
```