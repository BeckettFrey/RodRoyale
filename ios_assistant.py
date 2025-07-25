#!/usr/bin/env python3
"""
Monitor server response and provide iOS-specific debugging info
"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_health_check():
    """Test basic server connectivity"""
    print("🏥 Testing Basic Server Health")
    print("=" * 35)
    
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
        print(f"   Health endpoint: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Server is responding")
            return True
        else:
            print("   ❌ Server health check failed")
            return False
    except Exception as e:
        print(f"   ❌ Server not reachable: {e}")
        return False

def get_server_info():
    """Get server configuration info"""
    print("\n⚙️  Server Configuration")
    print("=" * 28)
    
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/")
        if response.status_code == 200:
            data = response.json()
            print(f"   API Version: {data.get('version', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
            
            # Check CORS headers
            print("\n   CORS Headers:")
            cors_headers = {k: v for k, v in response.headers.items() 
                          if 'access-control' in k.lower()}
            if cors_headers:
                for key, value in cors_headers.items():
                    print(f"     {key}: {value}")
            else:
                print("     No CORS headers found")
                
            return True
        else:
            print(f"   ❌ Server info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Cannot get server info: {e}")
        return False

def test_ios_common_issues():
    """Test common iOS networking issues"""
    print("\n📱 iOS-Specific Issue Tests")
    print("=" * 32)
    
    # Test different localhost variations
    base_urls = [
        "http://localhost:8000/api/v1",
        "http://127.0.0.1:8000/api/v1",
        # Add your computer's IP - you'll need to find this manually
    ]
    
    for base_url in base_urls:
        print(f"\n   Testing: {base_url}")
        try:
            response = requests.get(f"{base_url.replace('/api/v1', '')}/health", timeout=2)
            if response.status_code == 200:
                print("     ✅ Reachable")
            else:
                print(f"     ⚠️  Status: {response.status_code}")
        except requests.exceptions.ConnectTimeout:
            print("     ❌ Timeout")
        except requests.exceptions.ConnectionError:
            print("     ❌ Connection refused")
        except Exception as e:
            print(f"     ❌ Error: {e}")

def check_database_connection():
    """Check if database operations are working"""
    print("\n🗄️  Database Connectivity")
    print("=" * 27)
    
    # Try to login to test DB connection
    login_data = {"email": "test@Rod Royale.com", "password": "testpassword123"}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            print("   ✅ Database connection working (login successful)")
            return True
        else:
            print(f"   ⚠️  Login failed: {response.status_code}")
            if response.status_code == 401:
                print("      This is normal if test user doesn't exist")
            return False
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        return False

def print_ios_troubleshooting():
    """Print iOS-specific troubleshooting steps"""
    print("\n🛠️  iOS Troubleshooting Guide")
    print("=" * 33)
    
    print("1. 📱 In your iOS app, check these common issues:")
    print("   • Are you using 'localhost' or '127.0.0.1' in your base URL?")
    print("   • Is App Transport Security (ATS) blocking HTTP requests?")
    print("   • Are you sending the 'Bearer ' prefix with your JWT token?")
    print("   • Is the Content-Type header set to 'application/json'?")
    
    print("\n2. 🔍 In Xcode, enable network debugging:")
    print("   • Product → Scheme → Edit Scheme → Run → Arguments")
    print("   • Add Environment Variable: OS_ACTIVITY_MODE = disable")
    print("   • Add Launch Argument: -com.apple.CoreData.SQLDebug 1")
    
    print("\n3. 📊 Check iOS Console Logs:")
    print("   • Window → Devices and Simulators → Select Simulator → Open Console")
    print("   • Look for network errors when creating posts")
    
    print("\n4. 🌐 Test with different base URLs in iOS:")
    print("   • http://localhost:8000/api/v1 (often fails in simulator)")
    print("   • http://127.0.0.1:8000/api/v1 (usually works)")
    print("   • http://YOUR_COMPUTER_IP:8000/api/v1 (for device testing)")
    
    print("\n5. 🔧 Quick fix - Add to Info.plist (development only):")
    print("""   <key>NSAppTransportSecurity</key>
   <dict>
       <key>NSAllowsArbitraryLoads</key>
       <true/>
   </dict>""")

def find_computer_ip():
    """Help find the computer's IP address for device testing"""
    print("\n🌐 Finding Your Computer's IP Address")
    print("=" * 40)
    
    print("   Run these commands in Terminal to find your IP:")
    print("   • ifconfig | grep 'inet ' | grep -v 127.0.0.1")
    print("   • ifconfig en0 | grep inet")
    print("   • ipconfig getifaddr en0")
    
    print("\n   Then update your iOS app's base URL to:")
    print("   • http://YOUR_IP:8000/api/v1")
    
    print("\n   Example: if your IP is 192.168.1.100:")
    print("   • http://192.168.1.100:8000/api/v1")

def main():
    print("🔍 iOS Debugging Assistant")
    print("=" * 30)
    
    # Run basic connectivity tests
    health_ok = test_health_check()
    server_info_ok = get_server_info()
    
    if health_ok:
        test_ios_common_issues()
        check_database_connection()
    
    # Always show troubleshooting guide
    print_ios_troubleshooting()
    find_computer_ip()
    
    print("\n📝 Summary:")
    if health_ok and server_info_ok:
        print("   ✅ Backend is working correctly")
        print("   ❓ Issue is likely in iOS app configuration")
        print("   👉 Check the troubleshooting steps above")
    else:
        print("   ❌ Backend has issues that need to be fixed first")
        print("   🔧 Start the server with: python main.py")

if __name__ == "__main__":
    main()
