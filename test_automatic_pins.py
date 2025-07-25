#!/usr/bin/env python3
"""
Test automatic pin creation when add_to_map is True
"""
import requests
import json

BASE_URL = "http://192.168.86.29:8000/api/v1"

def get_auth_token():
    """Get authentication token"""
    print("🔑 Getting authentication token...")
    login_data = {
        "email": "test@Rod Royale.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            auth_response = response.json()
            token = auth_response['token']['access_token']
            print("✅ Authentication successful")
            return token
        else:
            print(f"❌ Authentication failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_automatic_pin_creation():
    """Test creating a catch with add_to_map=True"""
    print("\n📍 Testing Automatic Pin Creation")
    print("=" * 40)
    
    token = get_auth_token()
    if not token:
        print("❌ Cannot test without authentication")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test case 1: Create catch with add_to_map=True
    catch_data = {
        "species": "Auto Pin Test Bass",
        "weight": 3.5,
        "photo_url": "https://example.com/test-auto-pin.jpg",
        "location": {
            "lat": 43.054013,
            "lng": -89.450452
        },
        "shared_with_followers": True,
        "add_to_map": True  # This should automatically create a pin
    }
    
    print("Creating catch with add_to_map=True...")
    print(f"Data: {json.dumps(catch_data, indent=2)}")
    
    try:
        # Create the catch
        response = requests.post(f"{BASE_URL}/catches/", json=catch_data, headers=headers)
        
        if response.status_code == 201:
            catch_result = response.json()
            catch_id = catch_result.get('_id')
            print("✅ Catch created successfully!")
            print(f"   Catch ID: {catch_id}")
            
            # Now check if a pin was automatically created
            print("\nChecking for automatically created pin...")
            pins_response = requests.get(f"{BASE_URL}/pins/", headers=headers)
            
            if pins_response.status_code == 200:
                pins = pins_response.json()
                
                # Look for a pin with our catch_id
                auto_pin = None
                for pin in pins:
                    if pin.get('catch_id') == catch_id:
                        auto_pin = pin
                        break
                
                if auto_pin:
                    print("✅ Automatic pin creation SUCCESS!")
                    print(f"   Pin ID: {auto_pin.get('id')}")
                    print(f"   Pin Location: {auto_pin.get('location')}")
                    print(f"   Pin Visibility: {auto_pin.get('visibility')}")
                    return True
                else:
                    print("❌ Automatic pin creation FAILED!")
                    print(f"   No pin found for catch ID: {catch_id}")
                    print(f"   Available pins: {len(pins)}")
                    return False
            else:
                print(f"❌ Failed to fetch pins: {pins_response.status_code}")
                return False
                
        else:
            print(f"❌ Catch creation failed: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {json.dumps(error, indent=2)}")
            except:
                print(f"   Error text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def test_manual_pin_creation():
    """Test manual pin creation (original functionality)"""
    print("\n📌 Testing Manual Pin Creation")
    print("=" * 35)
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # First create a catch without add_to_map
    catch_data = {
        "species": "Manual Pin Test Bass",
        "weight": 2.8,
        "photo_url": "https://example.com/test-manual-pin.jpg",
        "location": {
            "lat": 43.054013,
            "lng": -89.450452
        },
        "shared_with_followers": False,
        "add_to_map": False  # No automatic pin
    }
    
    print("Creating catch with add_to_map=False...")
    
    try:
        # Create the catch
        response = requests.post(f"{BASE_URL}/catches/", json=catch_data, headers=headers)
        
        if response.status_code == 201:
            catch_result = response.json()
            catch_id = catch_result.get('_id')
            print(f"✅ Catch created: {catch_id}")
            
            # Now manually create a pin
            pin_data = {
                "catch_id": catch_id,
                "location": {
                    "lat": 43.054013,
                    "lng": -89.450452
                },
                "visibility": "public"
            }
            
            print("Manually creating pin...")
            pin_response = requests.post(f"{BASE_URL}/pins/", json=pin_data, headers=headers)
            
            if pin_response.status_code == 201:
                pin_result = pin_response.json()
                print("✅ Manual pin creation SUCCESS!")
                print(f"   Pin ID: {pin_result.get('_id')}")
                return True
            else:
                print(f"❌ Manual pin creation failed: {pin_response.status_code}")
                try:
                    error = pin_response.json()
                    print(f"   Error: {json.dumps(error, indent=2)}")
                except:
                    print(f"   Error text: {pin_response.text}")
                return False
        else:
            print(f"❌ Catch creation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Manual test error: {e}")
        return False

def main():
    print("🧪 Testing Automatic Pin Creation Feature")
    print("=" * 50)
    
    auto_success = test_automatic_pin_creation()
    manual_success = test_manual_pin_creation()
    
    print("\n📊 Test Results")
    print("=" * 20)
    print(f"   Automatic pin creation: {'✅ PASS' if auto_success else '❌ FAIL'}")
    print(f"   Manual pin creation: {'✅ PASS' if manual_success else '❌ FAIL'}")
    
    if auto_success:
        print("\n🎉 Automatic pin creation is now working!")
        print("   When you set add_to_map: true in your iOS app,")
        print("   pins will be automatically created on the map.")
    else:
        print("\n🔧 Automatic pin creation needs debugging.")
        print("   Check the server logs for any error messages.")

if __name__ == "__main__":
    main()
