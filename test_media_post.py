import urllib.request
import json
import socket

def test_post():
    url = 'http://localhost:8000/media/'
    data = {
        'title': 'Manual Test Media',
        'url': 'https://images.unsplash.com/photo-1541701494587-cb58502866ab',
        'type': 'image',
        'owner_id': 1,
        'community_id': 1
    }
    encoded_data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=encoded_data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            print(f"STATUS: {response.getcode()}")
            print(f"RESPONSE: {response.read().decode()}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_post()
