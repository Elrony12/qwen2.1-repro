# -*- coding: utf-8 -*-
"""Shot A: 3 s tilt-up reveal, FL2VA (first frame = full body, last frame = the close-up
that opens shot B), same 9:16 / 736x1312 / 24 fps shape as shot B so they concat cleanly.

usage:  python h3_shotA.py submit   |  python h3_shotA.py poll <id>
"""
import json, sys, time, urllib.request, urllib.error

SERVER = "http://127.0.0.1:6006"
BASE = "/root/autodl-tmp/ComfyUI/user/default/workflows/api_originals/comfyui_prompt_A(1).json"
FIRST = "kite_full.png"     # full body, legs low in frame  -> guarantees the start framing
LAST = "kite_cu_b.png"      # the close-up that opens shot B -> frame-matched seam
DURATION_S = 3
MEGAPIXELS_PASS1 = 0.4
SCALE_BY = 1.5
PREFIX = "video/kite_tilt"

PROMPT = """参考图索引：图1:JK少女
竖版9:16一镜到底真实彩色视频。图1中的少女是画面里唯一的人：16岁左右的JK少女，脸很小是标准V字鹅蛋脸、尖下巴，大眼睛、甜美可爱，黑色长直发、额前齐刘海，头顶架着橙色镜片太阳镜，金色小圆环耳环，穿白色短袖JK制服衬衫，下身藏青色百褶短裙，白色小腿袜和棕色乐福鞋。夏日明亮的海滩，沙地、远处的浪花白沫、海岸线青山和虚化的游客遮阳伞。
镜头：起幅是小腿高度的低机位近景，画面下缘是她的小腿、白色小腿袜和棕色乐福鞋踩在沙地上，脸部在画面上缘之外；镜头平稳地缓缓向上摇并轻微推近，中段经过藏青色百褶裙摆和白色衬衫，落幅停在胸口以上的脸部近景。整个上摇过程一镜到底，不切换镜头，不晃动跳跃。
动作：她双手握着红色风筝线轮，身体几乎不动，只是海风把她的黑色长发和齐刘海吹得大幅飘动、衬衫下摆被吹起，裙摆轻微摆动；她保持安静的微笑，不做大的表情变化。头顶上方那只彩虹拼色菱形风筝（戴草帽的骷髅交叉骨海盗旗）在蓝天里轻轻晃动，一根绷直的细绳从风筝向下连到她的线轮，全画面只有这一根线；背景海浪缓慢推进。
光照质感：正午明亮自然阳光从右上方照下，沙地上有清晰的影子，皮肤白皙通透细腻、干净磨皮感，色彩鲜艳饱和，高光不过曝，画面干净锐利。"""

DROP = ["111", "112", "113", "119", "120", "121", "122", "123", "124", "125"]


def req(path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(SERVER + path, data=data,
                               headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=180) as f:
        return json.loads(f.read())


def build():
    g = json.load(open(BASE, encoding="utf-8"))
    g = g.get("prompt", g)
    for n in DROP:
        g.pop(n, None)
    for nid in ("95", "96"):
        ins = g[nid]["inputs"]
        for k in list(ins):
            if k.startswith("ref_images."):
                ins.pop(k)
        ins["task_type"] = "FL2VA"
        ins["first_frame"] = ["117", 0]
        ins["last_frame"] = ["118", 0]
    g["117"]["inputs"]["image"] = FIRST
    g["118"]["inputs"]["image"] = LAST
    g["107"]["inputs"]["value"] = PROMPT
    g["27"]["inputs"]["value"] = DURATION_S
    g["54"]["inputs"]["value"] = SCALE_BY
    g["1"]["inputs"]["vae_name"] = "minimax_h3_video_vae_int8_convrot.safetensors"
    oi = req("/object_info/ResolutionSelector")
    spec = oi["ResolutionSelector"]["input"]["required"].get("aspect_ratio", [])
    enums = spec[0] if (spec and isinstance(spec[0], list)) else (
        spec[1].get("options", []) if len(spec) > 1 else [])
    portrait = [e for e in enums if isinstance(e, str) and "9:16" in e]
    if not portrait:
        raise SystemExit("no 9:16 enum in %r" % enums[:12])
    g["29"]["inputs"]["aspect_ratio"] = portrait[0]
    g["29"]["inputs"]["megapixels"] = MEGAPIXELS_PASS1
    g["115"]["inputs"]["filename_prefix"] = PREFIX
    g["126"]["inputs"]["seed"] = int(time.time() * 1000) % 10**15
    return g


def submit():
    g = build()
    try:
        r = req("/prompt", {"prompt": g, "client_id": "kitecu"})
    except urllib.error.HTTPError as e:
        print("HTTP", e.code)
        print(e.read().decode("utf-8", "replace")[:4000])
        raise SystemExit(1)
    print("PROMPT_ID", r["prompt_id"])


def poll(pid):
    try:
        h = req("/history/" + pid).get(pid, {})
    except Exception as e:
        print("poll err", e)
        return
    st = h.get("status", {})
    print("STATE", json.dumps({"completed": st.get("completed"), "status_str": st.get("status_str")}))
    for m in (st.get("messages") or []):
        if "success" in str(m[0]) or "error" in str(m[0]).lower():
            print("MSG", json.dumps(m, ensure_ascii=False)[:400])
    for k, v in (h.get("outputs") or {}).items():
        for f in v.get("images", []) + v.get("videos", []) + v.get("gifs", []):
            print("OUT", json.dumps(f, ensure_ascii=False))
    if not h:
        print("NOT FINISHED YET (queue_remaining=%s)" % req("/queue").get("queue_remaining"))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "submit"
    submit() if mode == "submit" else poll(sys.argv[2])
