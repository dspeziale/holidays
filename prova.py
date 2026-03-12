import datetime
from skyscanner import SkyScanner
from skyscanner.types import CabinClass, SpecialTypes
import sys

# Initialize the client with more retries
scanner = SkyScanner(
    locale="it-IT",
    currency="EUR",
    market="IT",
    max_retries=30,
    retry_delay=3
)

print("Searching for origin airport (Roma)...")
try:
    airports = scanner.search_airports("Roma")
    if not airports:
        print("No airports found for Roma.")
        sys.exit(1)
    
    origin = airports[0]
    print(f"Found Origin: {origin.title} ({origin.skyId})")

    print("Searching for destination airport (Londra)...")
    dest_airports = scanner.search_airports("Londra")
    if not dest_airports:
        print("No airports found for Londra.")
        sys.exit(1)
        
    destination = dest_airports[0]
    print(f"Found Destination: {destination.title} ({destination.skyId})")

    # Search for flights
    depart_date = datetime.datetime(2025, 8, 15)
    print(f"Searching flights for {depart_date}...")

    response = scanner.get_flight_prices(
        origin=origin,
        destination=destination,
        depart_date=depart_date,
        cabinClass=CabinClass.ECONOMY,
        adults=1
    )

    print(f"Search status: {response.search_status}")
    if response.itineraries:
        print(f"Found {len(response.itineraries)} itineraries.")
        for i, itin in enumerate(response.itineraries[:3]):
            print(f"Itinerary {i+1}: Price {itin['price']['amount']} {itin['price']['currency']}")
    else:
        print("No itineraries found.")

except Exception as e:
    print(f"An error occurred: {e}")