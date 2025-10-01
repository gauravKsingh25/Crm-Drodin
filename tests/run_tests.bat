@echo off
echo ====================================================
echo     Frappe CRM Comprehensive Test Suite
echo ====================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if CRM is running
echo Checking if CRM is running...
curl -s -o nul -w "%%{http_code}" http://localhost:8000 | findstr "200" >nul
if errorlevel 1 (
    echo.
    echo WARNING: CRM may not be running on http://localhost:8000
    echo Please start your CRM Docker containers first:
    echo   docker compose -f docker/docker-compose.yml up -d
    echo.
    set /p continue="Continue anyway? (y/N): "
    if /i not "!continue!"=="y" (
        echo Test cancelled
        exit /b 1
    )
)

echo.
echo ====================================================
echo Running CRM Feature Tests...
echo ====================================================

REM Run the simple test suite (no dependencies required)
echo.
echo [1/3] Running Simple Feature Tests...
python tests/test_crm_simple.py
set SIMPLE_RESULT=%errorlevel%

REM Run the comprehensive test suite
echo.
echo [2/3] Running Comprehensive Feature Tests...
python tests/test_crm_features.py
set COMPREHENSIVE_RESULT=%errorlevel%

REM Try to run UI tests if selenium is available
echo.
echo [3/3] Checking for UI Test Dependencies...
python -c "import selenium" >nul 2>&1
if errorlevel 1 (
    echo Selenium not found - skipping UI tests
    echo To run UI tests, install selenium:
    echo   pip install selenium
    set UI_RESULT=2
) else (
    echo Running UI Tests...
    python tests/test_crm_ui.py
    set UI_RESULT=%errorlevel%
)

echo.
echo ====================================================
echo           TEST RESULTS SUMMARY
echo ====================================================

REM Display results
if %SIMPLE_RESULT%==0 (
    echo ✓ Simple Feature Tests: PASSED
) else (
    echo ✗ Simple Feature Tests: FAILED
)

if %COMPREHENSIVE_RESULT%==0 (
    echo ✓ Comprehensive Tests: PASSED
) else (
    echo ✗ Comprehensive Tests: FAILED
)

if %UI_RESULT%==0 (
    echo ✓ UI Tests: PASSED
) else if %UI_RESULT%==2 (
    echo - UI Tests: SKIPPED (no selenium)
) else (
    echo ✗ UI Tests: FAILED
)

echo.

REM Calculate overall result
set /a TOTAL_TESTS=2
set /a PASSED_TESTS=0

if %SIMPLE_RESULT%==0 set /a PASSED_TESTS+=1
if %COMPREHENSIVE_RESULT%==0 set /a PASSED_TESTS+=1

if %UI_RESULT%==0 (
    set /a TOTAL_TESTS+=1
    set /a PASSED_TESTS+=1
)

echo Overall Result: %PASSED_TESTS%/%TOTAL_TESTS% test suites passed

if %PASSED_TESTS%==%TOTAL_TESTS% (
    echo.
    echo 🎉 ALL TESTS PASSED! Your Frappe CRM is working perfectly!
    echo.
) else if %PASSED_TESTS% gtr 0 (
    echo.
    echo ⚠️ Some tests passed. Your CRM has basic functionality.
    echo Check the detailed output above for specific issues.
    echo.
) else (
    echo.
    echo ❌ Tests failed. Please check your CRM setup:
    echo   1. Ensure Docker containers are running
    echo   2. Verify CRM is accessible at http://localhost:8000
    echo   3. Check login credentials (Administrator/admin)
    echo.
)

echo ====================================================
echo                   NEXT STEPS
echo ====================================================
echo.
echo 1. CRM Access: http://localhost:8000/crm
echo 2. Login: Administrator / admin
echo 3. Docker Logs: docker compose -f docker/docker-compose.yml logs
echo 4. Stop CRM: docker compose -f docker/docker-compose.yml down
echo.

pause