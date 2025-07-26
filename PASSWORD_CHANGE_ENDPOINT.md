# Password Change Endpoint Documentation

## Overview

The Rod Royale API now includes a secure password change endpoint that allows authenticated users to change their password with proper security validations.

## Endpoint Details

**URL:** `POST /auth/change-password`

**Authentication:** Required (Bearer Token)

**Content-Type:** `application/json`

## Request Format

```json
{
  "current_password": "your_current_password",
  "new_password": "your_new_password"
}
```

## Response Format

### Success Response (200 OK)
```json
{
  "message": "Password changed successfully",
  "detail": "Please log in again with your new password"
}
```

### Error Responses

#### Wrong Current Password (400 Bad Request)
```json
{
  "detail": "Current password is incorrect"
}
```

#### Same Password (400 Bad Request)
```json
{
  "detail": "New password must be different from current password"
}
```

#### Unauthenticated (401 Unauthorized)
```json
{
  "detail": "Not authenticated"
}
```

#### Validation Error (422 Unprocessable Entity)
```json
{
  "detail": [
    {
      "loc": ["body", "new_password"],
      "msg": "ensure this value has at least 6 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

## Security Features

1. **Authentication Required**: Must provide valid JWT access token
2. **Current Password Verification**: Must provide correct current password
3. **Password Uniqueness**: New password must be different from current password
4. **Password Validation**: New password must meet minimum requirements (6-100 characters)
5. **Secure Hashing**: Passwords are hashed using bcrypt before storage
6. **Audit Logging**: Password changes are logged for security monitoring

## Usage Examples

### Python (requests)
```python
import requests

# Get your access token from login
login_response = requests.post("http://localhost:8000/auth/login", json={
    "email": "user@example.com",
    "password": "current_password"
})
access_token = login_response.json()["token"]["access_token"]

# Change password
headers = {"Authorization": f"Bearer {access_token}"}
change_data = {
    "current_password": "current_password",
    "new_password": "new_secure_password"
}

response = requests.post(
    "http://localhost:8000/auth/change-password",
    json=change_data,
    headers=headers
)

if response.status_code == 200:
    print("Password changed successfully!")
    # Re-login with new password
else:
    print(f"Error: {response.json()['detail']}")
```

### JavaScript (fetch)
```javascript
// Get your access token from login first
const loginResponse = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: 'user@example.com',
        password: 'current_password'
    })
});
const loginData = await loginResponse.json();
const accessToken = loginData.token.access_token;

// Change password
const changeResponse = await fetch('http://localhost:8000/auth/change-password', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        current_password: 'current_password',
        new_password: 'new_secure_password'
    })
});

if (changeResponse.ok) {
    const result = await changeResponse.json();
    console.log('Password changed:', result.message);
    // Re-login with new password
} else {
    const error = await changeResponse.json();
    console.error('Error:', error.detail);
}
```

### cURL
```bash
# First login to get access token
ACCESS_TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"current_password"}' \
  | jq -r '.token.access_token')

# Change password
curl -X POST "http://localhost:8000/auth/change-password" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "current_password",
    "new_password": "new_secure_password"
  }'
```

## Testing

Run the test suite to verify the endpoint functionality:

```bash
# Run the password change tests
python test_password_change_endpoint.py

# Or run with pytest
pytest test_password_change_endpoint.py -v
```

## Security Considerations

1. **Always use HTTPS in production** to protect passwords in transit
2. **Implement rate limiting** to prevent brute force attacks
3. **Consider password strength requirements** beyond minimum length
4. **Log password change attempts** for security monitoring
5. **Invalidate existing sessions** after password change (future enhancement)
6. **Implement password history** to prevent reuse of recent passwords (future enhancement)

## Best Practices

1. **Prompt for re-authentication** after password change
2. **Clear stored tokens** on the client side after password change
3. **Notify users via email** when password is changed (future enhancement)
4. **Validate password strength** on the client side for better UX
5. **Handle network errors gracefully** in client applications

## Integration with Existing System

The password change endpoint integrates seamlessly with the existing Rod Royale authentication system:

- Uses the same JWT token authentication as other protected endpoints
- Follows the same error handling patterns
- Uses the established password hashing mechanism
- Maintains consistency with existing API response formats
