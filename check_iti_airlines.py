from swoop import search

results = search("FCO", "SEA", "2026-06-15")
if results.results:
    iti = results.results[0].legs[0].itinerary
    print(f"Itinerary airline_code: {iti.airline_code} (type: {type(iti.airline_code)})")
    print(f"Itinerary airline_names: {iti.airline_names} (type: {type(iti.airline_names)})")
    
    if iti.flights:
        f = iti.flights[0]
        print(f"First Flight attrs: {[a for a in dir(f) if not a.startswith('_')]}")
