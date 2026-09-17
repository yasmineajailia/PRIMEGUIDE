@echo off
echo ===================================================
echo     RUNNING INTEGRATION TESTS
echo ===================================================

echo.
echo Step 1: Testing FastAPI Backend
echo ---------------------------------------------------
python test_api.py --base-url http://localhost:8000
if %ERRORLEVEL% NEQ 0 (
    echo Backend tests failed! Please fix the issues before continuing.
    exit /b %ERRORLEVEL%
)

echo.
echo Step 2: Testing React Frontend
echo ---------------------------------------------------
cd react-example
call npm test -- --watchAll=false
if %ERRORLEVEL% NEQ 0 (
    echo Frontend tests failed! Please fix the issues before continuing.
    exit /b %ERRORLEVEL%
)

echo.
echo ===================================================
echo     ALL TESTS PASSED SUCCESSFULLY!
echo ===================================================
