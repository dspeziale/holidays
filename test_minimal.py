import requests

url = "https://www.skyscanner.it/g/fenryr/v1/inputorigin"
params = {
    "query": "Roma",
    "locale": "it-IT",
    "market": "IT"
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.skyscanner.it/"
}

print(f"Testing {url} with minimal headers...")
try:
    r = requests.get(url, params=params, headers=headers, timeout=10)
    print(f"Status Code: {r.status_code}")
    print(f"Response: {r.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
