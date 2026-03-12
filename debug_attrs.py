from swoop import search

results = search("FCO", "SEA", "2026-06-15")

if results.results:
    option = results.results[0]
    if option.legs:
        leg = option.legs[0]
        print(f"TripLeg attributes: {dir(leg)}")
        if leg.itinerary:
            print(f"Itinerary attributes: {dir(leg.itinerary)}")
            if hasattr(leg.itinerary, 'segments') and leg.itinerary.segments:
                print(f"Segment attributes: {dir(leg.itinerary.segments[0])}")
