# -*- coding: utf-8 -*-
"""Submit n character T2I jobs to the local ComfyUI (Qwen-Image 2.1) and wait."""
import json, time, urllib.request, uuid, sys

SERVER = "http://127.0.0.1:6006"

BASE = """一张完整独立的9:16竖版真实彩色照片，仅一位明确28岁的韩国成年女性真人cosplayer，普通生活中有辨识度的不完美美女，真实成人面部比例，皮肤有自然毛孔、小雀斑和轻微晒红，不是动漫人物、不是3D渲染，不要过度磨皮。角色是{name}，仅保留这一角色标志性的{features}，不混合其他角色。服装完整穿着，自然合身，不强调胸部，不是内衣或泳装。
夏日明亮海边，她正试图双手拉住一只巨大鲜艳的彩色菱形风筝。海风突然增强，将手中的风筝绳拉得笔直，细绳从双手连续连接到上方风筝。她的身体明显向后倾斜抵抗拉力，双脚前后分开踩稳沙地，膝盖微弯。长发和衣摆被风吹向同一个方向，风筝尾部彩带也顺风飘动；面颊被风轻轻挤压，双眼紧闭，嘴巴张开开怀大笑，夸张有趣的真实表情。
低机位广角CCD数码相机生活抓拍，镜头拉远，画面完整容纳头、身体、双脚、双手以及上方的大风筝，人物在画面下方，风筝占上方天空，蓝色海面和浪花在后景。鲜艳夏日色彩，CCD彩色柔焦、轻微颗粒、高光轻微溢出，主体可辨识而头发和衣角带自然动感。自然完整穿着，姿态有重量和拉力。单幅连续构图，单个人、单只风筝，禁止拼图、多宫格、分屏、海报拼接、文字和水印。"""

NEG = ("拼图，多宫格，分屏，拼接海报，文字，水印，多个人，动漫脸，卡通，塑料皮肤，"
       "过度磨皮，额外肢体，畸形手指，裸露，内衣，泳装")

CHARS = [
    ("hutao",   "胡桃 Hu Tao",     "深棕色长双马尾、黑色梅花纹圆礼帽、深褐色绣梅花短外套配红色内衬、黑色短裤与腿环、梅花造型挂饰"),
    ("ganyu",   "甘雨 Ganyu",      "淡蓝紫色长发、红黑相间的麒麟角、颈间金色铃铛、白紫黑配色的礼服轮廓、金色腰饰"),
    ("firefly", "流萤 Firefly",    "银灰色长直发与黑色发带、白色长外套式的连衣裙轮廓、蓝绿色渐变裙摆与银色饰品"),
    ("zero2",   "零二 Zero Two",   "粉色长发与红色发带、额前红色小角、红白配色的驾驶服轮廓、白色手套"),
    ("ai",      "星野爱 Ai",       "紫粉色长发、紫色星形瞳孔、白黑红配色的偶像舞台服、发间蝴蝶结发饰"),
]


def graph(idx, name, features, seed):
    return {
        "1": {"class_type": "UNETLoader",
              "inputs": {"unet_name": "qwen_image_2.1_int8_convrot.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "qwen3vl_8b_w4a8.safetensors", "type": "qwen_image", "device": "default"}},
        "3": {"class_type": "VAELoader",
              "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"}},
        "5": {"class_type": "TextEncodeQwenImage21",
              "inputs": {"clip": ["2", 0], "vae": ["3", 0],
                         "prompt": BASE.format(name=name, features=features),
                         "negative_prompt": NEG, "resolution": 1024}},
        "6": {"class_type": "KSampler",
              "inputs": {"model": ["1", 0], "seed": seed, "steps": 25, "cfg": 1.0,
                         "sampler_name": "euler", "scheduler": "simple",
                         "positive": ["5", 0], "negative": ["5", 1],
                         "latent_image": ["9", 0], "denoise": 1.0}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["3", 0]}},
        "8": {"class_type": "SaveImage",
              "inputs": {"images": ["7", 0], "filename_prefix": "qwen21_beach_cosplay2/%02d_%s" % (idx, name.split()[0])}},
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
    for i, (slug, name, feat) in enumerate(CHARS, 1):
        seed = int(time.time() * 1000) % 1000000000 + i
        g = graph(i, name, feat, seed)
        r = post("/prompt", {"prompt": g, "client_id": cid})
        jobs.append((r["prompt_id"], slug, seed))
        print("queued", slug, r["prompt_id"], "seed", seed, flush=True)

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
