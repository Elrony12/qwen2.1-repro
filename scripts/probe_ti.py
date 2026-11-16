# -*- coding: utf-8 -*-
"""What task_types / image inputs does MiniMaxH3AudioConditioningT8 accept?
Need to know whether one graph can carry a hard FIRST FRAME plus an identity reference."""
import json, urllib.request

SERVER = "http://127.0.0.1:6006"
for node in ("MiniMaxH3AudioConditioningT8", "MiniMaxH3ImageToVideo", "MiniMaxH3AddGuide"):
    try:
        with urllib.request.urlopen(SERVER + "/object_info/" + node, timeout=60) as f:
            oi = json.load(f)[node]["input"]
    except Exception as e:
        print(node, "-> ERR", e)
        continue
    print("\n#### %s" % node)
    for group in ("required", "optional"):
        for name, spec in (oi.get(group) or {}).items():
            t = spec[0] if isinstance(spec, list) else "?"
            opts = spec[1].get("options") if (isinstance(spec, list) and len(spec) > 1
                                              and isinstance(spec[1], dict)) else None
            if opts is None and isinstance(t, list):
                opts = t
            line = "  %-9s %-34s %s" % (group, name, t if not opts else "")
            if opts:
                line += "ENUM[" + ",".join(str(o) for o in opts[:14]) + "]"
            print(line)
