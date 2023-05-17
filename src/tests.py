import requests
from login import arena_session_id
from base import BASE_URL

matches = [
    '020-00156-000',
    '100-00092-001',
    '110-00092-026',
    '110-00092-027',
    '890-00010-000',
]

for item in matches:
    item_url = f'{BASE_URL}/items?number={item}'
    item_headers = {'arena_session_id':f'{arena_session_id}', 'Content-Type': 'application/json'}
    item_response = requests.get(item_url, headers=item_headers)
    lifecycle_phase = item_response.json()['results'][0]['lifecyclePhase']['name']
    print(f'{item} | {lifecycle_phase}')