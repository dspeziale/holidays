from swoop import search

results = search("FCO", "SEA", "2026-06-15")

if results.results:
    leg = results.results[0].legs[0]
    print("TripLeg attributes:")
    for attr in dir(leg):
        if not attr.startswith('__'):
            print(f"- {attr}")
    
    if leg.itinerary:
        print("\nItinerary attributes:")
        for attr in dir(leg.itinerary):
            if not attr.startswith('__'):
                print(f"- {attr}")
        
        if hasattr(leg.itinerary, 'segments') and leg.itinerary.segments:
            print("\nSegment attributes:")
            for attr in dir(leg.itinerary.segments[0]):
                if not attr.startswith('__'):
                    print(f"- {attr}")
