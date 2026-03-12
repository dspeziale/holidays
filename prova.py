from swoop import search

def format_time(t):
    if isinstance(t, tuple) and len(t) >= 2:
        return f"{t[0]:02d}:{t[1]:02d}"
    return str(t)

def format_date(d):
    if isinstance(d, tuple) and len(d) >= 3:
        return f"{d[0]}-{d[1]:02d}-{d[2]:02d}"
    return str(d)

def format_duration(m):
    if not m: return "0m"
    h = m // 60
    rem = m % 60
    if h > 0:
        return f"{h}h {rem}m"
    return f"{rem}m"

results = search("FCO", "SEA", "2026-06-15")

print("--- VERSION 4.0 ---")
print(f"REPORT COMPLETO VOLI: FCO -> SEA (2026-06-15)")
print(f"Voli trovati: {len(results.results)}\n")

for i, option in enumerate(results.results):
    print(f"=== OPZIONE {i+1} - Prezzo: ${option.price} ===")
    
    for j, leg in enumerate(option.legs):
        iti = leg.itinerary
        if not iti: continue
        
        last_flight = iti.flights[-1] if (hasattr(iti, 'flights') and iti.flights) else None
        
        print(f"  TRATTA {j+1}: {leg.origin} -> {leg.destination}")
        print(f"    Partenza: {format_date(iti.departure_date)} alle {format_time(iti.departure_time)}")
        if last_flight:
            print(f"    Arrivo:   {format_date(last_flight.arrival_date)} alle {format_time(last_flight.arrival_time)}")
        print(f"    Durata Totale: {format_duration(iti.travel_time)}")
        print(f"    Scali: {iti.stop_count}")
        
        if hasattr(iti, 'flights') and iti.flights:
            print(f"    DETTAGLIO SEGMENTI:")
            for k, f in enumerate(iti.flights):
                # Usiamo gli attributi ora verificati (incluso il nome aeroporto)
                dep_code = getattr(f, 'departure_airport_code', 'N/A')
                dep_name = getattr(f, 'departure_airport_name', '')
                arr_code = getattr(f, 'arrival_airport_code', 'N/A')
                arr_name = getattr(f, 'arrival_airport_name', '')
                
                dep_time = format_time(getattr(f, 'departure_time', 'N/A'))
                arr_time = format_time(getattr(f, 'arrival_time', 'N/A'))
                
                vettore = getattr(f, 'airline_name', 'Unknown')
                
                print(f"      {k+1}. {dep_code} ({dep_name}) [{dep_time}] -> {arr_code} ({arr_name}) [{arr_time}]")
                print(f"         Vettore: {vettore} ({getattr(f, 'airline_code', '??')} {getattr(f, 'flight_number', '????')})")
                print(f"         Aereo: {getattr(f, 'equipment', 'N/A')}")
                print(f"         Durata Volo: {format_duration(getattr(f, 'travel_time', 0))}")
                
                layover = getattr(f, 'layover_duration', 0)
                if layover:
                    print(f"         ATTESA SCALO: {format_duration(layover)}")
    
    print("-" * 50)