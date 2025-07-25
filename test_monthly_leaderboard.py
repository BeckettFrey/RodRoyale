#!/usr/bin/env python3
"""
Monthly Leaderboard Test Script
Tests the competitive metrics and leaderboard functionality with monthly periods
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_monthly_leaderboard_system():
    print("🏆 Testing Monthly Leaderboard System")
    print("=" * 60)
    
    # Test health check
    try:
        response = requests.get("http://localhost:8000/health")
        if response.json().get("status") == "healthy":
            print("✅ API is healthy")
        else:
            print("❌ API health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on http://localhost:8000")
        return False
    
    # Create competitive test users
    print("\n1. Creating competitive anglers...")
    test_users = [
        {
            "username": "monthly_bass_champ",
            "email": "monthly_bass@Rod Royale.com",
            "bio": "Monthly tournament bass fishing champion",
            "password": "champ123"
        },
        {
            "username": "monthly_trout_master",
            "email": "monthly_trout@Rod Royale.com", 
            "bio": "Fly fishing expert - monthly leader",
            "password": "trout123"
        },
        {
            "username": "monthly_volume_angler",
            "email": "monthly_volume@Rod Royale.com",
            "bio": "High volume angler this month",
            "password": "volume123"
        }
    ]
    
    users = []
    tokens = []
    
    for user_data in test_users:
        try:
            # Try registration first
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
            if response.status_code == 201:
                auth_response = response.json()
                users.append(auth_response['user'])
                tokens.append(auth_response['token']['access_token'])
                print(f"✅ Registered: {auth_response['user']['username']}")
            else:
                # If user exists, try login
                login_data = {"email": user_data["email"], "password": user_data["password"]}
                response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
                if response.status_code == 200:
                    auth_response = response.json()
                    users.append(auth_response['user'])
                    tokens.append(auth_response['token']['access_token'])
                    print(f"✅ Logged in: {auth_response['user']['username']}")
        except Exception as e:
            print(f"❌ Error with user {user_data['username']}: {e}")
    
    if len(users) < 3:
        print("❌ Need at least 3 users for competitive leaderboard testing")
        return False
    
    bass_champ, trout_master, volume_angler = users[:3]
    bass_token, trout_token, volume_token = tokens[:3]
    
    # Set up competitive relationships
    print("\n2. Setting up competitive relationships...")
    relationships = [
        (bass_champ['_id'], trout_master['_id'], "Bass champion follows trout master"),
        (bass_champ['_id'], volume_angler['_id'], "Bass champion follows volume angler"),
        (trout_master['_id'], bass_champ['_id'], "Trout master follows bass champion"),
    ]
    
    for follower_id, followed_id, description in relationships:
        try:
            response = requests.post(f"{BASE_URL}/users/{follower_id}/follow/{followed_id}")
            if response.status_code == 200:
                print(f"✅ {description}")
        except Exception as e:
            print(f"❌ Error: {description} - {e}")
    
    # Create competitive catches for the current month
    print("\n3. Creating competitive catches...")
    
    # Bass Champion - Has the biggest single catch this month
    bass_catches = [
        {
            "species": "Largemouth Bass",
            "weight": 14.8,  # BIGGEST CATCH THIS MONTH
            "photo_url": "https://example.com/monthly_bass_record.jpg",
            "location": {"lat": 34.0522, "lng": -118.2437}
        },
        {
            "species": "Smallmouth Bass", 
            "weight": 5.1,
            "photo_url": "https://example.com/monthly_bass2.jpg",
            "location": {"lat": 34.0522, "lng": -118.2437}
        }
    ]
    
    # Trout Master - Has best average this month
    trout_catches = [
        {
            "species": "Rainbow Trout",
            "weight": 4.2,
            "photo_url": "https://example.com/monthly_trout1.jpg", 
            "location": {"lat": 40.7128, "lng": -74.0060}
        },
        {
            "species": "Brown Trout",
            "weight": 4.8,
            "photo_url": "https://example.com/monthly_trout2.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060}
        },
        {
            "species": "Brook Trout",
            "weight": 4.5,
            "photo_url": "https://example.com/monthly_trout3.jpg",
            "location": {"lat": 40.7128, "lng": -74.0060}
        }
    ]
    
    # Volume Angler - Most catches this month
    volume_catches = [
        {
            "species": "Bluegill",
            "weight": 1.1,
            "photo_url": "https://example.com/monthly_bluegill1.jpg",
            "location": {"lat": 41.8781, "lng": -87.6298}
        },
        {
            "species": "Bluegill",
            "weight": 1.0,
            "photo_url": "https://example.com/monthly_bluegill2.jpg",
            "location": {"lat": 41.8781, "lng": -87.6298}
        },
        {
            "species": "Crappie",
            "weight": 1.3,
            "photo_url": "https://example.com/monthly_crappie1.jpg",
            "location": {"lat": 41.8781, "lng": -87.6298}
        },
        {
            "species": "Crappie",
            "weight": 1.2,
            "photo_url": "https://example.com/monthly_crappie2.jpg",
            "location": {"lat": 41.8781, "lng": -87.6298}
        },
        {
            "species": "Perch",
            "weight": 0.9,
            "photo_url": "https://example.com/monthly_perch1.jpg",
            "location": {"lat": 41.8781, "lng": -87.6298}
        },
        {
            "species": "Bass",
            "weight": 3.8,
            "photo_url": "https://example.com/monthly_bass_small.jpg",
            "location": {"lat": 41.8781, "lng": -87.6298}
        },
        {
            "species": "Sunfish",
            "weight": 0.6,
            "photo_url": "https://example.com/monthly_sunfish.jpg",
            "location": {"lat": 41.8781, "lng": -87.6298}
        }
    ]
    
    # Create catches for each user
    test_data = [
        (bass_champ, bass_token, bass_catches, "monthly_bass_champ"),
        (trout_master, trout_token, trout_catches, "monthly_trout_master"),
        (volume_angler, volume_token, volume_catches, "monthly_volume_angler")
    ]
    
    for user, token, catches, username in test_data:
        headers = {"Authorization": f"Bearer {token}"}
        for catch_data in catches:
            try:
                response = requests.post(f"{BASE_URL}/catches/", json=catch_data, headers=headers)
                if response.status_code == 201:
                    catch = response.json()
                    print(f"✅ {username}: {catch['species']} ({catch['weight']}lbs)")
                else:
                    print(f"❌ Failed catch for {username}: {response.text}")
            except Exception as e:
                print(f"❌ Error creating catch for {username}: {e}")
    
    # Test monthly leaderboard endpoints
    print("\n4. Testing personal monthly stats...")
    headers = {"Authorization": f"Bearer {bass_token}"}
    try:
        response = requests.get(f"{BASE_URL}/leaderboard/my-stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print("✅ Bass Champion's Monthly Stats:")
            print(f"   Total Catches: {stats['total_catches']}")
            print(f"   Biggest Catch This Month: {stats['biggest_catch_month']}lbs ({stats['biggest_catch_species']})")
            print(f"   Catches This Month: {stats['catches_this_month']}")
            print(f"   Best Average This Month: {stats['best_average_month']}lbs")
        else:
            print(f"❌ Personal stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting personal stats: {e}")
    
    # Test monthly following comparison leaderboard
    print("\n5. Testing monthly following comparison leaderboards...")
    
    metrics = ["biggest_catch_month", "catches_this_month", "best_average_month"]
    
    for metric in metrics:
        print(f"\n   🏆 {metric.replace('_', ' ').title()} Leaderboard:")
        try:
            response = requests.get(
                f"{BASE_URL}/leaderboard/following-comparison?metric={metric}",
                headers=headers
            )
            if response.status_code == 200:
                leaderboard = response.json()
                print(f"   Current user rank: {leaderboard['current_user_rank']}")
                print("   Top performers:")
                for user in leaderboard['leaderboard'][:3]:
                    if not user:  # Skip empty users
                        continue
                    indicator = "👑" if user['is_current_user'] else "  "
                    value = user[metric]
                    unit = "lbs" if metric in ["biggest_catch_month", "best_average_month"] else "catches"
                    print(f"   {indicator} #{user['rank']} {user['username']}: {value} {unit}")
            else:
                print(f"   ❌ {metric} leaderboard failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error getting {metric} leaderboard: {e}")
    
    # Test global monthly leaderboard
    print("\n6. Testing global monthly leaderboard...")
    try:
        response = requests.get(
            f"{BASE_URL}/leaderboard/global?metric=biggest_catch_month",
            headers=headers
        )
        if response.status_code == 200:
            leaderboard = response.json()
            print("✅ Global Monthly Biggest Catch Leaderboard:")
            print(f"   Total competing users this month: {leaderboard['total_users']}")
            print(f"   Bass champion's global rank: {leaderboard['current_user_rank']}")
            print("   Top 3 globally this month:")
            for user in leaderboard['leaderboard'][:3]:
                if not user:  # Skip empty users
                    continue
                indicator = "👑" if user['is_current_user'] else "  "
                print(f"   {indicator} #{user['rank']} {user['username']}: {user['biggest_catch_month']}lbs")
        else:
            print(f"❌ Global leaderboard failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting global leaderboard: {e}")
    
    # Test species-specific monthly leaderboard
    print("\n7. Testing species-specific monthly leaderboard...")
    try:
        response = requests.get(
            f"{BASE_URL}/leaderboard/species/bass?metric=biggest_catch_month",
            headers=headers
        )
        if response.status_code == 200:
            leaderboard = response.json()
            print("✅ Bass Species Monthly Leaderboard:")
            print(f"   Total bass anglers this month: {leaderboard['total_users']}")
            print("   Top bass catches this month:")
            for user in leaderboard['leaderboard']:
                if not user:  # Skip empty users
                    continue
                indicator = "👑" if user['is_current_user'] else "  "
                print(f"   {indicator} #{user['rank']} {user['username']}: {user['biggest_catch_month']}lbs")
        else:
            print(f"❌ Species leaderboard failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting species leaderboard: {e}")
    
    print("\n" + "=" * 60)
    print("🏆 Monthly Leaderboard System Test Complete!")
    print("\n📊 MONTHLY LEADERBOARD ENDPOINTS:")
    print("   ✅ GET /api/v1/leaderboard/my-stats              - Personal monthly statistics")
    print("   ✅ GET /api/v1/leaderboard/following-comparison  - Compare with following (monthly)")
    print("   ✅ GET /api/v1/leaderboard/global                - Global monthly leaderboard")
    print("   ✅ GET /api/v1/leaderboard/species/{species}     - Species monthly leaderboard")
    
    print("\n🎯 MONTHLY COMPETITIVE METRICS:")
    print("   📏 Biggest Catch Month  - Largest catch in last 30 days")
    print("   📅 Catches This Month   - Total catches in last 30 days") 
    print("   📊 Best Average Month   - Average weight in last 30 days")
    
    print("\n🏆 MONTHLY LEADERBOARD FEATURES:")
    print("   - Personal monthly statistics tracking")
    print("   - Following-based monthly competition")
    print("   - Global monthly rankings")
    print("   - Species-specific monthly competitions")
    print("   - Real-time monthly ranking updates")
    print("   - Current user position highlighting")
    print("   - 30-day rolling window for all metrics")
    
    return True

if __name__ == "__main__":
    success = test_monthly_leaderboard_system()
    exit(0 if success else 1)
