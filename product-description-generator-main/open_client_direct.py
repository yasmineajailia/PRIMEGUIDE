import os
import webbrowser

# Get the absolute path to the HTML file
current_dir = os.path.dirname(os.path.abspath(__file__))
html_file_path = os.path.join(current_dir, "image_description_client.html")

# Convert to file URL format
file_url = f"file:///{html_file_path.replace(os.sep, '/')}"

# Open the HTML file in the default browser
print(f"Opening {html_file_path}")
webbrowser.open(file_url)
