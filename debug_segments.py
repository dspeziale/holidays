from swoop import search
import pprint

results = search("FCO", "SEA", "2026-06-15")

if results.results:
    iti = results.results[0].legs[0].itinerary
    if iti:
        print("--- ITINERARY ---")
        for attr in ['airline_names', 'departure_date', 'departure_time', 'travel_time', 'stop_count']:
            print(f"{attr}: {getattr(iti, attr, 'N/A')}")
        
        if hasattr(iti, 'flights') and iti.flights:
            print("\n--- FIRST FLIGHT SEGMENT ---")
            f = iti.flights[0]
            for attr in dir(f):
                if not attr.startswith('_'):
                    print(f"{attr}: {getattr(f, attr)}")
            
            if len(iti.flights) > 1:
                print("\n--- LAST FLIGHT SEGMENT ---")
                f = iti.flights[-1]
                for attr in dir(f):
                    if not attr.startswith('_'):
                        print(f"{attr}: {getattr(f, attr)}")
