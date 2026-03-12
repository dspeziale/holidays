import sys
import os
from unittest.mock import MagicMock

# Aggiungi il path del progetto al sys.path
sys.path.append(os.path.abspath('.'))

def test_skyscanner_service():
    print("Testing Skyscanner Service...")
    
    # Mock Flask current_app
    app_mock = MagicMock()
    app_mock.config = {}
    
    # Importiamo il service (dopo aver mockato se necessario, o usando il file appena creato)
    from app.services import skyscanner_service
    
    # Test URL generation
    url = skyscanner_service.get_skyscanner_url("ROM", "LON", "2026-06-15")
    print(f"Generated URL: {url}")
    assert "skyscanner.it/trasporti/voli/rom/lon/260615/" in url
    
    # Test search_flights (demo mode)
    from flask import Flask
    app = Flask(__name__)
    with app.app_context():
        results = skyscanner_service.search_flights("ROM", "LON", "2026-06-15")
        print(f"Results found: {len(results)}")
        for r in results:
            print(f" - {r['airline_name']}: {r['price']} {r['currency']} ({r['skyscanner_url']})")
        assert len(results) > 0
        assert results[0]['origin'] == "ROM"
    
    print("✅ Skyscanner Service test passed!")

if __name__ == "__main__":
    test_skyscanner_service()
