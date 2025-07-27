# File: generate_security_key.py
#!/usr/bin/env python3
"""
Security Key Generator for Rod Royale API
Generates a secure SECRET_KEY for JWT token signing
"""

import secrets
import os

def generate_secret_key():
    """Generate a cryptographically secure secret key"""
    return secrets.token_urlsafe(32)

def create_env_file():
    """Create or update .env file with secure SECRET_KEY"""
    env_file = ".env"
    secret_key = generate_secret_key()
    
    # Read existing .env file if it exists
    env_lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_lines = f.readlines()
    
    # Check if SECRET_KEY already exists
    secret_key_exists = False
    for i, line in enumerate(env_lines):
        if line.startswith('SECRET_KEY='):
            # Ask user if they want to replace existing key
            response = input(f"SECRET_KEY already exists in {env_file}. Replace it? (y/N): ")
            if response.lower() == 'y':
                env_lines[i] = f"SECRET_KEY={secret_key}\n"
                secret_key_exists = True
            else:
                print("Keeping existing SECRET_KEY.")
                return
            break
    
    # Add SECRET_KEY if it doesn't exist
    if not secret_key_exists:
        env_lines.append(f"SECRET_KEY={secret_key}\n")
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.writelines(env_lines)
    
    print(f"✅ SECRET_KEY generated and saved to {env_file}")
    print(f"🔑 Your SECRET_KEY: {secret_key}")
    print("\n🔒 Security Notes:")
    print("1. Keep this key secret and never commit it to version control")
    print("2. Use different keys for development and production")
    print("3. Store production keys in secure environment variables")
    print("4. Regenerate keys periodically for enhanced security")

def main():
    print("🔐 Rod Royale API - Security Key Generator")
    print("=" * 50)
    
    # Generate and display a secret key
    secret_key = generate_secret_key()
    print(f"Generated SECRET_KEY: {secret_key}")
    print(f"Key length: {len(secret_key)} characters")
    
    print("\nOptions:")
    print("1. Copy this key and add it manually to your .env file")
    print("2. Let this script create/update your .env file automatically")
    
    choice = input("\nEnter your choice (1 or 2): ")
    
    if choice == "2":
        create_env_file()
    else:
        print("\n📋 Manual Setup Instructions:")
        print("1. Create or edit your .env file")
        print(f"2. Add this line: SECRET_KEY={secret_key}")
        print("3. Make sure .env is in your .gitignore file")
    
    print("\n🎯 Next Steps:")
    print("1. Set CORS_ORIGINS with your actual domain(s)")
    print("2. Configure HTTPS certificates for production")
    print("3. Set ENVIRONMENT=production for production deployment")

if __name__ == "__main__":
    main()
