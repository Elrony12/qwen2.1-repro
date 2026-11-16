# -*- coding: utf-8 -*-
"""Rice-paddy JK girl, frontal standing version, 3 seeds, 3:4 on Qwen-Image 2.1."""
import json, time, urllib.request, uuid

SERVER = "http://127.0.0.1:6006"

PROMPT = (
    "一张完整独立的3:4竖版真实彩色照片，仅一位成年女性真人模特，外表是18岁左右的JK少女，"
    "真实成人面部比例，身形纤细单薄、四肢细长，皮肤白皙通透，不是动漫、不是3D渲染，不过度磨皮。"
    "棕色长发、额前齐刘海，扎成一条长麻花辫垂在一侧肩前，辫尾系黑色缎带蝴蝶结，脸颊两侧有散落的碎发。"
    "脸很小，标准鹅蛋脸，五官精致柔和，大眼睛温柔地直视镜头，鼻梁小巧，"
    "脸颊白嫩透出淡淡粉色，表情平静温柔，甜美、少女感十足。"
    "黄昏蓝调时刻，她站在一片已抽穗的绿色水稻田里，正面完全朝向镜头直立，全身入镜，"
    "双手在小腹前握着一部手机，手指纤细，手腕戴细手链。"
    "她穿白色短袖JK制服衬衫，领口系深绿色领结，下身墨绿格纹百褶短裙，裙摆自然下垂，"
    "双腿并拢微斜，穿白色过膝长袜，脚上是带粉色蝴蝶结的白色厚底凉鞋。"
    "一只黑色菱格纹珍珠链条腋下小包斜挎在身上，包落在胯侧。"
    "背景是大片抽穗的水稻田，一道白色矮栅栏，左侧远处是亮着灯的民居和停放的白色汽车，"
    "右侧有一座木栈道桥，远处山脊上立着风力发电机，天空是蓝紫渐变的暮色薄云。"
    "相机与她平视，35mm镜头，全身构图，画面下缘到脚部，人物居中，"
    "柔和漫射自然光，整体冷色调，皮肤有真实毛孔和自然血色，画面有轻微胶片颗粒，"
    "日系校园清新写真风格，如真实相机直出的生活照。"
    "单幅连续构图，单人，无拼图无文字无水印。"
)

NEG = ("拼图，多宫格，分屏，文字，水印，多个人，动漫，卡通，3D渲染，塑料皮肤，过度磨皮，"
       "额外肢体，畸形手指，畸形手，坏腿，油画面，HDR过重，过度锐化，涂抹感，低分辨率，"
       "侧面，背面，回眸，侧身，坐姿，仰拍，俯拍，裙底特写，幼女，小学生")

N = 3


def graph(idx, seed):
    return {
        "1": {"class_type": "UNETLoader",
              "inputs": {"unet_name": "qwen_image_2.1_int8_convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "qwen3vl_8b_w4a8.safetensors", "type": "qwen_image", "device": "default"}},
        "3": {"class_type": "VAELoader",
              "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
        "5": {"class_type": "TextEncodeQwenImage21",
              "inputs": {"clip": ["2", 0], "vae": ["3", 0],
                         "prompt": PROMPT,
                         "negative_prompt": NEG, "resolution": 1024}},
        "6": {"class_type": "KSampler",
              "inputs": {"model": ["1", 0], "seed": seed, "steps": 25, "cfg": 1.0,
                         "sampler_name": "euler", "scheduler": "simple",
                         "positive": ["5", 0], "negative": ["5", 1],
                         "latent_image": ["9", 0], "denoise": 1.0}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["3", 0]}},
        "8": {"class_type": "SaveImage",
              "inputs": {"images": ["7", 0], "filename_prefix": "qwen21_paddy_front/%02d_front" % idx}},
        "9": {"class_type": "EmptySD3LatentImage",
              "inputs": {"width": 1152, "height": 1536, "batch_size": 1}},
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
    for i in range(1, N + 1):
        seed = int(time.time() * 1000) % 1000000000 + i
        r = post("/prompt", {"prompt": graph(i, seed), "client_id": cid})
        jobs.append((r["prompt_id"], i, seed))
        print("queued", i, r["prompt_id"], "seed", seed, flush=True)

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
