from swoop import search

results = search("FCO", "SEA", "2026-06-15")

if results.results:
    f = results.results[0].legs[0].itinerary.flights[0]
    print(f"Flight attrs: {dir(f)}")
    print(f"Is airline_name present? {'airline_name' in dir(f)}")
    print(f"Is airline_names present? {'airline_names' in dir(f)}")
    
    try:
        print(f"airline_name value: {f.airline_name}")
    except Exception as e:
        print(f"airline_name error: {e}")
        
    try:
        print(f"airline_names value: {f.airline_names}")
    except Exception as e:
        print(f"airline_names error: {e}")
