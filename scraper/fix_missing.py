import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(base, "data.json")
data = json.load(open(data_path, "r", encoding="utf-8"))

for m in data:
    p = m.get("poster", "").strip()
    if p and not os.path.exists(os.path.join(base, p)):
        # Find duplicate with working poster
        for m2 in data:
            if m2["movieName"] == m["movieName"] and m2 is not m:
                p2 = m2.get("poster", "").strip()
                if p2 and os.path.exists(os.path.join(base, p2)):
                    m["poster"] = p2
                    print(f"Fixed: {m['movieName']} ({m['year']}) -> {p2}")

with open(data_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
with open(os.path.join(base, "data.js"), "w", encoding="utf-8") as f:
    f.write("const INLINE_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")

missing = sum(1 for m in data if m.get("poster", "").strip() and not os.path.exists(os.path.join(base, m["poster"])))
print(f"Total: {len(data)} movies, {missing} missing posters")
