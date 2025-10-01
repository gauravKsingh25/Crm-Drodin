# 🧪 Frappe CRM Test Suite

This comprehensive test suite validates all major features of your Frappe CRM installation.

## 📋 Test Coverage

### 1. **Simple Feature Tests** (`test_crm_simple.py`)
- ✅ Basic connectivity 
- ✅ API endpoint accessibility
- ✅ Document creation (Leads)
- ✅ Data listing functionality
- ✅ Integration status checks
- ✅ User permissions verification

### 2. **Comprehensive Feature Tests** (`test_crm_features.py`)
- ✅ Lead Management (CRUD operations)
- ✅ Deal Management (CRUD operations)
- ✅ Contact Management (CRUD operations)
- ✅ Organization Management (CRUD operations)
- ✅ API endpoints testing
- ✅ Integration features (WhatsApp, Twilio, Exotel)
- ✅ Data operations (filtering, sorting)
- ✅ File upload functionality
- ✅ User permissions and roles

### 3. **UI Tests** (`test_crm_ui.py`) - *Optional*
- ✅ Login interface testing
- ✅ Navigation between CRM sections
- ✅ Form creation interfaces
- ✅ Search functionality
- ✅ Mobile responsiveness
- ✅ Performance metrics

## 🚀 Quick Start

### Prerequisites
1. **CRM Running**: Your Frappe CRM should be running on `http://localhost:8000`
2. **Python**: Python 3.6+ installed
3. **Access**: Login credentials (default: Administrator/admin)

### Run All Tests (Easiest)
```bash
# Windows
tests\run_tests.bat

# Linux/Mac
chmod +x tests/run_tests.sh && tests/run_tests.sh
```

### Run Individual Tests
```bash
# Simple tests (no dependencies)
python tests/test_crm_simple.py

# Comprehensive tests (requires requests library)
python tests/test_crm_features.py

# UI tests (requires selenium)
pip install selenium
python tests/test_crm_ui.py
```

## 📦 Dependencies

### Required (auto-installed with Python)
- `urllib` - for HTTP requests
- `json` - for JSON parsing
- `time` - for timing operations
- `random` - for test data generation

### Optional
- `requests` - for advanced HTTP features (comprehensive tests)
- `selenium` - for UI testing (requires ChromeDriver)

## 🔧 Configuration

Edit the configuration at the top of each test file:

```python
BASE_URL = "http://localhost:8000"     # Your CRM URL
USERNAME = "Administrator"              # Admin username
PASSWORD = "admin"                      # Admin password
```

## 📊 Understanding Results

### ✅ PASSED
- Feature works correctly
- All operations completed successfully

### ⚠️ PARTIAL 
- Feature partially works
- Some operations failed but core functionality exists

### ❌ FAILED
- Feature completely broken
- Critical errors preventing operation

## 🛠️ Troubleshooting

### Common Issues

#### 1. Connection Refused
```
❌ Cannot access login page: [Errno 111] Connection refused
```
**Solution**: Start your CRM containers
```bash
docker compose -f docker/docker-compose.yml up -d
```

#### 2. Login Failed
```
❌ Login failed: Invalid credentials
```
**Solution**: 
- Check credentials in test script
- Verify CRM is fully initialized
- Wait for Docker containers to complete setup

#### 3. Permission Denied
```
❌ Not allowed to create Lead
```
**Solution**: 
- Use Administrator account
- Check user roles and permissions
- Verify CRM installation completed

#### 4. Selenium Not Found
```
❌ Import "selenium" could not be resolved
```
**Solution**: Install Selenium (optional for UI tests)
```bash
pip install selenium
```

### Docker Issues

#### Check Container Status
```bash
docker compose -f docker/docker-compose.yml ps
```

#### View Logs
```bash
docker compose -f docker/docker-compose.yml logs frappe
```

#### Restart Containers
```bash
docker compose -f docker/docker-compose.yml down
docker compose -f docker/docker-compose.yml up -d
```

## 📝 Test Customization

### Adding New Tests

1. **Simple Tests**: Add to `test_crm_simple.py`
```python
def test_my_feature(self):
    print("🔧 Testing My Feature...")
    # Your test logic here
    self.results['my_feature'] = 'PASSED'
```

2. **Comprehensive Tests**: Add to `test_crm_features.py`
```python
def test_my_advanced_feature(self):
    """Test advanced feature"""
    try:
        # Test implementation
        self.test_results['my_advanced_feature'] = {'status': 'PASSED'}
    except Exception as e:
        self.test_results['my_advanced_feature'] = {'status': 'FAILED', 'error': str(e)}
```

### Custom Test Data
Modify the `generate_test_data()` function:
```python
def generate_test_data(self, prefix="Custom"):
    return {
        'first_name': f"Custom{random.randint(1000, 9999)}",
        'email': f"custom{random.randint(1000, 9999)}@yourcompany.com",
        # Add your custom fields
    }
```

## 🎯 Advanced Usage

### Testing Different Environments
```python
# Test staging environment
tester = SimpleCRMTester("https://staging.yourcrm.com", "admin", "password")

# Test with different user roles
tester = SimpleCRMTester("http://localhost:8000", "sales_user", "password")
```

### Batch Testing Multiple Instances
```python
environments = [
    ("http://localhost:8000", "Administrator", "admin"),
    ("https://staging.yourcrm.com", "admin", "staging_pass"),
    ("https://prod.yourcrm.com", "admin", "prod_pass")
]

for base_url, username, password in environments:
    tester = SimpleCRMTester(base_url, username, password)
    tester.run_tests()
```

## 📈 Performance Testing

The test suite includes basic performance metrics:
- **Page Load Times**: Measures initial CRM load time
- **API Response Times**: Tracks API endpoint performance
- **Operation Timing**: Times CRUD operations

### Performance Thresholds
- **Excellent**: < 2 seconds
- **Good**: 2-5 seconds  
- **Acceptable**: 5-10 seconds
- **Poor**: > 10 seconds

## 🔐 Security Notes

- Tests use read/write operations on test data
- Cleanup is attempted but not guaranteed
- Use test environments when possible
- Be careful with production credentials

## 🆘 Support

If tests consistently fail:

1. **Check CRM Status**: Verify CRM is running and accessible
2. **Review Logs**: Check Docker container logs for errors
3. **Verify Setup**: Ensure initialization completed successfully
4. **Test Manually**: Try creating a lead manually in the UI
5. **Check Network**: Verify no firewall blocking localhost:8000

## 📚 Additional Resources

- [Frappe CRM Documentation](https://github.com/frappe/crm)
- [Frappe Framework Docs](https://frappeframework.com/docs)
- [Docker Compose Guide](https://docs.docker.com/compose/)
- [Python Testing Best Practices](https://docs.python.org/3/library/unittest.html)

---

## 🎉 Happy Testing!

This test suite helps ensure your Frappe CRM is working correctly and all features are functional. Regular testing helps catch issues early and maintain system reliability.