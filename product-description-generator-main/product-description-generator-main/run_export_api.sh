#!/bin/bash

echo "Starting the Product Generator API..."

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
python export_api.py

echo ""
echo "API will be available at: http://localhost:8000"
echo ""
echo "To stop the server, press Ctrl+C in this window."
