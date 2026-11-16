import json, urllib.request
d = json.load(urllib.request.urlopen("http://127.0.0.1:6006/object_info"))
for n in ("MiniMaxH3DualModelLongVideoEXPT8", "MiniMaxH3FastH3V2DualModelLongVideoEXPT8"):
    v = d[n]
    print("=====", n)
    print("OUTPUTS", v.get("output"), v.get("output_name"))
    for g in ("required", "optional"):
        for k, spec in ((v.get("input") or {}).get(g) or {}).items():
            print(g, k, json.dumps(spec, ensure_ascii=False)[:150])
