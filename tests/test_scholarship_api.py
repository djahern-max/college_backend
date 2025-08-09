"""
Comprehensive test suite for Scholarship API endpoints.
Save this as: tests/test_scholarship_api.py
"""
import requests
import json
from typing import Dict, Any, Optional, List
import time


class ScholarshipAPITester:
    """Test class for scholarship API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1", token: Optional[str] = None):
        self.base_url = base_url
        self.token = token
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
        self.results = []
    
    def log_result(self, test_name: str, success: bool, response_data: Any = None, error: str = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "data": response_data,
            "error": error
        }
        self.results.append(result)
        
        # Print immediate feedback
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if error:
            print(f"    Error: {error}")
        if response_data and isinstance(response_data, dict):
            if 'total_count' in response_data:
                print(f"    Results: {response_data['total_count']} scholarships found")
            elif 'total_scholarships' in response_data:
                print(f"    Statistics: {response_data['total_scholarships']} total scholarships")
        print()
    
    def test_get_active_scholarships(self):
        """Test GET /scholarships/active"""
        try:
            response = requests.get(f"{self.base_url}/scholarships/active", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Get Active Scholarships", True, {"count": len(data), "sample": data[0] if data else None})
                return data
            else:
                self.log_result("Get Active Scholarships", False, error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Get Active Scholarships", False, error=str(e))
    
    def test_get_statistics(self):
        """Test GET /scholarships/statistics (requires auth)"""
        try:
            auth_headers = self.headers.copy()
            if not self.token:
                self.log_result("Get Statistics", False, error="No authentication token provided")
                return
                
            response = requests.get(f"{self.base_url}/scholarships/statistics", headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Get Statistics", True, data)
                return data
            else:
                self.log_result("Get Statistics", False, error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Get Statistics", False, error=str(e))
    
    def test_search_basic_query(self):
        """Test basic search functionality"""
        try:
            response = requests.get(f"{self.base_url}/scholarships/search?query=engineering", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Search - Basic Query (engineering)", True, data)
                return data
            else:
                self.log_result("Search - Basic Query", False, error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Search - Basic Query", False, error=str(e))
    
    def test_search_amount_filter(self):
        """Test amount filtering"""
        try:
            response = requests.get(
                f"{self.base_url}/scholarships/search?min_amount=3000&max_amount=6000", 
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Search - Amount Filter ($3000-$6000)", True, data)
                return data
            else:
                self.log_result("Search - Amount Filter", False, error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Search - Amount Filter", False, error=str(e))
    
    def test_search_scholarship_type(self):
        """Test scholarship type filtering"""
        try:
            response = requests.get(
                f"{self.base_url}/scholarships/search?scholarship_type=merit", 
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Search - Merit Type Filter", True, data)
                return data
            else:
                self.log_result("Search - Merit Type Filter", False, error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Search - Merit Type Filter", False, error=str(e))
    
    def test_search_categories(self):
        """Test category filtering"""
        try:
            response = requests.get(
                f"{self.base_url}/scholarships/search?categories=business,leadership", 
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Search - Categories (business, leadership)", True, data)
                return data
            else:
                self.log_result("Search - Categories", False, error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Search - Categories", False, error=str(e))
    
    def test_search_renewable_only(self):
        """Test renewable scholarship filtering"""
        try:
            response = requests.get(
                f"{self.base_url}/scholarships/search?renewable_only=true", 
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                renewable_count = len([s for s in data.get('scholarships', []) if s.get('renewable')])
                self.log_result("Search - Renewable Only", True, {**data, "renewable_count": renewable_count})
                return data
            else:
                self.log_result("Search - Renewable Only", False, error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Search - Renewable Only", False, error=str(e))
    
    def test_search_pagination(self):
        """Test search pagination"""
        try:
            response = requests.get(
                f"{self.base_url}/scholarships/search?skip=2&limit=3&sort_by=title&sort_order=asc", 
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Search - Pagination (skip: 2, limit: 3)", True, data)
                return data
            else:
                self.log_result("Search - Pagination", False, error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Search - Pagination", False, error=str(e))
    
    def test_get_by_provider(self):
        """Test get scholarships by provider"""
        try:
            response = requests.get(
                f"{self.base_url}/scholarships/provider/Foundation", 
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Get by Provider (Foundation)", True, {"count": len(data)})
                return data
            else:
                self.log_result("Get by Provider", False, error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Get by Provider", False, error=str(e))
    
    def test_get_expiring_soon(self):
        """Test get scholarships expiring soon"""
        try:
            response = requests.get(
                f"{self.base_url}/scholarships/expiring-soon?days=90", 
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_result("Get Expiring Soon (90 days)", True, {"count": len(data)})
                return data
            else:
                self.log_result("Get Expiring Soon", False, error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Get Expiring Soon", False, error=str(e))
    
    def get_available_scholarship_ids(self) -> List[int]:
        """Get list of available scholarship IDs"""
        try:
            response = requests.get(f"{self.base_url}/scholarships/active", headers=self.headers)
            if response.status_code == 200:
                scholarships = response.json()
                return [s['id'] for s in scholarships if 'id' in s]
            return []
        except:
            return []
    
    def test_get_specific_scholarship(self, scholarship_id: int = None):
        """Test get specific scholarship by ID"""
        # If no ID provided, get the first available one
        if scholarship_id is None:
            available_ids = self.get_available_scholarship_ids()
            if not available_ids:
                self.log_result("Get Specific Scholarship", False, error="No scholarships available")
                return
            scholarship_id = available_ids[0]
        
        try:
            response = requests.get(f"{self.base_url}/scholarships/{scholarship_id}", headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(f"Get Scholarship ID {scholarship_id}", True, {"title": data.get("title")})
                return data
            elif response.status_code == 404:
                self.log_result(f"Get Scholarship ID {scholarship_id}", False, error="Scholarship not found")
            else:
                self.log_result(f"Get Scholarship ID {scholarship_id}", False, error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result(f"Get Scholarship ID {scholarship_id}", False, error=str(e))
    
    def test_record_application(self, scholarship_id: int = None):
        """Test recording an application (requires auth)"""
        # If no ID provided, get the first available one
        if scholarship_id is None:
            available_ids = self.get_available_scholarship_ids()
            if not available_ids:
                self.log_result("Record Application", False, error="No scholarships available")
                return
            scholarship_id = available_ids[0]
        
        try:
            if not self.token:
                self.log_result("Record Application", False, error="No authentication token provided")
                return
                
            auth_headers = self.headers.copy()
            response = requests.post(f"{self.base_url}/scholarships/{scholarship_id}/apply", headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(f"Record Application (ID {scholarship_id})", True, data)
                return data
            else:
                self.log_result("Record Application", False, error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Record Application", False, error=str(e))
    
    def test_verify_scholarship(self, scholarship_id: int = None):
        """Test verifying a scholarship (requires auth)"""
        # If no ID provided, get the second available one (to avoid conflicts)
        if scholarship_id is None:
            available_ids = self.get_available_scholarship_ids()
            if len(available_ids) < 2:
                self.log_result("Verify Scholarship", False, error="Need at least 2 scholarships available")
                return
            scholarship_id = available_ids[1]  # Use second scholarship
        
        try:
            if not self.token:
                self.log_result("Verify Scholarship", False, error="No authentication token provided")
                return
                
            auth_headers = self.headers.copy()
            response = requests.post(f"{self.base_url}/scholarships/{scholarship_id}/verify", headers=auth_headers)
            
            if response.status_code == 200:
                data = response.json()
                self.log_result(f"Verify Scholarship (ID {scholarship_id})", True, {"verified": data.get("verified")})
                return data
            else:
                self.log_result("Verify Scholarship", False, error=f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Verify Scholarship", False, error=str(e))
    
    def test_create_scholarship(self):
        """Test creating a new scholarship (requires auth)"""
        test_scholarship = {
            "title": "Python API Test Scholarship",
            "description": "Test scholarship created via Python API test",
            "provider": "Test Organization",
            "amount_exact": 1500,
            "renewable": False,
            "deadline": "2024-12-31",
            "scholarship_type": "merit",
            "categories": ["test", "api"],
            "keywords": ["test", "python", "api"]
        }
        
        try:
            if not self.token:
                self.log_result("Create Scholarship", False, error="No authentication token provided")
                return
                
            auth_headers = self.headers.copy()
            response = requests.post(
                f"{self.base_url}/scholarships/", 
                headers=auth_headers,
                json=test_scholarship
            )
            
            if response.status_code == 201:
                data = response.json()
                self.log_result("Create Scholarship", True, {"id": data.get("id"), "title": data.get("title")})
                return data
            else:
                self.log_result("Create Scholarship", False, error=f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Create Scholarship", False, error=str(e))
    
    def run_all_tests(self):
        """Run all test methods"""
        print("=" * 60)
        print("STARTING SCHOLARSHIP API TESTS")
        print("=" * 60)
        print()
        
        # Test public endpoints first
        self.test_get_active_scholarships()
        self.test_search_basic_query()
        self.test_search_amount_filter()
        self.test_search_scholarship_type()
        self.test_search_categories()
        self.test_search_renewable_only()
        self.test_search_pagination()
        self.test_get_by_provider()
        self.test_get_expiring_soon()
        self.test_get_specific_scholarship()  # Will auto-discover ID
        self.test_get_specific_scholarship()  # Test second scholarship
        
        # Test authenticated endpoints
        if self.token:
            print("-" * 40)
            print("TESTING AUTHENTICATED ENDPOINTS")
            print("-" * 40)
            print()
            
            self.test_get_statistics()
            self.test_record_application()  # Will auto-discover ID
            self.test_verify_scholarship()  # Will auto-discover ID
            self.test_create_scholarship()
            
            # Get updated statistics
            print("Getting updated statistics after modifications...")
            self.test_get_statistics()
        else:
            print("⚠️  Skipping authenticated tests - no token provided")
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")
        
        if failed_tests > 0:
            print("\nFailed Tests:")
            for result in self.results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['error']}")
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    # Your token here
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTQ3NDE2MDksInN1YiI6IjQifQ.wn6kNZVqfc5ooEaTT5Ae_5cx1pqWu5pohchC-PvFjt8"
    
    # Create tester instance
    tester = ScholarshipAPITester(token=TOKEN)
    
    # Run all tests
    tester.run_all_tests()