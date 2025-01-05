from datetime import datetime
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def load_catalogs(store_name: str) -> List[Dict[str, Any]]:
    """Load catalogs from store-specific index file."""
    index_file = Path(f'data/index-{store_name.lower()}.json')
    if not index_file.exists():
        logger.warning(f"No index file found for {store_name}")
        return []
    
    with open(index_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_html():
    """Generate index.html with combined catalog data."""
    stores = ['ALDI', 'LIDL']
    all_catalogs = []
    
    # Load catalogs from all stores
    for store in stores:
        catalogs = load_catalogs(store)
        for catalog in catalogs:
            catalog['store'] = store
            catalog['store_logo'] = f'images/{store}.png'
        all_catalogs.extend(catalogs)
    
    # Sort all catalogs by valid_from date
    all_catalogs.sort(key=lambda x: x.get('valid_from', ''), reverse=True)
    
    # Generate HTML
    html = """
<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <meta name="googlebot" content="noindex, nofollow">
    <title>Akciós</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f5f5f5;
        }
        tr:hover {
            background-color: #f9f9f9;
        }
        a {
            color: #0066cc;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .store-logo {
            height: 30px;
            width: auto;
            vertical-align: middle;
            margin-right: 10px;
        }
        td {
            vertical-align: middle;
        }
        .store-cell {
            white-space: nowrap;
        }
    </style>
</head>
<body>
    <table>
        <thead>
            <tr>
                <th>Store</th>
                <th>Title</th>
                <th>Valid From</th>
                <th>Valid To</th>
                <th>Link</th>
            </tr>
        </thead>
        <tbody>
    """
    
    # Add catalog rows
    for catalog in all_catalogs:
        valid_from = catalog.get('valid_from', '').split('T')[0]
        valid_to = catalog.get('valid_to', '').split('T')[0]
        store_logo = catalog.get('store_logo', '')
        store_name = catalog.get('store', '')
        
        logo_html = f'<img src="{store_logo}" alt="{store_name}" class="store-logo">' if store_logo else ''
        
        html += f"""
            <tr>
                <td class="store-cell">
                    {logo_html}
                    {store_name}
                </td>
                <td>{catalog.get('title', '')}</td>
                <td>{valid_from}</td>
                <td>{valid_to}</td>
                <td>
                    <a href="{catalog.get('url', '#')}" target="_blank">View Catalog</a>
                </td>
            </tr>
        """
    
    html += """
        </tbody>
    </table>
</body>
</html>
    """
    
    # Write the HTML file to root directory instead of data
    output_file = Path('index.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"Generated index.html with {len(all_catalogs)} catalogs")

if __name__ == '__main__':
    generate_html() 