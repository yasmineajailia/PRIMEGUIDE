# Implementation Script for Fixes
# This script implements all fixes for the product description generator application

import os
import sys
import shutil
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("implementation.log")
    ]
)
logger = logging.getLogger("implementation")

def backup_original_file(file_path):
    """Create a backup of the original file"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup_{int(time.time())}"
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup of {file_path} at {backup_path}")
        return backup_path
    else:
        logger.warning(f"Original file {file_path} does not exist, no backup created")
        return None

def replace_image_generator():
    """Replace the original image generator with the enhanced version"""
    original_path = "generators/image_generator.py"
    enhanced_path = "enhanced_image_generator.py"
    
    if not os.path.exists(enhanced_path):
        logger.error(f"Enhanced generator {enhanced_path} not found")
        return False
    
    try:
        # Create backup
        backup_path = backup_original_file(original_path)
        
        # Copy enhanced version to original location
        shutil.copy2(enhanced_path, original_path)
        logger.info(f"Successfully replaced {original_path} with enhanced version")
        return True
    except Exception as e:
        logger.error(f"Error replacing image generator: {e}")
        return False

def setup_static_directories():
    """Setup static directories and symbolic links"""
    try:
        # Create necessary directories
        os.makedirs("static", exist_ok=True)
        os.makedirs("generated_images", exist_ok=True)
        logger.info("Created necessary directories")
        
        # Create symbolic link if it doesn't exist
        if not os.path.exists("static/generated_images") or not os.path.isdir("static/generated_images"):
            # Remove if it exists but is not a directory
            if os.path.exists("static/generated_images"):
                os.remove("static/generated_images")
                logger.info("Removed existing file at static/generated_images")
            
            # Create symbolic link for the static directory
            if os.name == 'nt':  # Windows
                os.system(f'mklink /J "{os.path.abspath("static/generated_images")}" "{os.path.abspath("generated_images")}"')
            else:  # Unix
                os.symlink(os.path.abspath("generated_images"), os.path.abspath("static/generated_images"))
            logger.info("Created symbolic link for static/generated_images")
        
        # Also do the same for audio directory if it exists
        if os.path.exists("generated_audio"):
            os.makedirs("static/generated_audio", exist_ok=True)
            if not os.path.exists("static/generated_audio") or not os.path.isdir("static/generated_audio"):
                if os.path.exists("static/generated_audio"):
                    os.remove("static/generated_audio")
                
                if os.name == 'nt':  # Windows
                    os.system(f'mklink /J "{os.path.abspath("static/generated_audio")}" "{os.path.abspath("generated_audio")}"')
                else:  # Unix
                    os.symlink(os.path.abspath("generated_audio"), os.path.abspath("static/generated_audio"))
                logger.info("Created symbolic link for static/generated_audio")
        
        return True
    except Exception as e:
        logger.error(f"Error setting up static directories: {e}")
        return False

def create_restart_script():
    """Create a script to restart the FastAPI server with proper configuration"""
    script_content = """@echo off
echo Starting FastAPI server with enhanced logging...
echo.

set PYTHONUNBUFFERED=1
cd /d %~dp0
python -m uvicorn fastapi_app:app --reload --host 0.0.0.0 --port 8000

echo.
pause
"""
    
    try:
        script_path = "start_server.bat"
        with open(script_path, "w") as f:
            f.write(script_content)
        logger.info(f"Created restart script at {script_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating restart script: {e}")
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("IMPLEMENTING FIXES FOR PRODUCT DESCRIPTION GENERATOR")
    print("=" * 80)
    
    print("\nThis script will implement the following fixes:")
    print("1. Replace the image generator with the enhanced version")
    print("2. Setup static directories and symbolic links")
    print("3. Create a restart script for the FastAPI server")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(0)
    
    # Implement fixes
    print("\nImplementing fixes...")
    
    result1 = replace_image_generator()
    print(f"1. Replace image generator: {'✅ SUCCESS' if result1 else '❌ FAILED'}")
    
    result2 = setup_static_directories()
    print(f"2. Setup static directories: {'✅ SUCCESS' if result2 else '❌ FAILED'}")
    
    result3 = create_restart_script()
    print(f"3. Create restart script: {'✅ SUCCESS' if result3 else '❌ FAILED'}")
    
    # Overall result
    if result1 and result2 and result3:
        print("\n✅ All fixes implemented successfully!")
        print("\nNext steps:")
        print("1. Run the start_server.bat script to start the FastAPI server")
        print("2. Use test_image_with_logging.py to test image generation")
        print("3. Navigate to http://127.0.0.1:8000/docs to test the API directly")
    else:
        print("\n⚠️ Some fixes could not be implemented. Check the implementation.log for details.")
    
    print("\nImplementation completed.")
    print("=" * 80)
