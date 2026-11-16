# -*- coding: utf-8 -*-
"""H3 Ref2VA single-ref video from the paddy-field JK still, 8 s, 3:4.
usage:  python h3_paddy.py submit | poll <id>
"""
import json, sys, urllib.request, urllib.error

SERVER = "http://127.0.0.1:6006"
BASE = "/root/autodl-tmp/ComfyUI/user/default/workflows/api_originals/comfyui_prompt_A(1).json"
IMAGE = "paddy_girl_orig.png"
DURATION_S = 8
MEGAPIXELS_PASS1 = 0.4
SCALE_BY = 1.5
PREFIX = "video/paddy_girl"

PROMPT = """参考图索引：图1:稻田JK少女
竖版3:4一镜到底真实彩色视频，图1中的少女就是画面里唯一的人：18岁左右的JK少女，脸很小是标准鹅蛋脸、大眼睛温柔，棕色长发齐刘海，一条长麻花辫垂在一侧肩前、辫尾系黑色缎带蝴蝶结，穿白色短袖JK制服衬衫、深绿色领结、墨绿格纹百褶短裙、白色过膝袜，双手在小腹前握着一部手机，胯侧挎着那只黑色菱格珍珠链条小包。黄昏蓝调时刻，她正面站在图1同一片已抽穗的水稻田中央直视镜头，背景保持图1的白色矮栅栏、左侧亮灯民居、右侧木栈道桥、远处山脊风力发电机和蓝紫渐变天空。
动作时间线：0到2秒她平静地注视着镜头，嘴角很轻地向上浮起，脸颊两侧碎发和辫尾被晚风吹动；2到4秒她绽出浅浅的甜笑，眼睛弯起，周围稻田的稻穗随晚风一阵一阵起伏摇摆，珍珠包链轻轻晃动，衬衫领结和裙摆被风吹得轻微飘动；4到6秒她抬起右手把一缕碎发别到耳后，手指纤细清晰，然后缓缓放下手重新与左手一起握住手机；6到8秒她保持浅浅微笑看向镜头，天空薄云缓慢移动，远处民居灯光与停在路边的白色汽车微微闪烁。
镜头：与人物平视的全身构图固定机位，画面下缘到脚部，人物居中，只有手持拍摄的轻微呼吸感晃动，极其缓慢地向她推近一点点，不切换镜头，不上摇不下摇。
光照质感：黄昏蓝调柔和漫射自然光，整体冷蓝紫调，天空略带粉紫，稻穗呈深绿带金黄，皮肤白皙通透有真实血色，轻微胶片颗粒，日系清新青春写真氛围。"""

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
    for nid in ("95", "96"):
        ins = g[nid]["inputs"]
        for i in range(1, 5):
            ins.pop("ref_images.ref_image_%d" % i, None)
        ins["ref_images.ref_image_0"] = ["117", 0]
    g["117"]["inputs"]["image"] = IMAGE
    g["107"]["inputs"]["value"] = PROMPT
    g["27"]["inputs"]["value"] = DURATION_S
    g["54"]["inputs"]["value"] = SCALE_BY
    g["1"]["inputs"]["vae_name"] = "minimax_h3_video_vae_int8_convrot.safetensors"
    oi = req("/object_info/ResolutionSelector")
    spec = oi["ResolutionSelector"]["input"]["required"].get("aspect_ratio", [])
    enums = spec[0] if (spec and isinstance(spec[0], list)) else (
        spec[1].get("options", []) if len(spec) > 1 else [])
    pick = None
    for want in ("3:4", "2:3", "9:16"):
        hits = [e for e in enums if isinstance(e, str) and want in e]
        if hits:
            pick = hits[0]
            break
    if not pick:
        raise SystemExit("no portrait enum in %r" % enums[:12])
    g["29"]["inputs"]["aspect_ratio"] = pick
    g["29"]["inputs"]["megapixels"] = MEGAPIXELS_PASS1
    g["115"]["inputs"]["filename_prefix"] = PREFIX
    print("ASPECT", pick, flush=True)
    return g


def submit():
    g = build()
    try:
        r = req("/prompt", {"prompt": g, "client_id": "paddyg"})
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
    print("STATE", json.dumps({"completed": st.get("completed"), "status_str": st.get("status_str")},
                              ensure_ascii=False))
    for m in (st.get("messages") or []):
        print("MSG", json.dumps(m, ensure_ascii=False)[:600])
    for k, v in (h.get("outputs") or {}).items():
        for f in v.get("images", []) + v.get("videos", []) + v.get("gifs", []):
            print("OUT", json.dumps(f, ensure_ascii=False))
    if not h:
        q = req("/queue")
        print("QUEUED/JOB:", json.dumps(q.get("queue_remaining")))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "submit"
    submit() if mode == "submit" else poll(sys.argv[2])
