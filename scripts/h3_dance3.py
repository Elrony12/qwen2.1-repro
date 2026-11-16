# -*- coding: utf-8 -*-
"""H3 I2VA: paddy face-swap (Hybrid: first frame + face ref) does xcx hand dance, 8 s, 3:4, v2 quality recipe.
usage:  python h3_dance1.py submit | poll <id>
"""
import json, sys, time, urllib.request, urllib.error

SERVER = "http://127.0.0.1:6006"
BASE = "/root/autodl-tmp/ComfyUI/user/default/workflows/api_originals/comfyui_prompt_A(1).json"
FIRST = "paddy_girl_orig.png"
FACEREF = "paddy_face_ref.png"
DURATION_S = 8
MEGAPIXELS_PASS1 = 0.4
PREFIX = "video/paddy_face_dance"

PROMPT = """参考图索引：图1:脸部参考
竖版3:4一镜到底真实彩色电影感视频。首帧中的JK少女就是画面里唯一的人，她的脸和发型替换为图1：白皙小圆脸、大而圆的黑眼睛、厚齐刘海、黑色长双马尾垂在身体两侧、白色蕾丝发带，表情淡淡的无辜又清冷；服装保持首帧不变：白色短袖JK衬衫、深绿色领结、墨绿格纹百褶短裙、白色过膝袜、粉蝴蝶结鞋，双手握手机挎珍珠链条黑包；场景保持首帧不变：黄昏蓝调稻田、白栅栏、亮灯民居、木栈道桥、山脊风车、蓝紫渐变天空。
动作时间线（原地跳一段酷酷的手势舞，脚不移动位置，表情全程酷淡、眼神微眯、嘴角很浅的笑）：0到1秒她把手机换到左手垂在身前腾出右手，1到2秒她双腿重心左右交替，胯跟着节拍小幅摆动，双手握成松拳在胸前一前一后轻点，像慢速跑步摆臂，黑色双马尾随节拍轻轻甩动；2到4秒左手抬到肩侧、拇指与食指捏合向外弹了一下，右手手肘在身前向后摆，身体随之扭出S形；4到5.5秒她双手在胸前交叉比出V字，然后双臂向两侧缓缓打开，掌心向外，格纹裙摆随身体摆动甩起；5.5到7秒双手收回握拳、拇指朝自己轻点胸口两下，耸肩，头微微歪向一侧；7到8秒双臂向两侧张开定格，掌心向外，浅笑收尾，稻浪和云恢复缓慢移动。
镜头：与人物平视的固定机位，画面包含全身从头顶到双脚，只有极轻微的手持呼吸感，不推拉不摇移不切换。
光照质感：比常规压暗半档的曝光，浓郁蓝调冷蓝紫调，民居暖灯形成冷暖对比，皮肤有真实毛孔与自然血色、不过度磨皮，35mm胶片颗粒，电影胶片色调，背景轻微虚化。"""

NEG = ("拼图，多宫格，分屏，文字，水印，多个人，动漫，卡通，3D渲染，塑料皮肤，过度磨皮，"
       "额外肢体，畸形手指，畸形手，坏腿，油画面，HDR过重，过度锐化，涂抹感，低分辨率，"
       "跳跃，大步移动，旋转跳离原地，手臂大幅挥舞，芭蕾，街舞地板动作，镜头推拉，摇移，"
       "背景更换，幼女，小学生，麻花辫，棕色头发，女仆装，蓝色裙子，猫耳发饰，黄色手机壳，熊图案，镜子反光，自拍构图")

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
        ins["task_type"] = "Hybrid"
        ins["first_frame"] = ["117", 0]
        ins["ref_images.ref_image_0"] = ["200", 0]
    g["117"]["inputs"]["image"] = FIRST
    g["200"] = {"class_type": "LoadImage", "inputs": {"image": FACEREF}}
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
