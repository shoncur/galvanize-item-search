import requests
from requests.exceptions import HTTPError
import getpass
from base import BASE_URL

url = f'{BASE_URL}/login'
headers = {'Content-Type':'application/json'}

login_fail = True
while login_fail:
    try:
        email = input('Enter email: ')
        password = getpass.getpass('Enter password: ')
        data = {
            'email':f'{email}',
            'password':f'{password}'
        }
        response = requests.post(url, headers=headers, json=data)
        arena_session_id = response.json()['arenaSessionId']
        response.raise_for_status()
        login_fail = False
    except HTTPError as http_error:
        print(f'HTTP error occurred: {http_error}')
    except Exception as error:
        print(f'Invalid entry: {error}')
