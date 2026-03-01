import requests
import json

BASE_URL = 'http://localhost:8000/api'

def login():
    resp = requests.post(f'{BASE_URL}/token/', data={'username': 'admin', 'password': 'password123'})
    if resp.status_code != 200:
        print("Login failed:", resp.text)
        return None
    return resp.json()['access']

def create_achievement(token):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    data = {
        'achievement_type': 'paper',
        'title': 'Test Achievement Auto',
        'journal': 'Test Journal',
        'publish_date': '2025-01-01',
        'project': None  # Optional
    }
    resp = requests.post(f'{BASE_URL}/research/achievements/', headers=headers, json=data)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == '__main__':
    token = login()
    if token:
        create_achievement(token)
