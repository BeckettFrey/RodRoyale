#!/usr/bin/env python3

# Script to fix all remaining catch tests with the new pattern

import re

# Read the current file
with open('tests/test_catches.py', 'r') as f:
    content = f.read()

# Define the helper function (already exists)
helper_function = '''def create_test_user_and_auth(client, unique_suffix=None):
    """Helper function to create a test user and return auth headers."""
    if unique_suffix is None:
        unique_suffix = uuid.uuid4().hex[:8]
    
    user_data = {
        "username": f"testuser_{unique_suffix}",
        "email": f"test_{unique_suffix}@example.com",
        "password": "testpass123"
    }
    
    # Register user
    reg_response = client.post("/api/v1/auth/register", json=user_data)
    assert reg_response.status_code == 201
    user_id = reg_response.json()["user"]["_id"]  # Use _id instead of id
    
    # Login to get token (use email, not username)
    login_response = client.post("/api/v1/auth/login", json={
        "email": user_data["email"],  # Use email for login
        "password": user_data["password"]
    })
    assert login_response.status_code == 200
    token = login_response.json()["token"]["access_token"]  # Access nested token
    auth_headers = {"Authorization": f"Bearer {token}"}
    
    return user_id, auth_headers'''

# Patterns for various test types we need to fix
replacements = [
    # Pattern 1: Simple tests that just need auth
    (
        r'def (test_[^(]*_unauthorized|test_[^(]*_not_found|test_[^(]*_missing_fields)\(self, client.*?\):\s*"""([^"]+)"""\s*',
        r'def \1(self, client):\n        """\2"""\n        '
    ),
    
    # Remove old user data creation patterns
    (
        r'        # Create test user via API\s*user_data = \{[^}]+\}\s*reg_response = client\.post[^)]+\)\s*assert reg_response\.status_code == 201[^\n]*\n\s*# Login to get token[^\n]*\n\s*login_response = client\.post[^)]+\)\s*assert login_response\.status_code == 200[^\n]*\n\s*token = login_response\.json\(\)\["[^"]*"\]\s*auth_headers = \{"Authorization": f"Bearer \{token\}"\}',
        r'\n        user_id, auth_headers = create_test_user_and_auth(client)'
    ),
]

# Apply replacements
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

# Manual fixes for specific patterns that are harder to regex
# Fix catch ID extraction patterns
content = re.sub(r'catch_ids = \[catch\["id"\] for catch in response_data\]', 
                 r'catch_ids = [catch.get("id", catch.get("_id")) for catch in response_data]', 
                 content)

# Fix assertions for id field
content = re.sub(r'assert "id" in response_data', 
                 r'assert ("id" in response_data) or ("_id" in response_data)', 
                 content)

# Write the updated content
with open('tests/test_catches.py', 'w') as f:
    f.write(content)

print("Fixed catch tests file!")
