from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import List, Dict, Any
import logging
import re

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

def minify_css():
    """Minify CSS file."""
    css_file = Path('styles.css')
    minified = ''
    
    with open(css_file, 'r', encoding='utf-8') as f:
        css = f.read()
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)
        # Remove whitespace
        css = re.sub(r'\s+', ' ', css)
        # Remove spaces around special characters
        css = re.sub(r'\s*([\{\}\:\;\,])\s*', r'\1', css)
        minified = css.strip()
    
    # Write minified version
    with open('styles.min.css', 'w', encoding='utf-8') as f:
        f.write(minified)
    
    return 'styles.min.css'

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

    # Reorder groups to show current date first
    today = datetime.now().date()
    reordered_groups = {}
    
    # First, find the current week's group
    current_week_key = None
    for date_range, group in sorted_groups.items():
        if group['is_this_week']:
            current_week_key = date_range
            reordered_groups[date_range] = group
            break
    
    # Then add all other groups
    for date_range, group in sorted_groups.items():
        if date_range != current_week_key:
            reordered_groups[date_range] = group

    # Minify CSS before generating HTML
    css_file = minify_css()  # This creates and returns 'styles.min.css'

    # Generate HTML with minified CSS
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow">
    <meta name="googlebot" content="noindex, nofollow">
    <title>Akciós</title>
    <link rel="preload" href="{css_file}" as="style">
    <link rel="stylesheet" href="{css_file}">
    <link rel="icon" href="/images/favicon.png" type="image/png" sizes="32x32">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta http-equiv="x-ua-compatible" content="ie=edge">
</head>
<body>
    <div class="container">
    """

    for date_range, group in reordered_groups.items():
        card_class = "card" + (" this-week" if group['is_this_week'] else "")
        
        html += f'<div class="{card_class}"><div class="card-header">'
        html += f'<div class="date-range">{date_range}</div></div>'
        html += '<div class="card-content">'
        
        for catalog in group['catalogs']:
            store_name = catalog['store']
            store_class = f"store-button {store_name.lower()}"
            html += f'<a href="{catalog["url"]}" target="_blank" class="{store_class}">'
            html += f'<span>{store_name}</span></a>'
        
        html += '</div></div>'

    html += f"""
        <div class="footer">
            Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
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