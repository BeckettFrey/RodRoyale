#!/bin/bash

# API Testing Script with curl
# Your credentials:
USER_ID="6883168abb9192f5819a205d"
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2ODgzMTY4YWJiOTE5MmY1ODE5YTIwNWQiLCJleHAiOjE3NTM0NzQxMTEsInR5cGUiOiJhY2Nlc3MifQ.YG7YCfJBCtmOuSgjoei0Hl0EwBdG1i4-jlruyvdWRko"
BASE_URL="http://localhost:8000/api/v1"

echo "🧪 Testing Rod Royale API with curl..."
echo "=================================="

echo -e "\n1. Testing Authentication - Get Current User"
curl -s -X GET "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'

echo -e "\n2. Getting Your User Profile"
curl -s -X GET "$BASE_URL/users/$USER_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'

echo -e "\n3. Getting Your Catches"
curl -s -X GET "$BASE_URL/catches/me" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'

echo -e "\n4. Getting Your Feed"
curl -s -X GET "$BASE_URL/catches/feed" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'

echo -e "\n5. Getting Your Pins"
curl -s -X GET "$BASE_URL/pins/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.'

echo -e "\n6. Creating a Test Catch with Automatic Pin"
curl -s -X POST "$BASE_URL/catches/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "species": "Test Bass",
    "weight": 2.8,
    "photo_url": "https://example.com/test-bass.jpg",
    "location": {
      "lat": 40.7589,
      "lng": -73.9851
    },
    "shared_with_followers": true,
    "add_to_map": true
  }' | jq '.'

echo -e "\n✅ API Testing Complete!"
