# -*- coding: utf-8 -*-
"""Dump the node contract of an API-format H3 graph so we know exactly which fields to patch."""
import json, sys, glob, os

files = sorted(glob.glob("/root/autodl-tmp/ComfyUI/user/default/workflows/api_originals/*.json"))
print("API-FORMAT FILES:", [os.path.basename(f) for f in files])
target = sys.argv[1] if len(sys.argv) > 1 else (files[0] if files else None)
d = json.load(open(target, encoding="utf-8"))
g = d.get("prompt") or d
print("\nTARGET:", target, "| nodes:", len(g))
for nid in sorted(g, key=lambda x: int(x) if x.isdigit() else 0):
    n = g[nid]
    ct = n.get("class_type")
    ins = n.get("inputs", {})
    scalars = {k: (v[:60] + "…" if isinstance(v, str) and len(v) > 60 else v)
               for k, v in ins.items() if not isinstance(v, list)}
    links = {k: v for k, v in ins.items() if isinstance(v, list)}
    print("%s %-46s" % (nid, ct))
    if scalars:
        print("     in:", json.dumps(scalars, ensure_ascii=False))
    if links:
        print("     <-:", json.dumps(links))
