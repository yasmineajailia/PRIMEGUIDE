# React-FastAPI Integration Test

This script tests the integration between the React frontend and FastAPI backend.
It verifies that API endpoints are accessible from the React app and components
function correctly.

## Requirements

1. Install test requirements:
```
npm install -g http-server cypress
```

2. Make sure the FastAPI backend is running:
```
cd d:\PI\product-description-generator-main\product-description-generator-main
python fastapi_app.py
```

3. Run the React app in a separate terminal:
```
cd d:\PI\product-description-generator-main\product-description-generator-main\react-example
npm start
```

## Integration Test Checklist

### Backend API Tests
- [ ] Run `test_api.py` to verify all endpoints work correctly
- [ ] Check CORS settings are correctly configured for frontend requests
- [ ] Verify static files are being served correctly (audio and images)

### Frontend Component Tests  
- [ ] Open the React app in browser: http://localhost:3000
- [ ] Test navigation between tabs (Trend Prediction and Audio Generator)
- [ ] Test the Audio Generator component:
  - [ ] Enter text in the text field
  - [ ] Select different voices from the dropdown
  - [ ] Adjust the style slider
  - [ ] Submit the form and verify audio generation
  - [ ] Verify that audio playback works
  - [ ] Test the download functionality

### Error Handling Tests
- [ ] Test with empty text (should show validation error)
- [ ] Test with very long text (should still work or show appropriate error)
- [ ] Test with network disconnected (should show network error)

## Manual API Testing

You can also test the API endpoints directly using curl:

### Get Available Voices
```powershell
curl -X GET http://localhost:8000/available-voices
```

### Generate Audio
```powershell
curl -X POST http://localhost:8000/generate-audio `
-H "Content-Type: application/json" `
-d "{\"text\":\"This is a test message\",\"voice_id\":\"Aria\",\"style\":0.5}"
```

### Generate Text
```powershell
curl -X POST http://localhost:8000/generate-product-description `
-H "Content-Type: application/json" `
-d "{\"product_name\":\"Smart Watch\",\"keywords\":\"fitness, health\",\"tone\":\"Enthusiastic\"}"
```

## Troubleshooting

If you encounter issues with the integration:

1. Check that both servers are running (FastAPI on port 8000, React on port 3000)
2. Verify CORS settings in the FastAPI app
3. Check browser console for JavaScript errors
4. Look at network tab in developer tools to see API request/response details
5. Verify API endpoints with a tool like Postman or use the test_api.py script
