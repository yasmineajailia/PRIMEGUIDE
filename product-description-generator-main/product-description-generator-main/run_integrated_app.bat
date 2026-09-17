@echo off
echo Starting the Product Description Generator System...

REM Create directories for generated content if they don't exist
if not exist "generated_images" (
    mkdir "generated_images"
    echo Created generated_images directory
)

if not exist "generated_gifs" (
    mkdir "generated_gifs"
    echo Created generated_gifs directory
)

echo.
echo Starting FastAPI server...
start cmd /k "python api.py"

REM Wait for API to start
timeout /t 5 /nobreak

echo.
echo Starting React development server...
cd react-example
start cmd /k "npm start"

echo.
echo Both servers are starting up...
echo API will be available at: http://localhost:8000
echo React app will open automatically or visit: http://localhost:3000
echo.
echo To stop the servers, close the command windows or press Ctrl+C in each window.
