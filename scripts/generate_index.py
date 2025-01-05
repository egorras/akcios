from datetime import datetime
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def format_date_range(valid_from: str, valid_to: str) -> str:
    """Format date range in a more readable way."""
    from_date = datetime.fromisoformat(valid_from)
    to_date = datetime.fromisoformat(valid_to)
    
    if from_date.year == to_date.year:
        return f"{from_date.year} {from_date.strftime('%m-%d')} → {to_date.strftime('%m-%d')}"
    return f"{from_date.strftime('%Y %m-%d')} → {to_date.strftime('%Y %m-%d')}"

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
    def check_active(catalog: Dict[str, Any]) -> bool:
        today = datetime.now().date()
        valid_from = datetime.fromisoformat(catalog['valid_from']).date()
        valid_to = datetime.fromisoformat(catalog['valid_to']).date()
        return valid_from <= today <= valid_to

    stores = ['ALDI', 'LIDL']
    all_catalogs = []
    
    # Load catalogs from all stores
    for store in stores:
        catalogs = load_catalogs(store)
        for catalog in catalogs:
            catalog['store'] = store
            catalog['store_logo'] = f'images/{store}.png'
            catalog['is_active'] = check_active(catalog)
            catalog['date_range'] = format_date_range(catalog['valid_from'], catalog['valid_to'])
        all_catalogs.extend(catalogs)
    
    # Sort catalogs by valid_from date
    all_catalogs.sort(key=lambda x: x.get('valid_from', ''), reverse=True)
    
    # Generate HTML
    html = """
<!DOCTYPE html>
<html lang="en" class="bg-gray-100">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <meta name="googlebot" content="noindex, nofollow">
    <title>Store Catalogs</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="min-h-screen p-4 md:p-8">
    <div class="max-w-7xl mx-auto space-y-8">
        <div class="bg-white rounded-lg shadow overflow-hidden">
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Store</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Valid Period</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Link</th>
                        </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
    """
    
    # Add catalog rows
    for catalog in all_catalogs:
        store_logo = catalog.get('store_logo', '')
        store_name = catalog.get('store', '')
        is_active = catalog.get('is_active', False)
        
        row_class = "hover:bg-green-50" if is_active else "hover:bg-gray-50"
        button_class = "bg-green-600 hover:bg-green-700 focus:ring-green-500" if is_active else "bg-blue-600 hover:bg-blue-700 focus:ring-blue-500"
        
        html += f"""
                        <tr class="{row_class}">
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="flex items-center">
                                    <div class="flex-shrink-0 h-8 w-8">
                                        <img class="h-8 w-8 object-contain" src="{store_logo}" alt="{store_name}">
                                    </div>
                                    <div class="ml-4">
                                        <div class="text-sm font-medium text-gray-900">{store_name}</div>
                                    </div>
                                </div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap">
                                <div class="text-sm text-gray-900">{catalog['date_range']}</div>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm">
                                <a href="{catalog.get('url', '#')}" 
                                   target="_blank"
                                   class="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white {button_class} focus:outline-none focus:ring-2 focus:ring-offset-2">
                                    View
                                </a>
                            </td>
                        </tr>
        """
    
    html += """
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="text-center text-sm text-gray-500">
            Last updated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """
        </div>
    </div>
</body>
</html>
    """
    
    # Write the HTML file
    output_file = Path('index.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    logger.info(f"Generated index.html with {len(all_catalogs)} catalogs")

if __name__ == '__main__':
    generate_html() 