# -*- coding: utf-8 -*-
"""Kite-beach girl, three exposure levels (subtle / L2 gust / L3 upskirt) on Qwen-Image 2.1."""
import json, time, urllib.request, uuid

SERVER = "http://127.0.0.1:6006"

HEAD = ("一张完整独立的9:16竖版真实彩色照片，仅一位成年女性真人模特，外表是16岁左右的高中JK少女，"
        "真实成人面部比例，身形纤细单薄、锁骨明显、四肢细长，皮肤白皙通透，不是动漫、不是3D渲染，不过度磨皮。"
        "黑色长直发及腰、额前齐刘海被海风吹乱，头顶架着橙色镜片太阳镜，金色小圆环耳环。"
        "她是不折不扣的年轻女性。脸很小，标准V字鹅蛋脸、尖下巴，五官精致柔和，"
        "大眼睛弯弯含水，鼻梁小巧，脸颊饱满白嫩透出淡淡粉色，气质甜美可爱、少女感十足。"
        "夏日明亮的海滩上，她双手紧握红色风筝线轮举在胸前抵抗拉力，"
        "身体微微后倾，双腿一前一后踩稳沙地，头微微歪向一侧，"
        "对着镜头眯起眼睛甜甜地笑，露出整齐洁白的牙齿和浅浅梨涡，笑起来眼睛弯成月牙，灿烂治愈。")

TAIL = ("细绳从双手连续向右上延伸，连接到一只飘在蓝天白云里的彩虹拼色菱形风筝，"
        "风筝图案是戴草帽的骷髅交叉骨海盗旗。后景是浪花白沫、海岸线青山和模糊的游客遮阳伞，"
        "正午强烈阳光，白皙皮肤上有清晰高光，鲜艳饱和色彩，单幅连续构图，单人单风筝，"
        "无拼图无文字无水印。")

BODY = {
    "cuteg": (
        "她穿白色短袖JK制服衬衫，最上面两颗纽扣敞开，露出纤细锁骨，衣料有真实的棉布褶皱和纹理；"
        "下身是藏青色百褶JK短裙，裙摆完好垂落覆盖，走光也不露，脚穿白色小腿袜和棕色乐福鞋。"
        "相机站在沙滩上与她平视，35mm镜头，全身入镜，画面下缘到脚踝，人物占画面中部，风筝在上方天空。"
        "自然明亮的正午侧顺光，阳光从右上方照下，脸颊、锁骨和手臂上有柔和高光，"
        "沙地投下清晰的影子，逆光方向头发边缘有一圈真实轮廓光；"
        "皮肤有真实毛孔、细小绒毛和自然血色，衬衫被风吹出立体褶皱，画面有轻微胶片颗粒，"
        "整体如真实相机直出的海边生活照。"),
}

LEVELS = ["full"]
VARIANTS = [f"cuteg_{t}" for t in "abc"]

NEG = ("拼图，多宫格，分屏，文字，水印，多个人，动漫，卡通，3D渲染，塑料皮肤，过度磨皮，"
       "额外肢体，畸形手指，儿童，幼女，小学生，肌肉感，晒黑小麦肤色，仰拍，低机位，"
       "走光，露内裤，裙底特写，油画感，HDR过重，过度锐化，涂抹感")


def graph(idx, key, seed):
    return {
        "1": {"class_type": "UNETLoader",
              "inputs": {"unet_name": "qwen_image_2.1_int8_convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "qwen3vl_8b_w4a8.safetensors", "type": "qwen_image", "device": "default"}},
        "3": {"class_type": "VAELoader",
              "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
        "5": {"class_type": "TextEncodeQwenImage21",
              "inputs": {"clip": ["2", 0], "vae": ["3", 0],
                         "prompt": HEAD + BODY[key.rsplit("_", 1)[0]] + TAIL,
                         "negative_prompt": NEG, "resolution": 1024}},
        "6": {"class_type": "KSampler",
              "inputs": {"model": ["1", 0], "seed": seed, "steps": 25, "cfg": 1.0,
                         "sampler_name": "euler", "scheduler": "simple",
                         "positive": ["5", 0], "negative": ["5", 1],
                         "latent_image": ["9", 0], "denoise": 1.0}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["3", 0]}},
        "8": {"class_type": "SaveImage",
              "inputs": {"images": ["7", 0], "filename_prefix": "qwen21_kite_cuteg/%02d_%s" % (idx, key)}},
        "9": {"class_type": "EmptySD3LatentImage",
              "inputs": {"width": 864, "height": 1536, "batch_size": 1}},
    }


def post(path, payload):
    req = urllib.request.Request(SERVER + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def get(path):
    with urllib.request.urlopen(SERVER + path, timeout=60) as r:
        return json.loads(r.read())


def main():
    cid = uuid.uuid4().hex
    jobs = []
    for i, key in enumerate(VARIANTS, 1):
        seed = int(time.time() * 1000) % 1000000000 + i
        r = post("/prompt", {"prompt": graph(i, key, seed), "client_id": cid})
        jobs.append((r["prompt_id"], key, seed))
        print("queued", key, r["prompt_id"], "seed", seed, flush=True)

    pending = {j[0]: j for j in jobs}
    while pending:
        time.sleep(3)
        for pid in list(pending):
            try:
                h = get("/history/" + pid)
            except Exception as e:
                print("poll err", e, flush=True)
                continue
            if pid in h and h[pid].get("status", {}).get("completed"):
                outs = h[pid].get("outputs", {})
                files = [f for n in outs.values() for f in n.get("images", [])]
                print("DONE", pending[pid][1], json.dumps(files, ensure_ascii=False), flush=True)
                del pending[pid]
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
