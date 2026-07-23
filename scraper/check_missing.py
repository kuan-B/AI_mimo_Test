import json, os, sys, shutil
sys.stdout.reconfigure(encoding="utf-8")
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(base, "data.json")
posters_dir = os.path.join(base, "posters")

data = json.load(open(data_path, "r", encoding="utf-8"))
existing = set(os.listdir(posters_dir))

# Find movies with missing poster files
for m in data:
    p = m.get("poster", "").strip()
    if p:
        fname = os.path.basename(p)
        if fname not in existing:
            print(f"MISSING: {m['movieName']} ({m['year']}) -> {p}")

# Check for movies with empty poster
no_poster = [m for m in data if not m.get("poster", "").strip()]
if no_poster:
    print(f"\n{len(no_poster)} movies with no poster path:")
    for m in no_poster:
        print(f"  {m['movieName']} ({m['year']})")
