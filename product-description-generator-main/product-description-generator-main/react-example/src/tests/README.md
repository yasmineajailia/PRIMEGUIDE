# Frontend Integration Tests

This directory contains automated tests for the React frontend components and their integration with the FastAPI backend.

## Running the Tests

1. Make sure the FastAPI backend is running:
```
cd d:\PI\product-description-generator-main\product-description-generator-main
python fastapi_app.py
```

2. Make sure the React app is running:
```
cd d:\PI\product-description-generator-main\product-description-generator-main\react-example
npm start
```

3. Run the integration tests:
```
cd d:\PI\product-description-generator-main\product-description-generator-main\react-example
npm test
```

## Test Files Overview

- `audioGenerator.test.js`: Tests for the Audio Generator component
- `api.test.js`: Tests for the API service functions
- `app.test.js`: Tests for the main App component and navigation

## Manual Testing

For manual testing instructions, refer to:
`d:\PI\product-description-generator-main\product-description-generator-main\INTEGRATION-TEST-GUIDE.md`
