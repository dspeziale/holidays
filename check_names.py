from swoop import search, to_dict
import pprint

results = search("FCO", "SEA", "2026-06-15")

if results.results:
    # Convert the first result to a dict and see if there are names anywhere
    data = to_dict(results.results[0])
    pprint.pprint(data)

# Check search parameters too
print("\nSearch Params:")
pprint.pprint(to_dict(results.search_params))
