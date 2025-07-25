#!/usr/bin/env python3
"""
Complete Catch Upload Workflow Example
Shows step-by-step process from user registration to catch upload
"""

import requests
import json
import tempfile
import os
from PIL import Image

BASE_URL = "http://localhost:8000/api/v1"

class CatchUploadDemo:
    def __init__(self):
        self.access_token = None
        self.user_data = None
        
    def create_sample_image(self):
        """Create a sample fish image for testing"""
        # Create a simple test image that looks like a fish photo
        img = Image.new('RGB', (1200, 800), color='lightblue')
        
        # Add some simple "fish-like" elements (very basic)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        
        # Draw a simple fish shape
        draw.ellipse([300, 250, 900, 550], fill='silver', outline='darkgray', width=3)
        draw.polygon([(900, 400), (1050, 350), (1050, 450)], fill='silver', outline='darkgray')  # tail
        draw.ellipse([400, 320, 450, 370], fill='black')  # eye
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        img.save(temp_file.name, 'JPEG', quality=85)
        temp_file.close()
        
        return temp_file.name
    
    def step_1_register_user(self):
        """Step 1: Register a new user"""
        print("🎣 STEP 1: Register New User")
        print("=" * 40)
        
        user_registration = {
            "username": "demo_angler_2025",
            "email": "demo_angler@Rod Royale.com",
            "password": "SecureFishing123!",
            "bio": "Passionate angler sharing my catches"
        }
        
        print("📝 Registration data:")
        print(json.dumps(user_registration, indent=2))
        print()
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=user_registration)
            
            print(f"📤 Request: POST {BASE_URL}/auth/register")
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 201:
                self.user_data = response.json()
                print("✅ User registered successfully!")
                print(f"   User ID: {self.user_data.get('_id', 'N/A')}")
                print(f"   Username: {self.user_data.get('username', 'N/A')}")
                return True
            else:
                print("❌ Registration failed:")
                print(f"   {response.json()}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return False
    
    def step_2_login_user(self):
        """Step 2: Login to get authentication token"""
        print("\n🔐 STEP 2: Login to Get Authentication Token")
        print("=" * 50)
        
        login_data = {
            "email": "demo_angler@Rod Royale.com",
            "password": "SecureFishing123!"
        }
        
        print("🔑 Login credentials:")
        print(json.dumps(login_data, indent=2))
        print()
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            
            print(f"📤 Request: POST {BASE_URL}/auth/login")
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                auth_response = response.json()
                self.access_token = auth_response["token"]["access_token"]
                
                print("✅ Login successful!")
                print(f"   Token Type: {auth_response['token']['token_type']}")
                print(f"   Expires In: {auth_response['token']['expires_in']} seconds")
                print(f"   Access Token: {self.access_token[:20]}...{self.access_token[-10:]}")
                return True
            else:
                print("❌ Login failed:")
                print(f"   {response.json()}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return False
    
    def step_3_upload_catch(self):
        """Step 3: Upload catch with image"""
        print("\n📸 STEP 3: Upload Catch with Image")
        print("=" * 40)
        
        # Create sample image
        image_path = self.create_sample_image()
        print(f"🖼️  Created sample image: {image_path}")
        
        # Prepare catch data
        catch_data = {
            'species': 'Largemouth Bass',
            'weight': 4.2,
            'lat': 28.5383,  # Orlando, FL
            'lng': -81.3792,
            'shared_with_followers': True
        }
        
        print("\n📊 Catch data:")
        for key, value in catch_data.items():
            print(f"   {key}: {value}")
        print()
        
        try:
            # Prepare the multipart form data
            with open(image_path, 'rb') as image_file:
                files = {
                    'file': ('bass_catch.jpg', image_file, 'image/jpeg')
                }
                
                headers = {
                    'Authorization': f'Bearer {self.access_token}'
                }
                
                print(f"📤 Request: POST {BASE_URL}/catches/upload-with-image")
                print("📎 Content-Type: multipart/form-data")
                print(f"🔐 Authorization: Bearer {self.access_token[:10]}...")
                print()
                
                response = requests.post(
                    f"{BASE_URL}/catches/upload-with-image",
                    data=catch_data,
                    files=files,
                    headers=headers
                )
            
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 201:
                catch_response = response.json()
                print("✅ Catch uploaded successfully!")
                print("\n📋 Complete catch object:")
                print(json.dumps(catch_response, indent=2))
                
                # Highlight the different URLs
                print("\n🖼️  Generated Image URLs:")
                print(f"   📷 Original: {catch_response.get('photo_url', 'N/A')}")
                print(f"   🖼️  Optimized (800x600): {catch_response.get('optimized_url', 'N/A')}")
                print(f"   📱 Thumbnail (300x300): {catch_response.get('thumbnail_url', 'N/A')}")
                print(f"   📍 Small (150x150): {catch_response.get('small_thumbnail_url', 'N/A')}")
                
                return catch_response
            else:
                print("❌ Catch upload failed:")
                print(f"   {response.json()}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return None
        finally:
            # Clean up the temporary image
            if os.path.exists(image_path):
                os.unlink(image_path)
                print(f"\n🧹 Cleaned up temporary image: {image_path}")
    
    def step_4_verify_catch(self, catch_data):
        """Step 4: Verify the catch was created and URLs work"""
        print("\n🔍 STEP 4: Verify Catch Creation")
        print("=" * 40)
        
        if not catch_data:
            print("❌ No catch data to verify")
            return
        
        catch_id = catch_data.get('_id')
        
        try:
            # Get the catch by ID
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(f"{BASE_URL}/catches/{catch_id}", headers=headers)
            
            print(f"📤 Request: GET {BASE_URL}/catches/{catch_id}")
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                retrieved_catch = response.json()
                print("✅ Catch successfully retrieved from database")
                print(f"   ID: {retrieved_catch.get('_id')}")
                print(f"   Species: {retrieved_catch.get('species')}")
                print(f"   Weight: {retrieved_catch.get('weight')} lbs")
                print(f"   Shared: {retrieved_catch.get('shared_with_followers')}")
                
                # Test image URLs
                print("\n🌐 Testing Image URLs:")
                urls_to_test = [
                    ('Original', retrieved_catch.get('photo_url')),
                    ('Optimized', retrieved_catch.get('optimized_url')),
                    ('Thumbnail', retrieved_catch.get('thumbnail_url')),
                    ('Small Thumbnail', retrieved_catch.get('small_thumbnail_url'))
                ]
                
                for name, url in urls_to_test:
                    if url:
                        try:
                            img_response = requests.head(url, timeout=5)
                            status = "✅ Accessible" if img_response.status_code == 200 else f"❌ Error {img_response.status_code}"
                            print(f"   {name}: {status}")
                        except:
                            print(f"   {name}: ❌ Network error")
                    else:
                        print(f"   {name}: ❌ URL missing")
                
                return True
            else:
                print("❌ Failed to retrieve catch:")
                print(f"   {response.json()}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return False
    
    def show_frontend_integration(self):
        """Show how frontend would integrate this workflow"""
        print("\n💻 FRONTEND INTEGRATION EXAMPLE")
        print("=" * 45)
        
        print("📱 React/JavaScript Example:")
        print("""
// Complete catch upload function
const uploadCatch = async (imageFile, catchData, authToken) => {
  const formData = new FormData();
  
  // Add image file
  formData.append('file', imageFile);
  
  // Add catch data
  formData.append('species', catchData.species);
  formData.append('weight', catchData.weight);
  formData.append('lat', catchData.location.lat);
  formData.append('lng', catchData.location.lng);
  formData.append('shared_with_followers', catchData.shared);
  
  try {
    const response = await fetch('/api/v1/catches/upload-with-image', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken}`
      },
      body: formData
    });
    
    if (response.ok) {
      const newCatch = await response.json();
      console.log('Catch uploaded successfully!', newCatch);
      
      // Use different URLs for different purposes
      displayInFeed(newCatch.thumbnail_url);      // 300x300 for feed
      showOnMap(newCatch.small_thumbnail_url);    // 150x150 for map pins
      openDetailView(newCatch.optimized_url);     // 800x600 for detail view
      
      return newCatch;
    } else {
      throw new Error('Upload failed');
    }
  } catch (error) {
    console.error('Upload error:', error);
    throw error;
  }
};

// Usage example
const handleCatchUpload = async (imageFile) => {
  const catchData = {
    species: 'Bass',
    weight: 3.5,
    location: { lat: 28.5383, lng: -81.3792 },
    shared: true
  };
  
  try {
    const newCatch = await uploadCatch(imageFile, catchData, userToken);
    // Handle success - update UI, show success message, etc.
  } catch (error) {
    // Handle error - show error message, retry option, etc.
  }
};
        """)
    
    def run_complete_workflow(self):
        """Run the complete workflow"""
        print("🎣 COMPLETE CATCH UPLOAD WORKFLOW DEMO")
        print("=" * 50)
        print("This demo shows the complete process from user registration")
        print("to uploading a catch with image in the Rod Royale app.")
        print()
        
        # Check if server is running
        try:
            health_response = requests.get("http://localhost:8000/health", timeout=5)
            if health_response.status_code != 200:
                print("❌ Server not responding. Please start the server:")
                print("   uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
                return
        except:
            print("❌ Cannot connect to server. Please start the server:")
            print("   uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
            return
        
        print("✅ Server is running, starting workflow...\n")
        
        # Run each step
        if self.step_1_register_user():
            if self.step_2_login_user():
                catch_data = self.step_3_upload_catch()
                if catch_data:
                    self.step_4_verify_catch(catch_data)
                    
                    print("\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
                    print("=" * 45)
                    print("✅ User registered and authenticated")
                    print("✅ Image uploaded to Cloudinary")
                    print("✅ Multiple optimized URLs generated")
                    print("✅ Catch data stored in MongoDB")
                    print("✅ Privacy settings applied")
                    print("\n🚀 Your catch is now live in the app!")
                    
                    self.show_frontend_integration()
                else:
                    print("\n❌ Workflow failed at catch upload step")
            else:
                print("\n❌ Workflow failed at login step")
        else:
            print("\n❌ Workflow failed at registration step")

if __name__ == "__main__":
    demo = CatchUploadDemo()
    demo.run_complete_workflow()
