#!/usr/bin/env python3
"""
Test script for admissions API endpoints
Run this after integrating the admissions endpoints into your backend

Usage:
    python test_admissions_api.py
"""

import requests
import json
from typing import Optional

# Configuration
API_BASE_URL = "http://localhost:8000"  # Change this to your API URL
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjIwOTEwNDUsInN1YiI6IjIifQ.zZJmgXkx5pPV7p2smfeDmxB8pihB447CIUpy27jhDdk"

# Headers with authentication
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def test_health():
    """Test if API is running"""
    print("=" * 60)
    print("Testing API Health...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API is not running or not reachable: {e}")
        return False


def get_sample_ipeds_id():
    """Get a sample IPEDS ID from the institutions endpoint"""
    print("\n" + "=" * 60)
    print("Getting sample institution IPEDS ID...")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/institutions/",
            params={"limit": 1},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("institutions") and len(data["institutions"]) > 0:
                ipeds_id = data["institutions"][0]["ipeds_id"]
                name = data["institutions"][0]["name"]
                print(f"✓ Found institution: {name}")
                print(f"✓ IPEDS ID: {ipeds_id}")
                return ipeds_id
        
        print("⚠ No institutions found, using default IPEDS ID: 166027")
        return 166027
        
    except Exception as e:
        print(f"⚠ Could not fetch institutions: {e}")
        print("Using default IPEDS ID: 166027")
        return 166027


def test_latest_admissions(ipeds_id: int):
    """Test GET /api/v1/admissions/institution/{ipeds_id}"""
    print("\n" + "=" * 60)
    print(f"Testing: GET /api/v1/admissions/institution/{ipeds_id}")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/admissions/institution/{ipeds_id}",
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ SUCCESS! Admissions data retrieved:")
            print(json.dumps(data, indent=2))
            
            # Highlight key fields
            print("\n📊 Key Statistics:")
            if data.get("acceptance_rate"):
                print(f"  • Acceptance Rate: {data['acceptance_rate']}%")
            if data.get("applications_total"):
                print(f"  • Total Applications: {data['applications_total']:,}")
            if data.get("sat_reading_25th") and data.get("sat_reading_75th"):
                print(f"  • SAT Reading Range: {data['sat_reading_25th']}-{data['sat_reading_75th']}")
            if data.get("sat_math_25th") and data.get("sat_math_75th"):
                print(f"  • SAT Math Range: {data['sat_math_25th']}-{data['sat_math_75th']}")
            if data.get("academic_year"):
                print(f"  • Academic Year: {data['academic_year']}")
            
            return True
            
        elif response.status_code == 404:
            print("❌ NOT FOUND: No admissions data exists for this institution")
            print(f"Response: {response.json()}")
            return False
            
        else:
            print(f"❌ ERROR: Unexpected status code")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Cannot reach API")
        print("Make sure your backend is running!")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_all_years_admissions(ipeds_id: int):
    """Test GET /api/v1/admissions/institution/{ipeds_id}/all"""
    print("\n" + "=" * 60)
    print(f"Testing: GET /api/v1/admissions/institution/{ipeds_id}/all")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/admissions/institution/{ipeds_id}/all",
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ SUCCESS! Found {len(data)} years of admissions data")
            
            if data:
                print("\n📅 Available Years:")
                for record in data:
                    year = record.get("academic_year", "Unknown")
                    acceptance = record.get("acceptance_rate", "N/A")
                    print(f"  • {year}: {acceptance}% acceptance rate")
            
            return True
            
        elif response.status_code == 404:
            print("❌ NOT FOUND: No admissions data exists for this institution")
            return False
            
        else:
            print(f"❌ ERROR: Unexpected status code")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_specific_year_admissions(ipeds_id: int, academic_year: str = "2023-24"):
    """Test GET /api/v1/admissions/institution/{ipeds_id}/year/{academic_year}"""
    print("\n" + "=" * 60)
    print(f"Testing: GET /api/v1/admissions/institution/{ipeds_id}/year/{academic_year}")
    print("=" * 60)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/admissions/institution/{ipeds_id}/year/{academic_year}",
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ SUCCESS! Retrieved admissions data for {academic_year}")
            print(json.dumps(data, indent=2))
            return True
            
        elif response.status_code == 404:
            print(f"❌ NOT FOUND: No admissions data for {academic_year}")
            return False
            
        else:
            print(f"❌ ERROR: Unexpected status code")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def check_endpoint_exists():
    """Check if the admissions endpoint is registered"""
    print("\n" + "=" * 60)
    print("Checking if admissions endpoint is registered...")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/routes-simple", timeout=5)
        if response.status_code == 200:
            routes = response.text
            if "/api/v1/admissions" in routes:
                print("✓ Admissions endpoint is registered!")
                return True
            else:
                print("❌ Admissions endpoint NOT found in routes")
                print("\nYou need to:")
                print("1. Add app/services/admissions.py")
                print("2. Add app/api/v1/admissions.py")
                print("3. Register the router in app/main.py")
                print("\nSee INTEGRATION_INSTRUCTIONS_V2.md for details")
                return False
    except Exception as e:
        print(f"Could not check routes: {e}")
        return False


def main():
    """Run all tests"""
    print("\n🚀 ADMISSIONS API TEST SUITE")
    print("=" * 60)
    
    # Test 1: Check if API is running
    if not test_health():
        print("\n❌ CANNOT PROCEED: API is not running")
        print("\nTo start your API:")
        print("  cd college-backend")
        print("  source venv/bin/activate")
        print("  uvicorn app.main:app --reload")
        return
    
    # Test 2: Check if endpoint is registered
    endpoint_exists = check_endpoint_exists()
    
    # Test 3: Get a sample IPEDS ID
    ipeds_id = get_sample_ipeds_id()
    
    # Test 4-6: Test the admissions endpoints
    if endpoint_exists:
        test_latest_admissions(ipeds_id)
        test_all_years_admissions(ipeds_id)
        test_specific_year_admissions(ipeds_id)
    else:
        print("\n⚠ Skipping admissions tests - endpoint not registered yet")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    if endpoint_exists:
        print("✓ API is running")
        print("✓ Admissions endpoint is registered")
        print("\nNext steps:")
        print("1. Check if you have data in the admissions_data table")
        print("2. Update your frontend to use the new endpoint")
        print("3. Test with real IPEDS IDs from your database")
    else:
        print("⚠ Admissions endpoint needs to be integrated")
        print("\nFollow the steps in INTEGRATION_INSTRUCTIONS_V2.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
