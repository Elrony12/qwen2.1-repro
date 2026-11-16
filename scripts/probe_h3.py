# -*- coding: utf-8 -*-
"""Probe the RUNNING ComfyUI on this box: which H3/T8 nodes exist, and what params the
existing H3 workflows actually use (resolution / frames / steps / loras)."""
import json, os, glob, urllib.request

SERVER = "http://127.0.0.1:6006"

with urllib.request.urlopen(SERVER + "/object_info", timeout=120) as r:
    oi = json.load(r)
names = sorted(k for k in oi if any(s in k.lower() for s in ("minimax", "t8", "h3")))
print("TOTAL NODES:", len(oi), "| H3/T8 NODES:", len(names))
print("NODES:", " ".join(names))

KEYS = ("width", "height", "frames", "frame_count", "length", "steps", "cfg", "fps",
        "motion", "camera", "unet_name", "clip_name", "vae_name", "lora_name", "strength",
        "seed", "sampler_name", "scheduler", "batch_size", "res_multistep", "upscale",
        "audio", "guide", "frame_rate", "duration", "blocks", "tile")

WF = "/root/autodl-tmp/ComfyUI/user/default/workflows"
hits = []
for p in glob.glob(WF + "/**/*.json", recursive=True):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        continue
    s = json.dumps(d, ensure_ascii=False)
    if "MiniMaxH3" not in s:
        continue
    nodes = d.get("nodes") or []
    kinds = {n.get("type") for n in nodes}
    mode = "I2V" if "MiniMaxH3ImageToVideo" in kinds else (
           "T8AV" if any(k and k.endswith("T8") for k in kinds) else "OTHER")
    params = {}
    for n in nodes:
        for ik, v in (n.get("inputs") or {}).items():
            if isinstance(v, (int, float, str)) and any(k in ik.lower() for k in KEYS):
                params[f'{n.get("type","?")}.{ik}'] = v
    hits.append((mode, os.path.relpath(p, WF), sorted(n.get("type") for n in nodes if n.get("type","").startswith("MiniMax")), params))

print("\nH3 WORKFLOWS FOUND:", len(hits))
for mode, rel, kinds, params in hits[:12]:
    print("\n### %s  %s" % (mode, rel))
    print("  nodes:", " ".join(kinds))
    for k, v in list(params.items())[:22]:
        print("   ", k, "=", v)
