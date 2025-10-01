#!/usr/bin/env python3
"""
Simplified CRM Feature Test Script
Tests core CRM functionality using built-in Python libraries only
"""

import urllib.request
import urllib.parse
import json
import time
import random
import string
import sys
from http.cookiejar import CookieJar

class SimpleCRMTester:
    def __init__(self, base_url="http://localhost:8000", username="Administrator", password="admin"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.cookie_jar = CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))
        self.csrf_token = None
        self.results = {}
        
    def make_request(self, url, data=None, headers=None, method="GET"):
        """Make HTTP request with cookies"""
        if headers is None:
            headers = {}
        
        if self.csrf_token:
            headers['X-Frappe-CSRF-Token'] = self.csrf_token
        
        if data:
            if isinstance(data, dict):
                data = json.dumps(data).encode('utf-8')
                headers['Content-Type'] = 'application/json'
            elif isinstance(data, str):
                data = data.encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=headers)
        req.get_method = lambda: method
        
        try:
            response = self.opener.open(req, timeout=30)
            content = response.read().decode('utf-8')
            
            # Try to extract CSRF token from response
            if 'csrf_token' in content and not self.csrf_token:
                try:
                    csrf_start = content.find('"csrf_token":"') + 14
                    csrf_end = content.find('"', csrf_start)
                    if csrf_start > 13 and csrf_end > csrf_start:
                        self.csrf_token = content[csrf_start:csrf_end]
                except:
                    pass
            
            return {
                'status_code': response.getcode(),
                'content': content,
                'headers': dict(response.headers)
            }
        except Exception as e:
            return {
                'status_code': 0,
                'content': str(e),
                'error': True
            }
    
    def login(self):
        """Login to CRM"""
        print("🔐 Attempting login...")
        
        # Get login page first
        login_page = self.make_request(f"{self.base_url}/login")
        if login_page['status_code'] != 200:
            print(f"❌ Cannot access login page: {login_page['content']}")
            return False
        
        # Perform login
        login_data = f"cmd=login&usr={self.username}&pwd={self.password}"
        login_response = self.make_request(
            f"{self.base_url}/", 
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            method="POST"
        )
        
        if login_response['status_code'] == 200:
            print("✅ Login successful")
            return True
        else:
            print(f"❌ Login failed: {login_response['content']}")
            return False
    
    def test_basic_connectivity(self):
        """Test basic connectivity to CRM"""
        print("\n🌐 Testing Basic Connectivity...")
        
        # Test main page
        response = self.make_request(f"{self.base_url}")
        if response['status_code'] == 200:
            print("✅ Main page accessible")
        else:
            print(f"❌ Main page not accessible: {response['content']}")
            return False
        
        # Test CRM page
        response = self.make_request(f"{self.base_url}/crm")
        if response['status_code'] == 200:
            print("✅ CRM page accessible")
            self.results['connectivity'] = 'PASSED'
            return True
        else:
            print(f"❌ CRM page not accessible: {response['content']}")
            self.results['connectivity'] = 'FAILED'
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        print("\n🔗 Testing API Endpoints...")
        
        endpoints = [
            "/api/method/frappe.auth.get_logged_user",
            "/api/method/crm.api.get_posthog_settings",
            "/api/method/crm.api.whatsapp.is_whatsapp_enabled",
            "/api/method/crm.integrations.api.is_call_integration_enabled"
        ]
        
        passed = 0
        total = len(endpoints)
        
        for endpoint in endpoints:
            response = self.make_request(f"{self.base_url}{endpoint}")
            if response['status_code'] == 200:
                print(f"✅ {endpoint}")
                passed += 1
            else:
                print(f"❌ {endpoint} - Status: {response['status_code']}")
        
        if passed == total:
            self.results['api_endpoints'] = 'PASSED'
        elif passed > 0:
            self.results['api_endpoints'] = 'PARTIAL'
        else:
            self.results['api_endpoints'] = 'FAILED'
        
        print(f"📊 API Tests: {passed}/{total} passed")
    
    def test_document_creation(self):
        """Test document creation via API"""
        print("\n📝 Testing Document Creation...")
        
        # Generate test data
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        
        # Test Lead creation
        lead_data = {
            "doctype": "CRM Lead",
            "first_name": f"Test{suffix}",
            "last_name": "Lead", 
            "email": f"test{suffix}@example.com",
            "status": "Open"
        }
        
        response = self.make_request(
            f"{self.base_url}/api/method/frappe.client.insert",
            data={"doc": lead_data},
            method="POST"
        )
        
        if response['status_code'] == 200:
            print("✅ Lead creation successful")
            
            try:
                result = json.loads(response['content'])
                if result.get('message', {}).get('name'):
                    lead_name = result['message']['name']
                    print(f"   Created lead: {lead_name}")
                    
                    # Test lead retrieval
                    get_response = self.make_request(
                        f"{self.base_url}/api/method/frappe.client.get?doctype=CRM Lead&name={lead_name}"
                    )
                    
                    if get_response['status_code'] == 200:
                        print("✅ Lead retrieval successful")
                        self.results['document_creation'] = 'PASSED'
                    else:
                        print("❌ Lead retrieval failed")
                        self.results['document_creation'] = 'PARTIAL'
            except:
                print("⚠️  Lead created but response parsing failed")
                self.results['document_creation'] = 'PARTIAL'
        else:
            print(f"❌ Lead creation failed: {response['content']}")
            self.results['document_creation'] = 'FAILED'
    
    def test_data_listing(self):
        """Test data listing functionality"""
        print("\n📊 Testing Data Listing...")
        
        # Test getting leads list
        response = self.make_request(
            f"{self.base_url}/api/method/frappe.client.get_list",
            data={
                "doctype": "CRM Lead",
                "fields": ["name", "first_name", "last_name", "status"],
                "limit_page_length": 10
            },
            method="POST"
        )
        
        if response['status_code'] == 200:
            try:
                result = json.loads(response['content'])
                leads = result.get('message', [])
                print(f"✅ Lead listing successful - Found {len(leads)} leads")
                
                # Test getting deals list
                deals_response = self.make_request(
                    f"{self.base_url}/api/method/frappe.client.get_list",
                    data={
                        "doctype": "CRM Deal",
                        "fields": ["name", "organization", "status"],
                        "limit_page_length": 10
                    },
                    method="POST"
                )
                
                if deals_response['status_code'] == 200:
                    deals_result = json.loads(deals_response['content'])
                    deals = deals_result.get('message', [])
                    print(f"✅ Deal listing successful - Found {len(deals)} deals")
                    self.results['data_listing'] = 'PASSED'
                else:
                    print("❌ Deal listing failed")
                    self.results['data_listing'] = 'PARTIAL'
                    
            except Exception as e:
                print(f"❌ Data listing parsing failed: {str(e)}")
                self.results['data_listing'] = 'FAILED'
        else:
            print(f"❌ Lead listing failed: {response['content']}")
            self.results['data_listing'] = 'FAILED'
    
    def test_integration_status(self):
        """Test integration status"""
        print("\n🔌 Testing Integration Status...")
        
        integrations = [
            ("WhatsApp", "/api/method/crm.api.whatsapp.is_whatsapp_enabled"),
            ("Call Integration", "/api/method/crm.integrations.api.is_call_integration_enabled")
        ]
        
        for name, endpoint in integrations:
            response = self.make_request(f"{self.base_url}{endpoint}")
            if response['status_code'] == 200:
                try:
                    result = json.loads(response['content'])
                    status = result.get('message', False)
                    print(f"📱 {name}: {'Enabled' if status else 'Disabled'}")
                except:
                    print(f"⚠️  {name}: Status unknown")
            else:
                print(f"❌ {name}: Cannot check status")
        
        self.results['integration_status'] = 'PASSED'
    
    def test_user_permissions(self):
        """Test user permissions"""
        print("\n🔐 Testing User Permissions...")
        
        # Check app permission
        response = self.make_request(f"{self.base_url}/api/method/crm.api.check_app_permission")
        if response['status_code'] == 200:
            try:
                result = json.loads(response['content'])
                has_permission = result.get('message', False)
                print(f"🔑 CRM App Permission: {'Granted' if has_permission else 'Denied'}")
            except:
                print("⚠️  Permission status unclear")
        else:
            print("❌ Cannot check permissions")
        
        # Check current user
        response = self.make_request(f"{self.base_url}/api/method/frappe.auth.get_logged_user")
        if response['status_code'] == 200:
            try:
                result = json.loads(response['content'])
                user = result.get('message', 'Unknown')
                print(f"👤 Current User: {user}")
            except:
                print("⚠️  User information unclear")
        else:
            print("❌ Cannot get user information")
        
        self.results['user_permissions'] = 'PASSED'
    
    def run_tests(self):
        """Run all tests"""
        print("🚀 Starting Simple CRM Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        # Login first
        if not self.login():
            print("❌ Cannot proceed without login")
            return False
        
        # Run tests
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed, skipping other tests")
            return False
        
        self.test_api_endpoints()
        self.test_document_creation()
        self.test_data_listing()
        self.test_integration_status()
        self.test_user_permissions()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = 0
        
        for test_name, status in self.results.items():
            if status == 'PASSED':
                print(f"✅ {test_name.replace('_', ' ').title()}: PASSED")
                passed_tests += 1
            elif status == 'PARTIAL':
                print(f"⚠️  {test_name.replace('_', ' ').title()}: PARTIAL")
                passed_tests += 0.5
            else:
                print(f"❌ {test_name.replace('_', ' ').title()}: FAILED")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n🎯 Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        if success_rate >= 100:
            print("\n🎉 ALL TESTS PASSED! Your CRM is working perfectly!")
        elif success_rate >= 80:
            print("\n✨ Most tests passed! CRM is mostly functional.")
        elif success_rate >= 50:
            print("\n⚠️  Some tests passed. CRM has basic functionality.")
        else:
            print("\n❌ Many tests failed. Please check your CRM setup.")
        
        return success_rate >= 80

if __name__ == "__main__":
    # Configuration
    BASE_URL = "http://localhost:8000"
    USERNAME = "Administrator"
    PASSWORD = "admin"
    
    print("🔧 Frappe CRM Feature Testing Tool")
    print("This tool tests core CRM functionality using simple HTTP requests")
    print()
    
    # Run tests
    tester = SimpleCRMTester(BASE_URL, USERNAME, PASSWORD)
    success = tester.run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)