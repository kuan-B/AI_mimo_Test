import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(base, "data.json"), "r", encoding="utf-8"))
existing = set(os.listdir(os.path.join(base, "posters")))

PAGE_SIZE = 10
for page in [6, 8, 9, 10]:
    start = (page - 1) * PAGE_SIZE
    end = min(start + PAGE_SIZE, len(data))
    print(f"--- Page {page} (#{start+1}-#{end}) ---")
    for i in range(start, end):
        m = data[i]
        p = m.get("poster", "").strip()
        fname = os.path.basename(p) if p else "(empty)"
        exists = fname in existing if p else False
        status = "OK" if exists else "MISSING"
        print(f"  [{i+1}] {m['movieName']}: {status} -> {fname}")
