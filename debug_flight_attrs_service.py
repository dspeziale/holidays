from swoop import search

results = search("FCO", "SEA", "2026-06-15")
if results.results:
    f = results.results[0].legs[0].itinerary.flights[0]
    print(f"Flight attrs: {dir(f)}")
    for a in ['airline_code', 'airline_name', 'departure_airport_code', 'arrival_airport_code']:
        print(f"{a}: {getattr(f, a, 'MISSING')}")
