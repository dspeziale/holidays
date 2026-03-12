import sys
from swoop import search
from datetime import datetime

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

def run_search(origin, dest, date, return_date=None):
    print(f"\n🔍 RICERCA: {origin} {'↔' if return_date else '→'} {dest} il {date} {f'(Ritorno: {return_date})' if return_date else ''}")
    
    try:
        if return_date:
            results = search(origin, dest, date, return_date=return_date)
        else:
            results = search(origin, dest, date)
            
        print(f"✅ Trovati {len(results.results)} risultati.\n")
        
        for i, option in enumerate(results.results[:5]): # Primi 5 per brevità
            print(f"=== OPZIONE {i+1} - PREZZO: ${option.price} ===")
            
            for j, leg in enumerate(option.legs):
                iti = leg.itinerary
                if not iti: continue
                
                print(f"  LEG {j+1}: {leg.origin} -> {leg.destination} ({format_duration(iti.travel_time)})")
                print(f"    Scali: {iti.stop_count}")
                
                if hasattr(iti, 'flights') and iti.flights:
                    for k, f in enumerate(iti.flights):
                        dep = f"{getattr(f, 'departure_airport_code', '??')} ({format_time(getattr(f, 'departure_time', (0,0)))})"
                        arr = f"{getattr(f, 'arrival_airport_code', '??')} ({format_time(getattr(f, 'arrival_time', (0,0)))})"
                        air = f"{getattr(f, 'airline_name', 'Unknown')} ({getattr(f, 'airline_code', '??')}{getattr(f, 'flight_number', '')})"
                        
                        print(f"      {k+1}. {dep} -> {arr} | {air}")
                        
                        layover = getattr(f, 'layover_duration', 0)
                        if layover:
                            print(f"         [Attesa: {format_duration(layover)}]")
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ Errore durante la ricerca: {e}")

if __name__ == "__main__":
    # Esempio default se non passati argomenti
    o = sys.argv[1] if len(sys.argv) > 1 else "FCO"
    d = sys.argv[2] if len(sys.argv) > 2 else "SEA"
    t1 = sys.argv[3] if len(sys.argv) > 3 else "2026-06-15"
    t2 = sys.argv[4] if len(sys.argv) > 4 else None
    
    run_search(o, d, t1, t2)
