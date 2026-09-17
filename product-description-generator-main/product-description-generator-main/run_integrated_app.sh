#!/bin/bash

echo "Starting the Product Description Generator System..."

# Create directories for generated content if they don't exist
if [ ! -d "generated_images" ]; then
  mkdir -p "generated_images"
  echo "Created generated_images directory"
fi

if [ ! -d "generated_gifs" ]; then
  mkdir -p "generated_gifs"
  echo "Created generated_gifs directory"
fi

echo ""
echo "Starting FastAPI server..."
python api.py &
API_PID=$!

# Wait for API to start
echo "Waiting for API server to start..."
sleep 5

echo ""
echo "Starting React development server..."
cd react-example
npm start &
REACT_PID=$!

echo ""
echo "Both servers are starting up..."
echo "API will be available at: http://localhost:8000"
echo "React app will open automatically or visit: http://localhost:3000"
echo ""
echo "To stop the servers, press Ctrl+C"

# Trap Ctrl+C and kill both processes
trap "kill $API_PID $REACT_PID; exit" INT

# Wait for both processes
wait
