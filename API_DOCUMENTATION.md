# Django User Management API Documentation

## Overview

This document provides comprehensive documentation for the Django User Management REST API. The API implements role-based access control and provides endpoints for user authentication, profile management, and administrative operations.

## Base URL

```
http://127.0.0.1:8000/api
```

## Authentication

The API uses token-based authentication. After successful login, include the token in request headers:

```
Authorization: Token <your_token_here>
```

## User Roles and Permissions

### Role Hierarchy
- **Admin**: Full system access, can manage all users and roles
- **Faculty**: Can view and manage students, limited administrative access
- **Staff**: Limited access, can view faculty information
- **Student**: Basic access, can view faculty and other students

### Permission Matrix

| Operation | Admin | Faculty | Staff | Student |
|-----------|-------|---------|-------|---------|
| View all users | ✅ | ✅ (limited) | ✅ (limited) | ✅ (limited) |
| Create users | ✅ | ✅ | ❌ | ❌ |
| Update own profile | ✅ | ✅ | ✅ | ✅ |
| Update other users | ✅ | ✅ (students only) | ❌ | ❌ |
| Delete users | ✅ | ❌ | ❌ | ❌ |
| Change user roles | ✅ | ❌ | ❌ | ❌ |
| Toggle user status | ✅ | ✅ (students only) | ❌ | ❌ |

## API Endpoints

### Authentication Endpoints

#### Login
```http
POST /api/auth/login/
```

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "userpassword"
}
```

**Response (Success):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "role": "student",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    "token": "abc123def456..."
}
```

**Response (Error):**
```json
{
    "email": ["This field is required."],
    "password": ["Invalid credentials"]
}
```

#### Logout
```http
POST /api/auth/logout/
```

**Headers:** `Authorization: Token <token>`

**Response:**
```json
{
    "message": "Logout successful"
}
```

#### Get Profile
```http
GET /api/auth/profile/
```

**Headers:** `Authorization: Token <token>`

**Response:**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "student",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Change Password
```http
POST /api/auth/change-password/
```

**Headers:** `Authorization: Token <token>`

**Request Body:**
```json
{
    "old_password": "currentpassword",
    "new_password": "newsecurepassword",
    "new_password_confirm": "newsecurepassword"
}
```

**Response:**
```json
{
    "message": "Password changed successfully"
}
```

### User Management Endpoints

#### List Users
```http
GET /api/users/
```

**Headers:** `Authorization: Token <token>`

**Query Parameters:**
- `role` (optional): Filter by role (admin, faculty, staff, student)
- `is_active` (optional): Filter by active status (true/false)

**Response:**
```json
[
    {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "role": "student",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    {
        "id": 2,
        "username": "jane_smith",
        "email": "jane@example.com",
        "role": "faculty",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
]
```

#### Create User (Registration)
```http
POST /api/users/
```

**Request Body:**
```json
{
    "username": "new_user",
    "email": "newuser@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "role": "student"
}
```

**Response:**
```json
{
    "id": 3,
    "username": "new_user",
    "email": "newuser@example.com",
    "role": "student",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Get User Details
```http
GET /api/users/{id}/
```

**Headers:** `Authorization: Token <token>`

**Response:**
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "student",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Update User
```http
PATCH /api/users/{id}/
```

**Headers:** `Authorization: Token <token>`

**Request Body:**
```json
{
    "username": "updated_username",
    "email": "updated@example.com"
}
```

**Response:**
```json
{
    "id": 1,
    "username": "updated_username",
    "email": "updated@example.com",
    "role": "student",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
}
```

#### Delete User
```http
DELETE /api/users/{id}/
```

**Headers:** `Authorization: Token <token>`

**Response:** `204 No Content`

#### Toggle User Status
```http
PATCH /api/users/{id}/toggle-status/
```

**Headers:** `Authorization: Token <token>`

**Response:**
```json
{
    "message": "User john_doe has been deactivated",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "role": "student",
        "is_active": false,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
    }
}
```

#### Change User Role
```http
PATCH /api/users/{id}/change-role/
```

**Headers:** `Authorization: Token <token>`

**Request Body:**
```json
{
    "role": "faculty"
}
```

**Response:**
```json
{
    "message": "User john_doe role changed to faculty",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "role": "faculty",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T12:00:00Z"
    }
}
```

### Utility Endpoints

#### Get Available Roles
```http
GET /api/roles/
```

**Headers:** `Authorization: Token <token>`

**Response:**
```json
{
    "roles": [
        {"value": "admin", "label": "Admin"},
        {"value": "faculty", "label": "Faculty"},
        {"value": "staff", "label": "Staff"},
        {"value": "student", "label": "Student"}
    ]
}
```

#### Get Filter Roles
```http
GET /api/filter-roles/
```

**Headers:** `Authorization: Token <token>`

**Response:**
```json
{
    "filter_roles": [
        {"value": "", "label": "All Roles"},
        {"value": "faculty", "label": "Faculty"},
        {"value": "student", "label": "Students"}
    ]
}
```

## Error Responses

### HTTP Status Codes

- `200 OK` - Successful GET request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Error Response Format

```json
{
    "detail": "Error message describing what went wrong"
}
```

**Or for validation errors:**

```json
{
    "field_name": ["Error message for this field"],
    "another_field": ["Another error message"]
}
```

## Rate Limiting

Currently, no rate limiting is implemented. In production, consider implementing rate limiting to prevent abuse.

## CORS Configuration

The API is configured to accept requests from the frontend application. Ensure CORS settings are properly configured for your deployment environment.

## Security Considerations

1. **HTTPS**: Use HTTPS in production to protect authentication tokens
2. **Token Expiration**: Consider implementing token expiration and refresh mechanisms
3. **Input Validation**: All inputs are validated using Django REST Framework serializers
4. **SQL Injection**: Protected by Django ORM
5. **XSS Prevention**: JSON responses prevent XSS attacks
6. **CSRF Protection**: API uses token authentication, reducing CSRF risks

## Testing the API

### Using curl

```bash
# Login
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "password"}'

# Get users (replace TOKEN with actual token)
curl -X GET http://127.0.0.1:8000/api/users/ \
  -H "Authorization: Token TOKEN"
```

### Using Python requests

```python
import requests

# Login
response = requests.post('http://127.0.0.1:8000/api/auth/login/', json={
    'email': 'admin@example.com',
    'password': 'password'
})

if response.status_code == 200:
    token = response.json()['token']
    
    # Get users
    headers = {'Authorization': f'Token {token}'}
    users_response = requests.get('http://127.0.0.1:8000/api/users/', headers=headers)
    print(users_response.json())
```

## Frontend Integration

The PyQt6 frontend application automatically handles:
- Token storage and management
- Request authentication headers
- Error handling and user feedback
- Role-based UI adjustments

Refer to the frontend documentation for details on client-side implementation.
