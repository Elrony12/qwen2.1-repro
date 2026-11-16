import json, urllib.request
d = json.load(urllib.request.urlopen("http://127.0.0.1:6006/object_info"))
target = "H3_T8_DANCE_MOTION"
hits = []
for n, spec in d.items():
    io = (spec.get("input") or {})
    for g in ("required", "optional"):
        for ik, ispec in (io.get(g) or {}).items():
            if isinstance(ispec, list) and ispec and str(ispec[0]) == target:
                hits.append((n, g, ik))
print("CONSUMERS of", target)
for h in hits:
    print(" ", *h)
print("--- nodes with Dance in name ---")
for k in sorted(d):
    if "dance" in k.lower():
        req = list(((d[k].get("input") or {}).get("required") or {}).keys())
        opt = list(((d[k].get("input") or {}).get("optional") or {}).keys())
        print(" ", k, "| req:", req[:10], "| opt:", opt[:10])
