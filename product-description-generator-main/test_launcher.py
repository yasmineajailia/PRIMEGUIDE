import os
import webbrowser
import subprocess
import time
import sys

def main():
    print("Product Description Generator - Test Launcher")
    print("============================================")
    
    # Determine the base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the FastAPI server batch file
    api_server_path = os.path.join(base_dir, "run_fastapi.bat")
    
    # Path to HTML client
    html_client_path = os.path.join(base_dir, "image_description_client.html")
    
    # Path to test script
    test_script_path = os.path.join(base_dir, "test_static_path_access.py")
    
    print("1. Starting FastAPI server...")
    
    # Start the FastAPI server in a new console
    if os.name == 'nt':  # Windows
        api_process = subprocess.Popen(["start", "cmd", "/k", api_server_path], 
                                       shell=True)
    else:  # Unix/Linux
        api_process = subprocess.Popen(["gnome-terminal", "--", "bash", api_server_path])
    
    print("2. Waiting for server to start (5 seconds)...")
    time.sleep(5)
    
    # Open HTML client in browser
    print(f"3. Opening HTML client: {html_client_path}")
    webbrowser.open(f"file://{os.path.abspath(html_client_path)}")
    
    # Run the test script
    print(f"4. Running static path access test: {test_script_path}")
    test_result = subprocess.run([sys.executable, test_script_path], 
                                 capture_output=True, text=True)
    
    # Print test results
    print("\nTest Results:")
    print(test_result.stdout)
    
    print("\nTest Complete!")
    print("You can now interact with the application using the browser client.")
    print("The FastAPI server is running in a separate terminal window.")
    print("Press Ctrl+C to exit this launcher (the server will continue running).")
    
    # Keep the launcher running until user presses Ctrl+C
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting launcher. The server is still running in its own window.")

if __name__ == "__main__":
    main()
