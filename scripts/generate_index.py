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
    
    # Using %b for abbreviated month name and %d for day
    return f"{from_date.strftime('%b %d')} — {to_date.strftime('%b %d')}"

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
    def is_this_week(catalog: Dict[str, Any]) -> bool:
        today = datetime.now().date()
        valid_from = datetime.fromisoformat(catalog['valid_from']).date()
        valid_to = datetime.fromisoformat(catalog['valid_to']).date()
        # Check if today falls between valid_from and valid_to
        return valid_from <= today <= valid_to

    stores = ['ALDI', 'LIDL', 'SPAR', 'TESCO']
    all_catalogs = []
    
    # Load catalogs from all stores
    for store in stores:
        catalogs = load_catalogs(store)
        for catalog in catalogs:
            catalog['store'] = store
            catalog['is_this_week'] = is_this_week(catalog)
            catalog['date_range'] = format_date_range(catalog['valid_from'], catalog['valid_to'])
        all_catalogs.extend(catalogs)
    
    # Sort catalogs by valid_from date
    all_catalogs.sort(key=lambda x: x.get('valid_from', ''), reverse=True)
    
    # Add this after the stores definition
    store_styles = {
        'ALDI': {
            'bg': 'bg-blue-800',
            'text': 'text-white'
        },
        'LIDL': {
            'bg': 'bg-yellow-400',
            'text': 'text-blue-600'
        },
        'SPAR': {
            'bg': 'bg-red-600',
            'text': 'text-white'
        },
        'TESCO': {
            'bg': 'bg-[#00539F]',
            'text': 'text-white'
        }
    }
    
    # Group catalogs by date range
    date_groups = {}
    for catalog in all_catalogs:
        date_key = catalog['date_range']
        if date_key not in date_groups:
            date_groups[date_key] = {
                'dates': {
                    'valid_from': catalog['valid_from'],
                    'valid_to': catalog['valid_to']
                },
                'catalogs': [],
                'is_this_week': is_this_week(catalog)
            }
        date_groups[date_key]['catalogs'].append(catalog)

    # Sort date groups by valid_from date
    sorted_groups = dict(sorted(
        date_groups.items(),
        key=lambda x: datetime.fromisoformat(x[1]['dates']['valid_from']),
        reverse=True
    ))

    # Generate HTML
    html = """
<!DOCTYPE html>
<html lang="en" class="bg-gray-100 dark:bg-gray-900">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <meta name="googlebot" content="noindex, nofollow">
    <title>Akciós</title>
    <link rel="icon" href="/images/favicon.png" type="image/png">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .store-button {
            transition: all 0.2s;
        }
        .store-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .this-week {
            background-color: rgba(59, 130, 246, 0.1);
            outline: 2px solid rgba(59, 130, 246, 0.2);
        }
        @media (prefers-color-scheme: dark) {
            .this-week {
                background-color: rgba(59, 130, 246, 0.15);
                outline: 2px solid rgba(59, 130, 246, 0.3);
            }
        }
    </style>
</head>
<body class="min-h-screen p-4 md:p-8">
    <div class="max-w-3xl mx-auto space-y-6">
    """

    for date_range, group in sorted_groups.items():
        group_classes = ["bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden"]
        if group['is_this_week']:
            group_classes.append("this-week")

        html += f"""
        <div class="{' '.join(group_classes)}">
            <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{date_range}</div>
            </div>
            <div class="p-4 flex flex-wrap gap-3">
        """

        # Add store buttons
        for catalog in group['catalogs']:
            store_name = catalog['store']
            store_style = store_styles[store_name]
            
            button_classes = [
                "store-button",
                "flex items-center justify-center px-4 py-2 rounded-md",
                store_style['bg'],
                store_style['text'],
                "w-24 font-medium"
            ]
            
            html += f"""
                <a href="{catalog['url']}" 
                   target="_blank" 
                   class="{' '.join(button_classes)}"
                    <span class="text-sm">{store_name}</span>
                </a>
            """

        html += """
            </div>
        </div>
        """

    html += """
        <div class="text-center text-sm text-gray-500 dark:text-gray-400">
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