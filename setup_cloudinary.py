#!/usr/bin/env python3
"""
Cloudinary Setup Helper
Helps verify and test Cloudinary configuration
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

def check_environment_variables():
    """Check if required Cloudinary environment variables are set"""
    required_vars = [
        'CLOUDINARY_CLOUD_NAME',
        'CLOUDINARY_API_KEY', 
        'CLOUDINARY_API_SECRET'
    ]
    
    print("🔍 Checking Cloudinary environment variables...")
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
        else:
            # Show partial value for security
            masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '*' * len(value)
            print(f"✅ {var}: {masked_value}")
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("\n✅ All Cloudinary environment variables are set!")
    return True

def create_env_file_template():
    """Create a .env file template with Cloudinary configuration"""
    env_example_path = Path(".env.example")
    env_path = Path(".env")
    
    if env_path.exists():
        print(f"📄 .env file already exists at {env_path}")
        return
    
    if env_example_path.exists():
        print(f"📋 Copying {env_example_path} to {env_path}")
        with open(env_example_path, 'r') as f:
            content = f.read()
        
        with open(env_path, 'w') as f:
            f.write(content)
        
        print("✅ Created .env file from template")
        print("📝 Please edit .env and add your Cloudinary credentials")
    else:
        # Create basic .env template
        env_content = """# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=rod_royale_db

# Cloudinary Configuration (Required for image storage)
# Get these values from your Cloudinary dashboard at https://cloudinary.com/console
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
"""
        
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"📄 Created basic .env file at {env_path}")
        print("📝 Please edit .env and add your Cloudinary credentials")

def test_cloudinary_connection():
    """Test connection to Cloudinary"""
    try:
        import cloudinary
        import cloudinary.api
        
        # Configure Cloudinary
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )
        
        print("🌤️  Testing Cloudinary connection...")
        
        # Test API connection
        result = cloudinary.api.ping()
        
        if result.get('status') == 'ok':
            print("✅ Cloudinary connection successful!")
            
            # Get account info
            usage = cloudinary.api.usage()
            print("📊 Account info:")
            print(f"   - Cloud name: {os.getenv('CLOUDINARY_CLOUD_NAME')}")
            print(f"   - Storage used: {usage.get('storage', {}).get('usage', 0)} bytes")
            print(f"   - Transformations: {usage.get('transformations', {}).get('usage', 0)}")
            return True
        else:
            print("❌ Cloudinary connection failed")
            return False
            
    except ImportError:
        print("❌ Cloudinary package not installed")
        print("   Run: pip install cloudinary==1.36.0")
        return False
    except Exception as e:
        print(f"❌ Cloudinary connection error: {str(e)}")
        print("   Please check your credentials and try again")
        return False

def main():
    print("🌤️  Cloudinary Setup Helper")
    print("=" * 50)
    
    # Load environment variables from .env file if it exists
    env_path = Path(".env")
    if env_path.exists():
        print(f"📄 Loading environment variables from {env_path}")
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("💡 Install python-dotenv to automatically load .env files:")
            print("   pip install python-dotenv")
    
    # Check if .env file exists, create if not
    if not env_path.exists():
        print("📝 Creating .env file template...")
        create_env_file_template()
        print("\n⚠️  Please edit .env with your Cloudinary credentials and run this script again")
        return
    
    # Check environment variables
    if not check_environment_variables():
        print("\n📝 Please edit .env with your Cloudinary credentials and run this script again")
        print("\n🔗 Get your credentials from: https://cloudinary.com/console")
        return
    
    # Test Cloudinary connection
    if test_cloudinary_connection():
        print("\n🎉 Cloudinary setup is complete and working!")
        print("\n🚀 Next steps:")
        print("   1. Start your API server: uvicorn main:app --reload")
        print("   2. Test image upload: python test_cloudinary_upload.py")
        print("   3. Check the API documentation at: http://localhost:8000/docs")
    else:
        print("\n❌ Cloudinary setup failed. Please check your credentials.")

if __name__ == "__main__":
    main()
