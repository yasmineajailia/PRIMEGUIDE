import requests
import time
import os
import subprocess
import sys
import signal
import webbrowser
from threading import Thread
import platform

def start_server():
    """Start the FastAPI server"""
    print("Starting test API server...")
    global server_process
    
    if platform.system() == 'Windows':
        # Windows process creation
        server_process = subprocess.Popen(
            ["python", "test_static_paths.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        # Unix process creation
        server_process = subprocess.Popen(
            ["python", "test_static_paths.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid
        )
    
    # Start threads to monitor stdout and stderr
    Thread(target=monitor_output, args=(server_process.stdout, "STDOUT")).start()
    Thread(target=monitor_output, args=(server_process.stderr, "STDERR")).start()

def monitor_output(pipe, name):
    """Monitor and print output from the server process"""
    for line in pipe:
        print(f"[SERVER {name}] {line.strip()}")

def stop_server():
    """Stop the FastAPI server"""
    print("Stopping server...")
    if platform.system() == 'Windows':
        # Windows process termination
        os.kill(server_process.pid, signal.CTRL_BREAK_EVENT)
    else:
        # Unix process termination
        os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
    
    print("Server process terminated")

def test_paths():
    """Test the static and direct image paths"""
    base_url = "http://127.0.0.1:8000"
    
    # Wait for server to start
    print("Waiting for server to start...")
    server_ready = False
    max_attempts = 10
    attempts = 0
    
    while not server_ready and attempts < max_attempts:
        try:
            response = requests.get(f"{base_url}/")
            if response.status_code == 200:
                server_ready = True
                print("Server is ready!")
            else:
                attempts += 1
                time.sleep(1)
        except requests.exceptions.ConnectionError:
            attempts += 1
            time.sleep(1)
    
    if not server_ready:
        print("Failed to connect to server after multiple attempts")
        return False
    
    # Test image paths
    print("\nTesting image paths...")
    try:
        response = requests.get(f"{base_url}/test-images")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            
            direct_url = f"{base_url}{data['direct_url']}"
            static_url = f"{base_url}{data['static_url']}"
            
            print(f"\nDirect URL: {direct_url}")
            print(f"Static URL: {static_url}")
            
            # Test direct access
            direct_response = requests.get(direct_url)
            print(f"Direct access: {'✅ SUCCESS' if direct_response.status_code == 200 else '❌ FAILED'} - Status: {direct_response.status_code}")
            
            # Test static access
            static_response = requests.get(static_url)
            print(f"Static access: {'✅ SUCCESS' if static_response.status_code == 200 else '❌ FAILED'} - Status: {static_response.status_code}")
            
            # Generate HTML to view results
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Static Paths Test</title>
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                    h1, h2 {{ color: #333; }}
                    .path-container {{ margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                    pre {{ background: #f5f5f5; padding: 10px; border-radius: 5px; overflow: auto; }}
                </style>
            </head>
            <body>
                <h1>Static Paths Test Results</h1>
                
                <div class="path-container">
                    <h2>Direct Path</h2>
                    <p><code>{direct_url}</code></p>
                    <p>Status: {direct_response.status_code}</p>
                    <h3>Content:</h3>
                    <pre>{direct_response.text if direct_response.status_code == 200 else 'Not accessible'}</pre>
                </div>
                
                <div class="path-container">
                    <h2>Static Path</h2>
                    <p><code>{static_url}</code></p>
                    <p>Status: {static_response.status_code}</p>
                    <h3>Content:</h3>
                    <pre>{static_response.text if static_response.status_code == 200 else 'Not accessible'}</pre>
                </div>
            </body>
            </html>
            """
            
            # Write HTML file
            html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static_paths_test.html")
            with open(html_path, "w") as f:
                f.write(html_content)
            
            print(f"\nTest results HTML page created: {html_path}")
            
            # Try to open the HTML file
            try:
                webbrowser.open(f"file://{html_path}")
            except:
                print("Could not automatically open the HTML file. Please open it manually.")
            
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    server_process = None
    
    try:
        # Start server
        start_server()
        
        # Wait a bit for the server to initialize
        time.sleep(3)
        
        # Test paths
        test_paths()
        
        # Keep server running for manual testing
        print("\nServer is running. Press Ctrl+C to stop...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nUser interrupted. Stopping server...")
    finally:
        # Stop server
        if server_process:
            stop_server()
