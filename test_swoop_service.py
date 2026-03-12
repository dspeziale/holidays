from flask import Flask
from app.services.skyscanner_service import search_flights
import pprint

app = Flask(__name__)

with app.app_context():
    print("Testing Swoop Service Integration...")
    try:
        results = search_flights("FCO", "SEA", "2026-06-15")
        print(f"Service returned {len(results)} results.")
        if results:
            pprint.pprint(results[0])
    except Exception as e:
        print(f"Service test failed: {e}")
