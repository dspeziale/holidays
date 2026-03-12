from swoop import search

def inspect(obj, name, depth=0):
    indent = "  " * depth
    print(f"{indent}--- {name} (type: {type(obj)}) ---")
    try:
        attrs = [attr for attr in dir(obj) if not attr.startswith('_')]
        print(f"{indent}Attrs: {attrs}")
        for attr in attrs:
            val = getattr(obj, attr)
            if depth < 2: # Evitiamo loop infiniti o troppa verbosità
                if isinstance(val, list) and val:
                    inspect(val[0], f"{attr}[0]", depth + 1)
                elif hasattr(val, "__dict__") or (hasattr(val, 'origin') and not isinstance(val, str)):
                    inspect(val, attr, depth + 1)
    except Exception as e:
        print(f"{indent}Error inspecting {name}: {e}")

results = search("FCO", "SEA", "2026-06-15")

if results.results:
    inspect(results.results[0], "TripOption")

print("\n--- RESULTS WRAPPER ---")
print(dir(results))
