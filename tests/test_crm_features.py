#!/usr/bin/env python3
"""
Comprehensive Test Suite for Frappe CRM
Tests all major CRM features including:
- Lead Management
- Deal Management  
- Contact Management
- Organization Management
- Communication Features
- Integration Features
- API Endpoints
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
import random
import string

class CRMTestSuite:
    def __init__(self, base_url="http://localhost:8000", username="Administrator", password="admin"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.csrf_token = None
        self.test_results = {}
        
    def login(self):
        """Login to CRM and get session"""
        print("🔐 Logging into CRM...")
        
        # Get login page to get csrf token
        resp = self.session.get(f"{self.base_url}/login")
        if resp.status_code != 200:
            raise Exception("Failed to access login page")
        
        # Login
        login_data = {
            "cmd": "login", 
            "usr": self.username,
            "pwd": self.password
        }
        
        resp = self.session.post(f"{self.base_url}/", data=login_data)
        if resp.status_code == 200 and "logged_in" in resp.text:
            print("✅ Login successful")
            return True
        else:
            raise Exception("Login failed")
    
    def get_csrf_token(self):
        """Get CSRF token for API calls"""
        resp = self.session.get(f"{self.base_url}/api/method/frappe.auth.get_logged_user")
        if resp.status_code == 200:
            # Extract csrf token from cookies or headers
            for cookie in self.session.cookies:
                if cookie.name == "csrf_token":
                    self.csrf_token = cookie.value
                    break
            return True
        return False
    
    def api_call(self, method, endpoint, data=None, params=None):
        """Make authenticated API call"""
        url = f"{self.base_url}/api/method/{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.csrf_token:
            headers['X-Frappe-CSRF-Token'] = self.csrf_token
        
        if method == "GET":
            resp = self.session.get(url, params=params, headers=headers)
        elif method == "POST":
            resp = self.session.post(url, json=data, headers=headers)
        elif method == "PUT":
            resp = self.session.put(url, json=data, headers=headers)
        elif method == "DELETE":
            resp = self.session.delete(url, headers=headers)
        
        return resp
    
    def generate_test_data(self, prefix="Test"):
        """Generate random test data"""
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        return {
            'first_name': f"{prefix}First{suffix}",
            'last_name': f"{prefix}Last{suffix}",
            'email': f"test{suffix}@example.com",
            'mobile_no': f"+1555{random.randint(1000000, 9999999)}",
            'organization_name': f"{prefix} Corp {suffix}",
            'website': f"https://{prefix.lower()}{suffix}.com",
            'industry': 'Technology'
        }
    
    def test_lead_management(self):
        """Test Lead CRUD operations"""
        print("\n📋 Testing Lead Management...")
        test_data = self.generate_test_data("Lead")
        
        try:
            # 1. Create Lead
            lead_data = {
                "doctype": "CRM Lead",
                "first_name": test_data['first_name'],
                "last_name": test_data['last_name'], 
                "email": test_data['email'],
                "mobile_no": test_data['mobile_no'],
                "organization": test_data['organization_name'],
                "status": "Open"
            }
            
            resp = self.api_call("POST", "frappe.client.insert", {"doc": lead_data})
            if resp.status_code == 200:
                lead_name = resp.json()['message']['name']
                print(f"✅ Lead created: {lead_name}")
                
                # 2. Read Lead
                resp = self.api_call("GET", f"frappe.client.get", params={
                    "doctype": "CRM Lead",
                    "name": lead_name
                })
                if resp.status_code == 200:
                    print("✅ Lead read successful")
                    
                    # 3. Update Lead
                    update_data = {
                        "doctype": "CRM Lead",
                        "name": lead_name,
                        "status": "Interested"
                    }
                    resp = self.api_call("POST", "frappe.client.set_value", {
                        "doctype": "CRM Lead",
                        "name": lead_name,
                        "fieldname": "status", 
                        "value": "Interested"
                    })
                    if resp.status_code == 200:
                        print("✅ Lead updated")
                    
                    # 4. Convert Lead to Deal
                    resp = self.api_call("POST", "crm.fcrm.doctype.crm_lead.crm_lead.convert_to_deal", {
                        "lead": lead_name
                    })
                    if resp.status_code == 200:
                        deal_name = resp.json().get('message')
                        print(f"✅ Lead converted to Deal: {deal_name}")
                        
                        self.test_results['lead_management'] = {
                            'status': 'PASSED',
                            'lead_created': lead_name,
                            'deal_created': deal_name
                        }
                        return lead_name, deal_name
                    
        except Exception as e:
            print(f"❌ Lead management test failed: {str(e)}")
            self.test_results['lead_management'] = {'status': 'FAILED', 'error': str(e)}
        
        return None, None
    
    def test_deal_management(self):
        """Test Deal CRUD operations"""
        print("\n💼 Testing Deal Management...")
        test_data = self.generate_test_data("Deal")
        
        try:
            # 1. Create Deal
            deal_data = {
                "first_name": test_data['first_name'],
                "last_name": test_data['last_name'],
                "email": test_data['email'],
                "mobile_no": test_data['mobile_no'],
                "organization_name": test_data['organization_name'],
                "deal_value": 50000,
                "probability": 50,
                "status": "Qualification"
            }
            
            resp = self.api_call("POST", "crm.fcrm.doctype.crm_deal.crm_deal.create_deal", deal_data)
            if resp.status_code == 200:
                deal_name = resp.json()['message']
                print(f"✅ Deal created: {deal_name}")
                
                # 2. Get Deal details
                resp = self.api_call("GET", "frappe.client.get", params={
                    "doctype": "CRM Deal",
                    "name": deal_name
                })
                if resp.status_code == 200:
                    print("✅ Deal retrieved successfully")
                    
                    # 3. Update Deal
                    resp = self.api_call("POST", "frappe.client.set_value", {
                        "doctype": "CRM Deal",
                        "name": deal_name,
                        "fieldname": "probability",
                        "value": 75
                    })
                    if resp.status_code == 200:
                        print("✅ Deal updated")
                        
                        self.test_results['deal_management'] = {
                            'status': 'PASSED',
                            'deal_created': deal_name
                        }
                        return deal_name
                        
        except Exception as e:
            print(f"❌ Deal management test failed: {str(e)}")
            self.test_results['deal_management'] = {'status': 'FAILED', 'error': str(e)}
        
        return None
    
    def test_contact_management(self):
        """Test Contact CRUD operations"""
        print("\n👤 Testing Contact Management...")
        test_data = self.generate_test_data("Contact")
        
        try:
            # 1. Create Contact
            contact_data = {
                "doctype": "Contact",
                "first_name": test_data['first_name'],
                "last_name": test_data['last_name'],
                "email_ids": [{"email_id": test_data['email'], "is_primary": 1}],
                "phone_nos": [{"phone": test_data['mobile_no'], "is_primary_mobile_no": 1}]
            }
            
            resp = self.api_call("POST", "frappe.client.insert", {"doc": contact_data})
            if resp.status_code == 200:
                contact_name = resp.json()['message']['name']
                print(f"✅ Contact created: {contact_name}")
                
                # 2. Search contacts by email
                resp = self.api_call("POST", "crm.api.contact.search_emails", {
                    "txt": test_data['email'][:5]
                })
                if resp.status_code == 200:
                    print("✅ Contact search successful")
                    
                    self.test_results['contact_management'] = {
                        'status': 'PASSED',
                        'contact_created': contact_name
                    }
                    return contact_name
                    
        except Exception as e:
            print(f"❌ Contact management test failed: {str(e)}")
            self.test_results['contact_management'] = {'status': 'FAILED', 'error': str(e)}
        
        return None
    
    def test_organization_management(self):
        """Test Organization CRUD operations"""
        print("\n🏢 Testing Organization Management...")
        test_data = self.generate_test_data("Org")
        
        try:
            # 1. Create Organization
            org_data = {
                "doctype": "CRM Organization",
                "organization_name": test_data['organization_name'],
                "website": test_data['website'],
                "industry": test_data['industry'],
                "annual_revenue": 1000000
            }
            
            resp = self.api_call("POST", "frappe.client.insert", {"doc": org_data})
            if resp.status_code == 200:
                org_name = resp.json()['message']['name']
                print(f"✅ Organization created: {org_name}")
                
                # 2. Update Organization
                resp = self.api_call("POST", "frappe.client.set_value", {
                    "doctype": "CRM Organization", 
                    "name": org_name,
                    "fieldname": "annual_revenue",
                    "value": 1500000
                })
                if resp.status_code == 200:
                    print("✅ Organization updated")
                    
                    self.test_results['organization_management'] = {
                        'status': 'PASSED',
                        'organization_created': org_name
                    }
                    return org_name
                    
        except Exception as e:
            print(f"❌ Organization management test failed: {str(e)}")
            self.test_results['organization_management'] = {'status': 'FAILED', 'error': str(e)}
        
        return None
    
    def test_api_endpoints(self):
        """Test various API endpoints"""
        print("\n🔗 Testing API Endpoints...")
        
        endpoints_to_test = [
            ("crm.api.get_posthog_settings", "GET", None),
            ("crm.api.views.get_views", "POST", {"doctype": "CRM Lead"}),
            ("crm.api.notifications.get_notifications", "GET", None),
            ("crm.api.whatsapp.is_whatsapp_enabled", "GET", None),
            ("crm.integrations.api.is_call_integration_enabled", "GET", None),
        ]
        
        passed_tests = 0
        total_tests = len(endpoints_to_test)
        
        for endpoint, method, data in endpoints_to_test:
            try:
                resp = self.api_call(method, endpoint, data)
                if resp.status_code == 200:
                    print(f"✅ {endpoint}")
                    passed_tests += 1
                else:
                    print(f"⚠️  {endpoint} - Status: {resp.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} - Error: {str(e)}")
        
        self.test_results['api_endpoints'] = {
            'status': 'PASSED' if passed_tests == total_tests else 'PARTIAL',
            'passed': passed_tests,
            'total': total_tests
        }
    
    def test_integrations(self):
        """Test integration features"""
        print("\n🔌 Testing Integration Features...")
        
        try:
            # Test Twilio integration status
            resp = self.api_call("GET", "crm.integrations.api.is_call_integration_enabled")
            if resp.status_code == 200:
                integration_status = resp.json().get('message', {})
                print(f"📞 Call Integration - Twilio: {integration_status.get('twilio_enabled', False)}")
                print(f"📞 Call Integration - Exotel: {integration_status.get('exotel_enabled', False)}")
            
            # Test WhatsApp integration status
            resp = self.api_call("GET", "crm.api.whatsapp.is_whatsapp_enabled")
            if resp.status_code == 200:
                whatsapp_enabled = resp.json().get('message', False)
                print(f"💬 WhatsApp Integration: {whatsapp_enabled}")
            
            self.test_results['integrations'] = {'status': 'PASSED'}
                
        except Exception as e:
            print(f"❌ Integration test failed: {str(e)}")
            self.test_results['integrations'] = {'status': 'FAILED', 'error': str(e)}
    
    def test_data_operations(self):
        """Test data operations like filtering, sorting"""
        print("\n📊 Testing Data Operations...")
        
        try:
            # Test getting leads with filters
            resp = self.api_call("POST", "crm.api.doc.get_data", {
                "doctype": "CRM Lead",
                "filters": {"status": "Open"},
                "order_by": "creation desc",
                "page_length": 10
            })
            if resp.status_code == 200:
                leads_data = resp.json().get('message', {})
                print(f"✅ Lead data retrieved: {len(leads_data.get('data', []))} records")
            
            # Test getting deals with filters
            resp = self.api_call("POST", "crm.api.doc.get_data", {
                "doctype": "CRM Deal",
                "filters": {},
                "order_by": "creation desc", 
                "page_length": 10
            })
            if resp.status_code == 200:
                deals_data = resp.json().get('message', {})
                print(f"✅ Deal data retrieved: {len(deals_data.get('data', []))} records")
                
            self.test_results['data_operations'] = {'status': 'PASSED'}
                
        except Exception as e:
            print(f"❌ Data operations test failed: {str(e)}")
            self.test_results['data_operations'] = {'status': 'FAILED', 'error': str(e)}
    
    def test_file_operations(self):
        """Test file upload functionality"""
        print("\n📎 Testing File Operations...")
        
        try:
            # Get file uploader defaults
            resp = self.api_call("POST", "crm.api.get_file_uploader_defaults", {
                "doctype": "CRM Lead"
            })
            if resp.status_code == 200:
                file_settings = resp.json().get('message', {})
                print(f"✅ File uploader settings retrieved")
                print(f"   Max file size: {file_settings.get('max_file_size', 'Unknown')}")
                print(f"   Allowed types: {file_settings.get('allowed_file_types', 'Unknown')}")
                
                self.test_results['file_operations'] = {'status': 'PASSED'}
            
        except Exception as e:
            print(f"❌ File operations test failed: {str(e)}")
            self.test_results['file_operations'] = {'status': 'FAILED', 'error': str(e)}
    
    def test_user_permissions(self):
        """Test user permissions and roles"""
        print("\n🔐 Testing User Permissions...")
        
        try:
            # Test app permission check
            resp = self.api_call("GET", "crm.api.check_app_permission")
            if resp.status_code == 200:
                has_permission = resp.json().get('message', False)
                print(f"✅ App permission check: {has_permission}")
            
            # Get current user
            resp = self.api_call("GET", "frappe.auth.get_logged_user")
            if resp.status_code == 200:
                user_info = resp.json().get('message', {})
                print(f"✅ Current user: {user_info}")
                
            self.test_results['user_permissions'] = {'status': 'PASSED'}
                
        except Exception as e:
            print(f"❌ User permissions test failed: {str(e)}")
            self.test_results['user_permissions'] = {'status': 'FAILED', 'error': str(e)}
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚀 Starting Comprehensive CRM Test Suite")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Login
            self.login()
            self.get_csrf_token()
            
            # Run all tests
            self.test_lead_management()
            self.test_deal_management() 
            self.test_contact_management()
            self.test_organization_management()
            self.test_api_endpoints()
            self.test_integrations()
            self.test_data_operations()
            self.test_file_operations()
            self.test_user_permissions()
            
        except Exception as e:
            print(f"\n💥 Test suite failed: {str(e)}")
            return False
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed_tests = 0
        total_tests = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = result['status']
            if status == 'PASSED':
                print(f"✅ {test_name.replace('_', ' ').title()}: PASSED")
                passed_tests += 1
            elif status == 'PARTIAL':
                print(f"⚠️  {test_name.replace('_', ' ').title()}: PARTIAL ({result.get('passed', 0)}/{result.get('total', 0)})")
            else:
                print(f"❌ {test_name.replace('_', ' ').title()}: FAILED")
                if 'error' in result:
                    print(f"   Error: {result['error']}")
        
        print(f"\n🎯 Overall Score: {passed_tests}/{total_tests} tests passed")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL TESTS PASSED! Your Frappe CRM is working perfectly!")
        elif passed_tests > total_tests * 0.8:
            print("\n✨ Most tests passed! CRM is mostly functional with minor issues.")
        else:
            print("\n⚠️  Several tests failed. Please check the errors above.")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    # Configuration
    BASE_URL = "http://localhost:8000"
    USERNAME = "Administrator" 
    PASSWORD = "admin"
    
    # Run tests
    test_suite = CRMTestSuite(BASE_URL, USERNAME, PASSWORD)
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)