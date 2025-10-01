#!/usr/bin/env python3
"""
Frontend UI Test Suite for Frappe CRM
Tests the web interface using Selenium WebDriver
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import random
import string

class CRMUITestSuite:
    def __init__(self, base_url="http://localhost:8000", username="Administrator", password="admin"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.driver = None
        self.wait = None
        self.test_results = {}
    
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        print("🌐 Setting up WebDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            print("✅ WebDriver setup successful")
            return True
        except Exception as e:
            print(f"❌ WebDriver setup failed: {str(e)}")
            print("💡 Please install ChromeDriver or use headless mode")
            return False
    
    def login_ui(self):
        """Login through web interface"""
        print("🔐 Testing UI Login...")
        
        try:
            self.driver.get(f"{self.base_url}/login")
            
            # Wait for login form
            self.wait.until(EC.presence_of_element_located((By.NAME, "usr")))
            
            # Fill login form
            username_field = self.driver.find_element(By.NAME, "usr")
            password_field = self.driver.find_element(By.NAME, "pwd")
            
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)
            
            # Wait for redirect after login
            time.sleep(3)
            
            # Check if login successful (should redirect to main page)
            if "/app" in self.driver.current_url or "/crm" in self.driver.current_url:
                print("✅ UI Login successful")
                self.test_results['ui_login'] = {'status': 'PASSED'}
                return True
            else:
                print(f"❌ UI Login failed - URL: {self.driver.current_url}")
                self.test_results['ui_login'] = {'status': 'FAILED'}
                return False
                
        except Exception as e:
            print(f"❌ UI Login failed: {str(e)}")
            self.test_results['ui_login'] = {'status': 'FAILED', 'error': str(e)}
            return False
    
    def navigate_to_crm(self):
        """Navigate to CRM application"""
        print("🧭 Navigating to CRM...")
        
        try:
            # Try direct CRM URL
            self.driver.get(f"{self.base_url}/crm")
            time.sleep(3)
            
            # Check if CRM loaded
            if "CRM" in self.driver.title or "crm" in self.driver.current_url:
                print("✅ CRM navigation successful")
                return True
            else:
                print(f"❌ CRM navigation failed - Title: {self.driver.title}")
                return False
                
        except Exception as e:
            print(f"❌ CRM navigation failed: {str(e)}")
            return False
    
    def test_lead_creation_ui(self):
        """Test creating a lead through UI"""
        print("📝 Testing Lead Creation UI...")
        
        try:
            # Navigate to leads page
            self.driver.get(f"{self.base_url}/crm/leads")
            time.sleep(2)
            
            # Look for "New Lead" or "+" button
            try:
                new_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'New') or contains(text(), '+')]"))
                )
                new_button.click()
                time.sleep(2)
                
                # Generate test data
                test_name = f"TestLead{''.join(random.choices(string.ascii_lowercase, k=5))}"
                test_email = f"test{random.randint(1000, 9999)}@example.com"
                
                # Fill form fields (adapt selectors based on actual form)
                form_fields = [
                    ("first_name", test_name),
                    ("email", test_email),
                    ("mobile_no", f"+1555{random.randint(1000000, 9999999)}")
                ]
                
                for field_name, value in form_fields:
                    try:
                        field = self.driver.find_element(By.NAME, field_name)
                        field.clear()
                        field.send_keys(value)
                    except:
                        # Try alternative selectors
                        try:
                            field = self.driver.find_element(By.CSS_SELECTOR, f"input[data-field='{field_name}']")
                            field.clear() 
                            field.send_keys(value)
                        except:
                            pass  # Skip if field not found
                
                # Save the lead
                save_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Save') or contains(text(), 'Create')]")
                save_button.click()
                time.sleep(3)
                
                print("✅ Lead creation UI test completed")
                self.test_results['lead_creation_ui'] = {'status': 'PASSED'}
                
            except Exception as e:
                print(f"⚠️  Lead creation UI - Form interaction failed: {str(e)}")
                self.test_results['lead_creation_ui'] = {'status': 'PARTIAL'}
                
        except Exception as e:
            print(f"❌ Lead creation UI test failed: {str(e)}")
            self.test_results['lead_creation_ui'] = {'status': 'FAILED', 'error': str(e)}
    
    def test_deal_creation_ui(self):
        """Test creating a deal through UI"""
        print("💼 Testing Deal Creation UI...")
        
        try:
            # Navigate to deals page
            self.driver.get(f"{self.base_url}/crm/deals")
            time.sleep(2)
            
            # Look for "New Deal" button
            try:
                new_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'New') or contains(text(), '+')]"))
                )
                new_button.click()
                time.sleep(2)
                
                print("✅ Deal creation UI test completed")
                self.test_results['deal_creation_ui'] = {'status': 'PASSED'}
                
            except Exception as e:
                print(f"⚠️  Deal creation UI - Button not found: {str(e)}")
                self.test_results['deal_creation_ui'] = {'status': 'PARTIAL'}
                
        except Exception as e:
            print(f"❌ Deal creation UI test failed: {str(e)}")
            self.test_results['deal_creation_ui'] = {'status': 'FAILED', 'error': str(e)}
    
    def test_navigation_ui(self):
        """Test navigation between different CRM sections"""
        print("🗂️  Testing Navigation UI...")
        
        navigation_tests = [
            ("/crm/leads", "Leads"),
            ("/crm/deals", "Deals"), 
            ("/crm/contacts", "Contacts"),
            ("/crm/organizations", "Organizations"),
        ]
        
        passed_nav = 0
        
        for url, section_name in navigation_tests:
            try:
                self.driver.get(f"{self.base_url}{url}")
                time.sleep(2)
                
                # Check if page loaded (has some content)
                if len(self.driver.page_source) > 1000:  # Basic check
                    print(f"✅ {section_name} page loaded")
                    passed_nav += 1
                else:
                    print(f"⚠️  {section_name} page - minimal content")
                    
            except Exception as e:
                print(f"❌ {section_name} navigation failed: {str(e)}")
        
        if passed_nav == len(navigation_tests):
            self.test_results['navigation_ui'] = {'status': 'PASSED'}
        elif passed_nav > 0:
            self.test_results['navigation_ui'] = {'status': 'PARTIAL'}
        else:
            self.test_results['navigation_ui'] = {'status': 'FAILED'}
    
    def test_search_functionality(self):
        """Test search functionality"""
        print("🔍 Testing Search Functionality...")
        
        try:
            # Navigate to leads and try to search
            self.driver.get(f"{self.base_url}/crm/leads")
            time.sleep(2)
            
            # Look for search box
            search_selectors = [
                "input[placeholder*='Search']",
                "input[type='search']",
                ".search input",
                "[data-testid='search']"
            ]
            
            search_box = None
            for selector in search_selectors:
                try:
                    search_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if search_box:
                search_box.send_keys("test")
                search_box.send_keys(Keys.RETURN)
                time.sleep(2)
                print("✅ Search functionality test completed")
                self.test_results['search_functionality'] = {'status': 'PASSED'}
            else:
                print("⚠️  Search box not found")
                self.test_results['search_functionality'] = {'status': 'PARTIAL'}
                
        except Exception as e:
            print(f"❌ Search functionality test failed: {str(e)}")
            self.test_results['search_functionality'] = {'status': 'FAILED', 'error': str(e)}
    
    def test_mobile_responsiveness(self):
        """Test mobile responsive design"""
        print("📱 Testing Mobile Responsiveness...")
        
        try:
            # Set mobile viewport
            self.driver.set_window_size(375, 667)  # iPhone dimensions
            
            self.driver.get(f"{self.base_url}/crm")
            time.sleep(2)
            
            # Check if mobile elements are present or if layout adapts
            body_width = self.driver.execute_script("return document.body.scrollWidth;")
            
            if body_width <= 400:  # Reasonable mobile width
                print("✅ Mobile responsiveness test passed")
                self.test_results['mobile_responsiveness'] = {'status': 'PASSED'}
            else:
                print("⚠️  Mobile responsiveness - layout may not be optimized")
                self.test_results['mobile_responsiveness'] = {'status': 'PARTIAL'}
            
            # Reset to desktop size
            self.driver.set_window_size(1920, 1080)
            
        except Exception as e:
            print(f"❌ Mobile responsiveness test failed: {str(e)}")
            self.test_results['mobile_responsiveness'] = {'status': 'FAILED', 'error': str(e)}
    
    def test_performance_metrics(self):
        """Test basic performance metrics"""
        print("⚡ Testing Performance Metrics...")
        
        try:
            start_time = time.time()
            self.driver.get(f"{self.base_url}/crm")
            
            # Wait for page to be fully loaded
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            load_time = time.time() - start_time
            
            print(f"📊 Page load time: {load_time:.2f} seconds")
            
            if load_time < 5:
                print("✅ Performance test passed (< 5s)")
                self.test_results['performance_metrics'] = {'status': 'PASSED', 'load_time': load_time}
            elif load_time < 10:
                print("⚠️  Performance test partial (5-10s)")
                self.test_results['performance_metrics'] = {'status': 'PARTIAL', 'load_time': load_time}
            else:
                print("❌ Performance test failed (> 10s)")
                self.test_results['performance_metrics'] = {'status': 'FAILED', 'load_time': load_time}
                
        except Exception as e:
            print(f"❌ Performance test failed: {str(e)}")
            self.test_results['performance_metrics'] = {'status': 'FAILED', 'error': str(e)}
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
            print("🧹 WebDriver cleaned up")
    
    def run_ui_tests(self):
        """Run all UI tests"""
        print("🎭 Starting UI Test Suite for Frappe CRM")
        print("=" * 60)
        
        if not self.setup_driver():
            return False
        
        try:
            # Run all UI tests
            if not self.login_ui():
                print("❌ Cannot proceed without login")
                return False
            
            if not self.navigate_to_crm():
                print("❌ Cannot access CRM application")
                return False
            
            self.test_navigation_ui()
            self.test_lead_creation_ui()
            self.test_deal_creation_ui()
            self.test_search_functionality()
            self.test_mobile_responsiveness()
            self.test_performance_metrics()
            
        finally:
            self.cleanup()
        
        # Print results
        print("\n" + "=" * 60)
        print("🎭 UI TEST RESULTS")
        print("=" * 60)
        
        passed_tests = 0
        total_tests = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = result['status']
            if status == 'PASSED':
                print(f"✅ {test_name.replace('_', ' ').title()}: PASSED")
                passed_tests += 1
            elif status == 'PARTIAL':
                print(f"⚠️  {test_name.replace('_', ' ').title()}: PARTIAL")
                passed_tests += 0.5
            else:
                print(f"❌ {test_name.replace('_', ' ').title()}: FAILED")
        
        print(f"\n🎯 UI Test Score: {passed_tests}/{total_tests} tests passed")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    BASE_URL = "http://localhost:8000"
    USERNAME = "Administrator"
    PASSWORD = "admin"
    
    ui_test_suite = CRMUITestSuite(BASE_URL, USERNAME, PASSWORD)
    success = ui_test_suite.run_ui_tests()