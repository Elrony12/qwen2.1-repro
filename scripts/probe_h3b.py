# -*- coding: utf-8 -*-
"""Signature table of every H3 workflow on this box: mode, size/frames, steps, loras,
whether it is API-format (directly POSTable), and which VRAM-savers it already wires in."""
import json, glob, os

WF = "/root/autodl-tmp/ComfyUI/user/default/workflows"
NEED = ("MiniMaxH3ImageToVideo", "MiniMaxH3ReferenceToVideo", "MiniMaxH3DualClockSamplerT8")

def vals(node):
    """widget values of a UI-format node, as plain scalars"""
    return [v for v in (node.get("widgets_values") or []) if isinstance(v, (int, float, str, bool))]

rows = []
for p in glob.glob(WF + "/**/*.json", recursive=True):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:
        continue
    api = isinstance(d, dict) and "prompt" in d and "nodes" not in d
    nodes = d.get("nodes") or (d.get("prompt") or {}).values() if api else (d.get("nodes") or [])
    if api:
        kinds = {v.get("class_type") for v in nodes if isinstance(v, dict)}
        sig = {}
        for v in nodes:
            if not isinstance(v, dict):
                continue
            ct = v.get("class_type", "")
            for k, iv in (v.get("inputs") or {}).items():
                if isinstance(iv, (int, float, str)) and any(
                        s in k.lower() for s in ("width", "height", "frame", "length", "step", "fps",
                                                 "unet_name", "lora_name", "vae_name", "clip_name")):
                    sig.setdefault(k, iv)
        loras = [iv for v in nodes if isinstance(v, dict) for k, iv in (v.get("inputs") or {}).items()
                 if k == "lora_name"]
    else:
        kinds = {n.get("type") for n in nodes if isinstance(n, dict)}
        sig, loras = {}, []
        for n in nodes:
            if not isinstance(n, dict):
                continue
            for v in vals(n):
                if isinstance(v, str) and ("safetensors" in v or ".png" in v or ".mp4" in v or ".wav" in v):
                    if "lora" in (n.get("type") or "").lower():
                        loras.append(v)
                    else:
                        sig.setdefault(n.get("type"), []).append(v)
            for v in vals(n):
                if isinstance(v, (int, float)) and n.get("type") in NEED:
                    sig.setdefault(n.get("type"), []).append(v)
    if not (set(kinds) & set(NEED)):
        continue
    mode = ("I2V" if "MiniMaxH3ImageToVideo" in kinds else
            "REF2V" if "MiniMaxH3ReferenceToVideo" in kinds else
            "T8AV" if "MiniMaxH3DualClockSamplerT8" in kinds else "?")
    vram = sorted({k for k in kinds if any(s in (k or "") for s in
                 ("LowVRAM", "VRAMPolicy", "VRAMCleanup", "ExternalBlockSwap", "SolAttn", "SageAttn", "TeaCache"))})
    nimg = len([k for k in kinds if k == "LoadImage"])
    audio = any("Audio" in (k or "") for k in kinds)
    rows.append((mode, os.path.relpath(p, WF), "API" if api else "UI", nimg, audio, vram, loras[:3], sig))

rows.sort()
print("CANDIDATE WORKFLOWS:", len(rows))
for mode, rel, fmt, nimg, audio, vram, loras, sig in rows:
    print("\n%-6s %-6s %-52s refs=%d audio=%s vram=%s" % (mode, fmt, rel, nimg, audio, ",".join(vram) or "-"))
    if loras:
        print("   loras:", " | ".join(loras))
    for k, v in list(sig.items())[:8]:
        s = str(v)
        print("   ", k, "=", s[:150])
