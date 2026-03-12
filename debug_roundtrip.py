from swoop import search

# Testing round-trip search with Swoop
# I'll try adding a return date as the fourth parameter
results = search("FCO", "SEA", "2026-06-15", "2026-06-25")

print(f"REPORT ROUND-TRIP: FCO <-> SEA")
print(f"Voli trovati: {len(results.results)}\n")

for i, option in enumerate(results.results[:2]):
    print(f"=== OPZIONE {i+1} - Prezzo: ${option.price} ===")
    print(f"Numero legs: {len(option.legs)}")
    
    for j, leg in enumerate(option.legs):
        print(f"  LEG {j+1}: {leg.origin} -> {leg.destination} ({leg.date})")
        iti = leg.itinerary
        if iti:
            print(f"    Scali: {iti.stop_count}")
            for k, f in enumerate(iti.flights):
                print(f"      {k+1}. {f.departure_airport_code} -> {f.arrival_airport_code} ({f.airline_name})")
    print("-" * 30)
