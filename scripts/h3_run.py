# -*- coding: utf-8 -*-
"""Take the proven API-format T8 graph, retarget it to a single 9:16 reference image,
8 seconds, and submit / poll on the running ComfyUI.

usage:  python h3_run.py submit      -> prints prompt_id and exits
        python h3_run.py poll <id>   -> prints compact status and any validation error
"""
import json, sys, time, urllib.request, urllib.error

SERVER = "http://127.0.0.1:6006"
BASE = "/root/autodl-tmp/ComfyUI/user/default/workflows/api_originals/comfyui_prompt_A(1).json"
IMAGE = "kite_cu_b.png"
DURATION_S = 8
MEGAPIXELS_PASS1 = 0.4
SCALE_BY = 1.5
PREFIX = "video/kite_cu"

PROMPT = """参考图索引：图1:JK少女
竖版9:16一镜到底真实彩色视频，图1中的少女就是画面里唯一的人：16岁左右的JK少女，脸很小是标准V字鹅蛋脸、尖下巴，大眼睛、甜美可爱，黑色长直发、额前齐刘海，头顶架着橙色镜片太阳镜，金色小圆环耳环，穿白色短袖JK制服衬衫。夏日明亮的海滩，她头顶正上方的蓝天白云里飘着那只彩虹拼色菱形风筝，风筝图案是戴草帽的骷髅交叉骨海盗旗，一根绷直的细绳从风筝向下连到她手里握着的红色风筝线轮，全画面只有这一根线。
动作时间线：0到2秒她微微低头、双眼轻闭，长发被海风吹起大幅飘动；2到4秒她缓缓抬起头睁开眼看向镜头，眉眼弯起；4到6秒绽开灿烂甜笑，露出整齐洁白牙齿和浅浅梨涡；6到8秒右眼俏皮地单眼wink一下随即恢复甜笑，胸口随呼吸轻微起伏，肩膀轻轻晃动。
镜头：近景脸部特写固定机位，只有手持拍摄的轻微呼吸感晃动，极其缓慢地向她推近一点点，不切换镜头，不上摇不下摇。
光照质感：正午明亮自然阳光从右上方照下，脸颊、鼻梁和锁骨有柔和高光，头发边缘有一圈逆光轮廓光，背景海浪、青山和游客遮阳伞虚化；皮肤白皙通透细腻、干净磨皮感，色彩鲜艳饱和，高光不过曝。"""

DROP = ["111", "112", "113", "118", "119", "120", "121", "122", "123", "124", "125"]


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
    # single reference image, repeated nowhere else
    for nid in ("95", "96"):
        ins = g[nid]["inputs"]
        for i in range(1, 5):
            ins.pop("ref_images.ref_image_%d" % i, None)
        ins["ref_images.ref_image_0"] = ["117", 0]
    g["117"]["inputs"]["image"] = IMAGE
    g["107"]["inputs"]["value"] = PROMPT
    g["27"]["inputs"]["value"] = DURATION_S
    g["54"]["inputs"]["value"] = SCALE_BY
    # int8 video VAE keeps the 193-frame decode inside 32 GB
    g["1"]["inputs"]["vae_name"] = "minimax_h3_video_vae_int8_convrot.safetensors"
    # portrait aspect: take the exact enum string the installed node offers
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
    print("STATE", json.dumps({"completed": st.get("completed"), "status_str": st.get("status_str"),
                               "dyna": bool(st.get("dynaflow"))}, ensure_ascii=False))
    for m in (st.get("messages") or []):
        print("MSG", json.dumps(m, ensure_ascii=False)[:600])
    for k, v in (h.get("outputs") or {}).items():
        for f in v.get("images", []) + v.get("videos", []) + v.get("gifs", []):
            print("OUT", json.dumps(f, ensure_ascii=False))
    if not h:
        q = req("/queue")
        print("QUEUED/JOB:", json.dumps(q.get("queue_remaining")), "| running:",
              [j[1] for j in (q.get("queue_pending") or [])][:1] or "see /history")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "submit"
    submit() if mode == "submit" else poll(sys.argv[2])
