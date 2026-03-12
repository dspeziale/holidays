from swoop import search

results = search("FCO", "SEA", "2026-06-15")

if results.results:
    f = results.results[0].legs[0].itinerary.flights[0]
    print("--- FULL ATTRIBUTES OF FLIGHT ---")
    for attr in dir(f):
        if not attr.startswith('__'):
            try:
                val = getattr(f, attr)
                print(f"{attr}: {val}")
            except Exception as e:
                print(f"{attr}: Error - {e}")
