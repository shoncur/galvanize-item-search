import requests
from base import BASE_URL

response = requests.get(f'{BASE_URL}/items')
print(response)