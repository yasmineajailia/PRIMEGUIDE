import os
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

class WebsiteGenerator:
    def __init__(self, output_dir="generated_websites"):
        self.output_dir = Path(output_dir)
        self.template_dir = Path("templates")
        self.template_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create basic template if it doesn't exist
        self.create_default_template()
        
        # Set up Jinja environment
        self.env = Environment(loader=FileSystemLoader(str(self.template_dir)))

    def create_default_template(self):
        template_path = self.template_dir / "product_template.html"
        if not template_path.exists():
            template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ product_name }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        .header {
            text-align: center;
            padding: 2rem 0;
            background: #f8f9fa;
            margin-bottom: 2rem;
        }
        .product-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        @media (max-width: 768px) {
            .product-section {
                grid-template-columns: 1fr;
            }
        }
        .product-media {
            text-align: center;
        }
        .product-media img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .product-info {
            padding: 1rem;
        }
        .product-description {
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }
        .product-features {
            background: #f8f9fa;
            padding: 2rem;
            border-radius: 8px;
            margin-top: 2rem;
        }
        .footer {
            text-align: center;
            padding: 2rem;
            background: #f8f9fa;
            margin-top: 2rem;
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>{{ product_name }}</h1>
        </div>
    </header>
    
    <main class="container">
        <section class="product-section">
            <div class="product-media">
                {% if image_path %}
                <img src="{{ image_path }}" alt="{{ product_name }}">
                {% endif %}
                {% if gif_path %}
                <img src="{{ gif_path }}" alt="{{ product_name }} animation">
                {% endif %}
            </div>
            <div class="product-info">
                <div class="product-description">
                    {{ product_description }}
                </div>
                {% if features %}
                <div class="product-features">
                    <h2>Key Features</h2>
                    <ul>
                    {% for feature in features %}
                        <li>{{ feature }}</li>
                    {% endfor %}
                    </ul>
                </div>
                {% endif %}
            </div>
        </section>
    </main>

    <footer class="footer">
        <div class="container">
            <p>Generated on {{ generation_date }}</p>
        </div>
    </footer>
</body>
</html>
"""
            template_path.write_text(template_content)

    def generate_website(self, data):
        """Generate a product website from the given data.
        
        Args:
            data (dict): Dictionary containing:
                - product_name (str): Name of the product
                - product_description (str): Product description text
                - image_path (str, optional): Path to product image
                - gif_path (str, optional): Path to product GIF
                - features (list, optional): List of product features
        
        Returns:
            str: Path to the generated website
        """
        # Create directory for this product
        slug = data['product_name'].lower().replace(' ', '-')
        site_dir = self.output_dir / slug
        site_dir.mkdir(exist_ok=True)

        # Copy media files if they exist
        if data.get('image_path'):
            shutil.copy(data['image_path'], site_dir)
            data['image_path'] = Path(data['image_path']).name
            
        if data.get('gif_path'):
            shutil.copy(data['gif_path'], site_dir)
            data['gif_path'] = Path(data['gif_path']).name

        # Add generation date
        data['generation_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Generate HTML
        template = self.env.get_template('product_template.html')
        html = template.render(**data)

        # Write HTML file
        index_path = site_dir / 'index.html'
        index_path.write_text(html)

        return str(site_dir)
