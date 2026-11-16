# -*- coding: utf-8 -*-
"""Rice-paddy JK girl, frontal standing version, 3 seeds, 3:4 on Qwen-Image 2.1."""
import json, time, urllib.request, uuid

SERVER = "http://127.0.0.1:6006"

PROMPT = (
    "一张完整独立的3:4竖版真实彩色照片，半身近景人像，一位18岁左右的亚洲少女，"
    "画面下缘到腰部以上，人物占据画面大部分，脸在画面中上部。"
    "鹅蛋小脸、下巴略尖，细长的内双眼睛、眼尾微微下垂、瞳孔深黑，眉毛细而平直，"
    "鼻梁细直鼻头小巧，唇形偏薄唇色淡粉，左侧眼睛下方有一颗小痣。"
    "额前薄薄的空气刘海，两侧垂着碎发，黑色长直发及腰披在肩后。肤色白皙通透，"
    "皮肤有真实毛孔和自然血色，不过度磨皮，不是动漫不是3D渲染。表情安静、清冷、微微侧头看镜头。"
    "身穿白色短袖JK制服衬衫，领口系深绿色领结，领子干净利落，下身墨绿格纹百褶短裙的上缘可见。"
    "黄昏蓝调时刻，背景是虚化的抽穗水稻田、白色矮栅栏、远处木栈道桥和蓝紫渐变暮色天空。"
    "柔和漫射自然光，整体冷蓝紫调，35mm胶片颗粒，浅景深背景虚化，日系清新写真风格。"
    "相机与人脸平视，85mm人像镜头，单幅连续构图，单人，无文字无水印。"
)

NEG = ("拼图，多宫格，分屏，文字，水印，多个人，动漫，卡通，3D渲染，塑料皮肤，过度磨皮，"
       "额外肢体，畸形手指，畸形手，坏腿，油画面，HDR过重，过度锐化，涂抹感，低分辨率，"
       "侧面，背面，回眸，侧身，坐姿，仰拍，俯拍，裙底特写，幼女，小学生")

N = 2


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
              "inputs": {"images": ["7", 0], "filename_prefix": "qwen21_face_cu/%02d_cu" % idx}},
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
