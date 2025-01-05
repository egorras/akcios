from datetime import datetime, timedelta
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
    
    def is_this_week(catalog: Dict[str, Any]) -> bool:
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        valid_from = datetime.fromisoformat(catalog['valid_from']).date()
        return start_of_week <= valid_from <= end_of_week

    stores = ['ALDI', 'LIDL']
    all_catalogs = []
    
    # Load catalogs from all stores
    for store in stores:
        catalogs = load_catalogs(store)
        for catalog in catalogs:
            catalog['store'] = store
            catalog['store_logo'] = f'images/{store}.png'
            catalog['is_active'] = check_active(catalog)
            catalog['is_this_week'] = is_this_week(catalog)
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
    <title>Akcios</title>
    <link rel="icon" href="/images/favicon.svg" type="image/svg+xml">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .clickable-row {
            cursor: pointer;
            transition: all 0.2s;
        }
        .clickable-row:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .this-week {
            background-color: rgba(59, 130, 246, 0.05);
            font-weight: 500;
        }
        .this-week:hover {
            background-color: rgba(59, 130, 246, 0.1);
        }
    </style>
</head>
<body class="min-h-screen p-4 md:p-8">
    <div class="max-w-7xl mx-auto space-y-8">
        <div class="bg-white rounded-lg shadow overflow-hidden">
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <tbody class="bg-white divide-y divide-gray-200">
    """
    
    # Add catalog rows
    for catalog in all_catalogs:
        store_logo = catalog.get('store_logo', '')
        store_name = catalog.get('store', '')
        is_active = catalog.get('is_active', False)
        is_this_week = catalog.get('is_this_week', False)
        url = catalog.get('url', '#')
        
        row_classes = []
        row_classes.append("clickable-row")
        if is_this_week:
            row_classes.append("this-week")
        if is_active:
            row_classes.append("hover:bg-green-50")
        else:
            row_classes.append("hover:bg-gray-50")
        
        html += f"""
                        <tr onclick="window.open('{url}', '_blank')" class="{' '.join(row_classes)}">
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