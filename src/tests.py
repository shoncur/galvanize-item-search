import requests
from login import arena_session_id
from base import BASE_URL

matches = [
    '020-00156-000',
    '100-00092-001',
    '110-00092-026',
    '110-00092-027',
    '890-00010-000',
    # 'CER-00001',
    # 'DCD-00004',
    # 'DCD-00007',
    # 'DCD-00106',
    # 'DCD-00109',
    # 'DDP-00006',
    # 'DHF-00012',
    # 'DHF-00012-DV',
    # 'DHF-00012-RM',
    # 'DHF-00012-SW',
    # 'DMR-00049',
    # 'DP-1001',
    # 'FRM-00077',
    # 'FRM-00145',
    # 'GTI-00005-01',
    # 'GTI-00005-02',
    # 'GTI-00006-01',
    # 'GTI-00007-01',
    # 'LBL-00145-001',
    # 'RSK-00007',
    # 'RSK-00008',
    # 'RSK-00111',
    # 'RSK-00112',
    # 'RSK-00116',
    # 'SOP-00002',
    # 'SOP-00003',
    # 'SOP-00024',
    # 'SOP-00088',
    # 'TP-00046',
    # 'TP-00062',
    # 'TP-00080',
    # 'TP-00596',
    # 'TR-00046',
    # 'TR-00070',
    # 'TR-00071',
    # 'TR-00080',
    # 'TR-00596',
    # 'WRK-00022'
]

for item in matches:
    item_url = f'{BASE_URL}/items?number={item}'
    item_headers = {'arena_session_id':f'{arena_session_id}', 'Content-Type': 'application/json'}
    item_response = requests.get(item_url, headers=item_headers)
    lifecycle_phase = item_response.json()['results'][0]['lifecyclePhase']['name']
    print(f'{item} | {lifecycle_phase}')