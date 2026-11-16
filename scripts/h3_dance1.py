# -*- coding: utf-8 -*-
"""H3 I2VA: paddy JK girl does the douyin hip-sway dance, 8 s, 3:4, v2 quality recipe.
usage:  python h3_dance1.py submit | poll <id>
"""
import json, sys, time, urllib.request, urllib.error

SERVER = "http://127.0.0.1:6006"
BASE = "/root/autodl-tmp/ComfyUI/user/default/workflows/api_originals/comfyui_prompt_A(1).json"
FIRST = "paddy_girl_orig.png"
DURATION_S = 8
MEGAPIXELS_PASS1 = 0.4
PREFIX = "video/paddy_dance"

PROMPT = """参考图索引：图1:稻田JK少女
竖版3:4一镜到底真实彩色电影感视频。图1中的少女就是画面里唯一的人：18岁JK少女，棕色长发齐刘海、一条长麻花辫垂在左肩前、辫尾黑色缎带蝴蝶结，白色短袖JK衬衫、深绿色领结、墨绿格纹百褶短裙、白色过膝袜、粉蝴蝶结鞋，双手握手机挎珍珠链条黑包。场景是图1的黄昏蓝调稻田：白栅栏、亮灯民居、木栈道桥、山脊风车、蓝紫渐变天空。
动作时间线（原地跳一段轻柔的扭扭舞，脚不移动位置）：0到2秒她把手机交给左手垂在身前，身体缓缓向右侧转成半侧背对镜头的姿态，右手抬起、食指轻轻点在自己下巴上，做出俏皮的表情；2到5秒她的胯部左右连续摆动，身体随之S形扭动，墨绿格纹百褶裙摆随胯部摆动一层层甩开再落下，珍珠包链跟着节奏晃动，麻花辫和碎发随扭动摆动，重心在双腿间交替，过膝袜的袜口随膝盖起伏；她的视线越过肩膀回望镜头，眨一下眼；5到6秒她右手食指从下巴缓缓滑到嘴唇前，扭腰的幅度加大一拍然后忽然停住，做出定格感；6到8秒她缓缓转回正面面向镜头，双手捏住裙摆两侧轻轻压下，歪头浅笑定格收尾，稻浪和云恢复缓慢移动。
镜头：与人物平视的固定机位，画面包含全身从头顶到双脚，只有极轻微的手持呼吸感，不推拉不摇移不切换。
光照质感：比常规压暗半档的曝光，浓郁蓝调冷蓝紫调，民居暖灯形成冷暖对比，皮肤有真实毛孔与自然血色、不过度磨皮，35mm胶片颗粒，电影胶片色调，背景轻微虚化。"""

NEG = ("拼图，多宫格，分屏，文字，水印，多个人，动漫，卡通，3D渲染，塑料皮肤，过度磨皮，"
       "额外肢体，畸形手指，畸形手，坏腿，油画面，HDR过重，过度锐化，涂抹感，低分辨率，"
       "跳跃，大步移动，旋转跳离原地，手臂大幅挥舞，芭蕾，街舞地板动作，镜头推拉，摇移，"
       "背景更换，幼女，小学生")

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
        for k in list(ins):
            if k.startswith("ref_images."):
                ins.pop(k)
        ins["task_type"] = "I2VA"
        ins["first_frame"] = ["117", 0]
    g["117"]["inputs"]["image"] = FIRST
    g["107"]["inputs"]["value"] = PROMPT
    g["27"]["inputs"]["value"] = DURATION_S
    g["1"]["inputs"]["vae_name"] = "minimax_h3_video_vae_int8_convrot.safetensors"
    for nid in ("52", "53"):
        g[nid]["inputs"]["strength_model"] = 0.0
    g["48"]["inputs"]["strength_model"] = 0.7
    g["49"]["inputs"]["strength_model"] = 0.35
    up = g["13"]["inputs"]
    up["size_mode"] = "target_megapixels"
    up["target_megapixels"] = 1.3
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
    g["126"]["inputs"]["seed"] = int(time.time() * 1000) % 10**15
    print("ASPECT", pick, flush=True)
    return g


def submit():
    g = build()
    try:
        r = req("/prompt", {"prompt": g, "client_id": "paddyd"})
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
            print("MSG", json.dumps(m, ensure_ascii=False)[:500])
    for k, v in (h.get("outputs") or {}).items():
        for f in v.get("images", []) + v.get("videos", []) + v.get("gifs", []):
            print("OUT", json.dumps(f, ensure_ascii=False))
    if not h:
        print("NOT FINISHED (queue_remaining=%s)" % req("/queue").get("queue_remaining"))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "submit"
    submit() if mode == "submit" else poll(sys.argv[2])
