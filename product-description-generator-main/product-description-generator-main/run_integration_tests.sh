#!/bin/bash

echo "==================================================="
echo "     RUNNING INTEGRATION TESTS"
echo "==================================================="

echo
echo "Step 1: Testing FastAPI Backend"
echo "---------------------------------------------------"
python test_api.py --base-url http://localhost:8000
if [ $? -ne 0 ]; then
    echo "Backend tests failed! Please fix the issues before continuing."
    exit 1
fi

echo
echo "Step 2: Testing React Frontend"
echo "---------------------------------------------------"
cd react-example
npm test -- --watchAll=false
if [ $? -ne 0 ]; then
    echo "Frontend tests failed! Please fix the issues before continuing."
    exit 1
fi

echo
echo "==================================================="
echo "     ALL TESTS PASSED SUCCESSFULLY!"
echo "==================================================="
