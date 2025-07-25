# Mobile App Authentication Debug Guide

## ✅ Backend Status: WORKING
The JWT authentication system is working perfectly on the backend. Tests show:
- Login successful with JWT token generation
- Catch creation works with proper Authorization header
- User authentication and validation working correctly

## 🔍 Common Mobile App Issues

### 1. Authorization Header Format
**CORRECT FORMAT:**
```javascript
headers: {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
}
```

**COMMON MISTAKES:**
- Missing "Bearer " prefix
- Extra spaces: "Bearer  token" (double space)
- Wrong case: "authorization" instead of "Authorization"
- Token encoding issues

### 2. URL Endpoint Issues
**CORRECT URL:** `http://your-ip:8000/api/v1/catches/` (note trailing slash)
**WRONG URL:** `http://your-ip:8000/api/v1/catches` (missing trailing slash)

The backend shows a 307 redirect when the trailing slash is missing.

### 3. Token Expiration
- Access tokens expire in **30 minutes**
- Check if your app handles token refresh
- Verify token timestamp with: `console.log('Token expires:', new Date(tokenData.exp * 1000))`

### 4. Network/CORS Issues
- Ensure your mobile device can reach the server IP
- Check if CORS is properly configured for your mobile app's requests
- Verify the server is accessible from your mobile device's network

## 🛠️ Debug Steps for Your Mobile App

### Step 1: Log the Full Request
```javascript
console.log('Request URL:', url);
console.log('Request Headers:', headers);
console.log('Request Body:', JSON.stringify(requestBody));
console.log('Token:', accessToken);
```

### Step 2: Check Token Validity
```javascript
// Decode JWT token to check expiration
const tokenParts = accessToken.split('.');
const payload = JSON.parse(atob(tokenParts[1]));
console.log('Token payload:', payload);
console.log('Token expires:', new Date(payload.exp * 1000));
console.log('Current time:', new Date());
```

### Step 3: Test with Curl
Replace `YOUR_TOKEN` with your actual token:
```bash
curl -X POST http://your-ip:8000/api/v1/catches/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "species": "Test Fish",
    "weight": 2.5,
    "photo_url": "http://example.com/photo.jpg",
    "location": {"lat": 43.054, "lng": -89.450},
    "shared_with_followers": true
  }'
```

### Step 4: Check Server Logs
Look for these log patterns:
- `INFO:auth:JWT payload:` - Token is being processed
- `INFO:auth:Successfully authenticated user:` - Authentication succeeded
- `ERROR:auth:` - Authentication failed

## 🚨 Most Likely Issues

Based on the backend being working correctly, your mobile app issue is most likely:

1. **Authorization Header Format** - Missing "Bearer " prefix or wrong format
2. **URL Trailing Slash** - Missing trailing slash causing 307 redirect
3. **Token Expiration** - Token expired and needs refresh
4. **Network Issues** - Mobile device can't reach server IP

## 📱 React Native Specific Checks

### AsyncStorage Token Retrieval
```javascript
const token = await AsyncStorage.getItem('accessToken');
console.log('Retrieved token:', token);
```

### Fetch Request Format
```javascript
const response = await fetch(`${API_BASE_URL}/catches/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(catchData),
});

console.log('Response status:', response.status);
console.log('Response headers:', response.headers);
const responseText = await response.text();
console.log('Response body:', responseText);
```

## 🎯 Immediate Action Items

1. **Add logging** to your mobile app to capture the exact request format
2. **Check the Authorization header** format in your mobile app
3. **Verify the URL** includes the trailing slash: `/catches/`
4. **Test token expiration** - try logging in again to get a fresh token
5. **Network test** - ensure your mobile device can reach the server

The backend is working perfectly, so the issue is definitely in how the mobile app is formatting or sending the request.
