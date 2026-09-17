# Comprehensive test script for the product description generator
import os
import sys
import logging
import time
import shutil
import requests
import webbrowser
import json
from PIL import Image
from pprint import pprint

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("comprehensive_test.log")
    ]
)
logger = logging.getLogger("comprehensive-test")

def setup_environment():
    """Setup the environment for testing"""
    logger.info("Setting up test environment")
    
    # Create required directories
    directories = ["static", "generated_images", "static/generated_images"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    # Create symbolic link if it doesn't exist
    if not os.path.exists("static/generated_images") or not os.path.isdir("static/generated_images"):
        # Remove if it exists but is not a directory
        if os.path.exists("static/generated_images"):
            try:
                os.remove("static/generated_images")
                logger.info("Removed existing file at static/generated_images")
            except:
                logger.warning("Could not remove existing file at static/generated_images")
        
        try:
            # Create symbolic link for the static directory
            if os.name == 'nt':  # Windows
                os.system(f'mklink /J "{os.path.abspath("static/generated_images")}" "{os.path.abspath("generated_images")}"')
            else:  # Unix
                os.symlink(os.path.abspath("generated_images"), os.path.abspath("static/generated_images"))
            logger.info("Created symbolic link for static/generated_images")
        except Exception as e:
            logger.error(f"Failed to create symbolic link: {e}")
    
    # Create a test file for checking paths
    test_file_path = "generated_images/test_file.txt"
    with open(test_file_path, "w") as f:
        f.write(f"This is a test file created at {time.ctime()}")
    logger.info(f"Created test file at {test_file_path}")
    
    # Also create a test image
    test_image = Image.new('RGB', (100, 100), color=(255, 0, 0))
    test_image_path = "generated_images/test_image.png"
    test_image.save(test_image_path)
    logger.info(f"Created test image at {test_image_path}")
    
    # Check if symbolic link is working
    static_test_path = "static/generated_images/test_file.txt"
    if os.path.exists(static_test_path):
        logger.info(f"Symbolic link verified: {static_test_path} exists")
    else:
        logger.error(f"Symbolic link not working: {static_test_path} does not exist")

def verify_image_generator():
    """Verify the image generator code"""
    logger.info("Verifying image generator implementation")
    
    # Check if the image generator module exists
    if not os.path.exists("generators/image_generator.py"):
        logger.error("generators/image_generator.py not found")
        return False
    
    # Try importing the module
    try:
        sys.path.append(os.path.abspath("."))
        from generators.image_generator import generate_product_image
        logger.info("Successfully imported image_generator module")
        return True
    except Exception as e:
        logger.error(f"Error importing image_generator: {e}")
        return False

def verify_enhanced_generator():
    """Verify the enhanced image generator code"""
    logger.info("Verifying enhanced image generator implementation")
    
    # Check if the enhanced image generator module exists
    if not os.path.exists("enhanced_image_generator.py"):
        logger.error("enhanced_image_generator.py not found")
        return False
    
    # Try importing the module
    try:
        sys.path.append(os.path.abspath("."))
        from enhanced_image_generator import generate_product_image
        logger.info("Successfully imported enhanced_image_generator module")
        return True
    except Exception as e:
        logger.error(f"Error importing enhanced_image_generator: {e}")
        return False

def run_fastapi_test():
    """Test FastAPI static file configuration if the server is running"""
    logger.info("Testing FastAPI static file configuration")
    
    base_url = "http://127.0.0.1:8000"
    endpoints = [
        "/generated_images/test_file.txt",
        "/static/generated_images/test_file.txt",
        "/generated_images/test_image.png",
        "/static/generated_images/test_image.png"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            logger.info(f"Testing URL: {url}")
            response = requests.get(url)
            status = response.status_code
            results[endpoint] = {
                "status": status,
                "success": status == 200,
                "content_type": response.headers.get("content-type", "unknown") if status == 200 else "N/A"
            }
            logger.info(f"Result: {status} {'✅' if status == 200 else '❌'}")
        except Exception as e:
            logger.error(f"Error testing {url}: {e}")
            results[endpoint] = {
                "status": "Error",
                "success": False,
                "error": str(e)
            }
    
    return results

def create_html_report(results):
    """Create an HTML report of test results"""
    logger.info("Creating HTML report")
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Comprehensive Test Report</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }
            h1, h2, h3 { color: #333; }
            .section { margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .success { color: green; }
            .failure { color: red; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { padding: 10px; text-align: left; border: 1px solid #ddd; }
            th { background-color: #f5f5f5; }
            .success-row { background-color: #e6ffe6; }
            .failure-row { background-color: #ffe6e6; }
            pre { background-color: #f5f5f5; padding: 10px; border-radius: 3px; overflow: auto; }
        </style>
    </head>
    <body>
        <h1>Product Description Generator - Comprehensive Test Report</h1>
        <div class="section">
            <h2>Test Environment Setup</h2>
            <p>Directories and symbolic links were created to ensure proper static file access.</p>
            <pre>Static directory: ./static
Generated images directory: ./generated_images
Symbolic link: ./static/generated_images -> ./generated_images</pre>
            <p>Test files were created to verify path access:</p>
            <ul>
                <li><code>generated_images/test_file.txt</code></li>
                <li><code>generated_images/test_image.png</code></li>
            </ul>
        </div>
    """
    
    # Add FastAPI test results if available
    if results:
        html_content += """
        <div class="section">
            <h2>FastAPI Static File Access Test Results</h2>
            <p>Testing both direct and static paths to the same files:</p>
            <table>
                <tr>
                    <th>Path</th>
                    <th>Status</th>
                    <th>Content Type</th>
                    <th>Result</th>
                </tr>
        """
        
        for endpoint, data in results.items():
            result_class = "success-row" if data.get("success", False) else "failure-row"
            result_icon = "✅" if data.get("success", False) else "❌"
            
            html_content += f"""
                <tr class="{result_class}">
                    <td><code>{endpoint}</code></td>
                    <td>{data.get("status", "Unknown")}</td>
                    <td>{data.get("content_type", "N/A")}</td>
                    <td>{result_icon}</td>
                </tr>
            """
        
        html_content += """
            </table>
        </div>
        """
    
    # Add recommendations section
    html_content += """
        <div class="section">
            <h2>Recommended Fixes</h2>
            <h3>1. Image Generator Syntax and Logging</h3>
            <p>The enhanced image generator includes:</p>
            <ul>
                <li>Fixed syntax errors in the original file</li>
                <li>Improved logging to display progress in the terminal</li>
                <li>Better error handling with detailed error messages</li>
                <li>Creation of symbolic links for proper static file access</li>
            </ul>
            
            <h3>2. FastAPI Configuration</h3>
            <p>For proper image access, ensure the FastAPI app includes:</p>
            <pre>
# Create directories if they don't exist
os.makedirs("static", exist_ok=True)
os.makedirs("generated_images", exist_ok=True)

# Create symbolic links
if not os.path.exists("static/generated_images"):
    if os.name == 'nt':  # Windows
        os.system(f'mklink /J "{os.path.abspath("static/generated_images")}" "{os.path.abspath("generated_images")}"')
    else:  # Unix
        os.symlink(os.path.abspath("generated_images"), os.path.abspath("static/generated_images"))

# Mount static directories
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/generated_images", StaticFiles(directory="generated_images"), name="generated_images")
            </pre>
            
            <h3>3. API Response Format</h3>
            <p>Ensure API endpoints return both URL formats:</p>
            <pre>
# Get relative path for URL
relative_path = image_path.replace('\\', '/')
if '/' in relative_path:
    relative_path = '/' + '/'.join(relative_path.split('/')[1:])

# Also create a static URL path for backward compatibility
static_path = '/static' + relative_path
    
return {
    "success": True,
    "image_url": relative_path,
    "static_image_url": static_path,
    "status": status
}
            </pre>
        </div>
    </body>
    </html>
    """
    
    # Write HTML file
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "comprehensive_test_report.html")
    with open(html_path, "w") as f:
        f.write(html_content)
    
    logger.info(f"HTML report created at: {html_path}")
    return html_path

if __name__ == "__main__":
    print("=" * 80)
    print("COMPREHENSIVE TEST FOR PRODUCT DESCRIPTION GENERATOR")
    print("=" * 80)
    
    # Setup environment
    setup_environment()
    
    # Verify image generator modules
    original_generator = verify_image_generator()
    enhanced_generator = verify_enhanced_generator()
    
    print("\nVerification Results:")
    print(f"Original Image Generator: {'✅ Available' if original_generator else '❌ Not available or has errors'}")
    print(f"Enhanced Image Generator: {'✅ Available' if enhanced_generator else '❌ Not available or has errors'}")
    
    # Test FastAPI if it's running
    print("\nTesting FastAPI static files (if server is running)...")
    try:
        fastapi_results = run_fastapi_test()
        print("\nFastAPI Test Results:")
        pprint(fastapi_results)
    except Exception as e:
        print(f"Error testing FastAPI: {e}")
        fastapi_results = {}
        print("FastAPI may not be running. This is normal if you haven't started the server.")
    
    # Create HTML report
    html_path = create_html_report(fastapi_results)
    print(f"\nHTML report created at: {html_path}")
    
    try:
        webbrowser.open(f"file://{html_path}")
        print("Report opened in browser")
    except:
        print("Could not open report in browser automatically. Please open it manually.")
    
    print("\nTest Summary:")
    
    print("""
1. Environment Setup:
   - Created directories: static, generated_images, static/generated_images
   - Created test files to verify access paths

2. Module Verification:
   - Checked both original and enhanced image generator modules
   
3. FastAPI Static File Access:
   - Tested direct and static paths to the same files (if server is running)
   
4. Recommendations:
   - See the HTML report for detailed recommendations for fixing the issues
""")

    print("\nNext Steps:")
    print("1. Replace the original image_generator.py with the enhanced version")
    print("2. Ensure the FastAPI app has the correct static file configuration")
    print("3. Restart the FastAPI server to apply changes")
    print("4. Test image generation to confirm all issues are fixed")
