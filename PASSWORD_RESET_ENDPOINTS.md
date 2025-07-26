# Password Reset Endpoints Documentation

## Overview

The Rod Royale API now includes secure password reset endpoints that allow users to reset their passwords via email verification.

## Endpoints

### 1. Request Password Reset

**URL:** `POST /api/v1/auth/forgot-password`

**Authentication:** None required

**Content-Type:** `application/json`

#### Request Format
```json
{
  "email": "user@example.com"
}
```

#### Response Format

**Success Response (200 OK)**
```json
{
  "message": "If an account with this email exists, a password reset link has been sent",
  "detail": "Check your email for password reset instructions",
  "reset_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "note": "In production, this token would be sent via email, not returned in the API response"
}
```

**Note:** For security, the response is the same whether the email exists or not. The `reset_token` field is only included in demo mode and should be removed in production.

### 2. Reset Password

**URL:** `POST /api/v1/auth/reset-password`

**Authentication:** None required (uses reset token)

**Content-Type:** `application/json`

#### Request Format
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "new_password": "your_new_secure_password"
}
```

#### Response Format

**Success Response (200 OK)**
```json
{
  "message": "Password reset successfully",
  "detail": "You can now log in with your new password"
}
```

**Error Responses**

#### Invalid/Expired Token (400 Bad Request)
```json
{
  "detail": "Invalid or expired reset token"
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

1. **Time-Limited Tokens**: Reset tokens expire after 1 hour
2. **Single-Use Tokens**: Each reset token can only be used once
3. **Email Verification**: Reset tokens are tied to specific email addresses
4. **Secure Token Generation**: Uses JWT with HMAC signing
5. **No Email Enumeration**: Same response for existing/non-existing emails
6. **Password Validation**: New passwords must meet security requirements (6-100 characters)

## Complete Password Reset Flow

### Step 1: User Requests Password Reset
```bash
curl -X POST "https://localhost:8000/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### Step 2: User Receives Reset Token
In production, the user would receive an email with a reset link containing the token. For demo purposes, the token is returned in the API response.

### Step 3: User Resets Password
```bash
curl -X POST "https://localhost:8000/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "new_password": "my_new_secure_password"
  }'
```

### Step 4: User Logs In with New Password
```bash
curl -X POST "https://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "my_new_secure_password"
  }'
```

## Usage Examples

### Python (requests)
```python
import requests

# Step 1: Request password reset
reset_request = {
    "email": "user@example.com"
}

response = requests.post(
    "https://localhost:8000/api/v1/auth/forgot-password",
    json=reset_request,
    verify=False  # Only for demo with self-signed certs
)

if response.status_code == 200:
    result = response.json()
    reset_token = result.get("reset_token")  # In demo mode only
    
    # Step 2: Reset password with token
    reset_data = {
        "token": reset_token,
        "new_password": "my_new_secure_password"
    }
    
    reset_response = requests.post(
        "https://localhost:8000/api/v1/auth/reset-password",
        json=reset_data,
        verify=False
    )
    
    if reset_response.status_code == 200:
        print("Password reset successful!")
```

### JavaScript (fetch)
```javascript
// Step 1: Request password reset
const resetRequest = await fetch('https://localhost:8000/api/v1/auth/forgot-password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: 'user@example.com' })
});

if (resetRequest.ok) {
    const result = await resetRequest.json();
    const resetToken = result.reset_token; // Demo mode only
    
    // Step 2: Reset password
    const resetResponse = await fetch('https://localhost:8000/api/v1/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            token: resetToken,
            new_password: 'my_new_secure_password'
        })
    });
    
    if (resetResponse.ok) {
        console.log('Password reset successful!');
    }
}
```

## Production Considerations

### Email Integration
In production, you should integrate with an email service to send reset tokens:

```python
# Example with SendGrid
import sendgrid
from sendgrid.helpers.mail import Mail

def send_password_reset_email(email: str, reset_token: str):
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    
    reset_link = f"https://yourapp.com/reset-password?token={reset_token}"
    
    message = Mail(
        from_email='noreply@yourapp.com',
        to_emails=email,
        subject='Password Reset Request',
        html_content=f'''
        <h2>Password Reset Request</h2>
        <p>Click the link below to reset your password:</p>
        <a href="{reset_link}">Reset Password</a>
        <p>This link expires in 1 hour.</p>
        '''
    )
    
    sg.send(message)
```

### Security Enhancements

1. **Rate Limiting**: Implement rate limiting on password reset requests
2. **Email Templates**: Use professional email templates
3. **Logging**: Log all password reset attempts for security monitoring
4. **Token Cleanup**: Implement cleanup for expired tokens
5. **HTTPS Only**: Ensure all password reset operations use HTTPS

### Database Considerations

Consider adding a `password_reset_tokens` collection to track tokens:

```python
# Optional: Store reset tokens in database for better tracking
await db.password_reset_tokens.insert_one({
    "email": email,
    "token_hash": hash_token(reset_token),
    "created_at": datetime.utcnow(),
    "expires_at": datetime.utcnow() + timedelta(hours=1),
    "used": False
})
```

## Testing

Run the demo script to test the complete password reset flow:

```bash
python password_reset_demo.py
```

This will demonstrate:
- Creating a test user
- Requesting password reset
- Using reset token to change password
- Verifying old password no longer works
- Verifying new password works
- Testing security (token reuse prevention)

## Error Handling

The endpoints include comprehensive error handling for:
- Invalid email formats
- Non-existent users
- Expired tokens
- Invalid tokens
- Password validation errors
- Database errors

All errors are properly logged for debugging and security monitoring.
