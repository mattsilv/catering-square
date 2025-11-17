import json

with open('/tmp/menu.json', 'r') as f:
    content = f.read()
    if content.startswith('HTTP/'):
        json_start = max(content.find('{'), content.find('['))
        if json_start != -1:
            content = content[json_start:]

    data = json.loads(content)
    print(f'Data type: {type(data)}')

    if isinstance(data, dict):
        print(f'\nTop-level keys: {list(data.keys())}')

        # Look for menu items or categories
        for key in ['menu', 'items', 'categories', 'products', 'salads']:
            if key in data:
                print(f'\nFound "{key}" key with {len(data[key])} items')
                if data[key] and isinstance(data[key], list):
                    print(f'First item sample:')
                    print(json.dumps(data[key][0], indent=2)[:500])
