import os
import webbrowser
import http.server
import socketserver
import threading
import time

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Path to the HTML file
html_file_path = os.path.join(current_dir, "image_description_client.html")

# Define handler for HTTP server
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=current_dir, **kwargs)

# Function to start the HTTP server
def start_server():
    PORT = 8080
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Serving at port {PORT}")
        print(f"Open your browser to http://localhost:{PORT}/image_description_client.html")
        httpd.serve_forever()

# Start the server in a separate thread
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

# Wait a bit for the server to start
time.sleep(1)

# Open the default web browser
webbrowser.open(f"http://localhost:8080/image_description_client.html")

# Keep the main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Server stopped.")
