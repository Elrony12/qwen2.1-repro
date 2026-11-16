# 模型下载说明

脚本与工作流依赖以下量化模型。模型文件体积大（数 GB～数十 GB），不随 Git 仓库分发，请按来源下载后放到 ComfyUI 对应目录。

## Qwen-Image 2.1 文生图

| 模型文件 | 类型 | ComfyUI 目录 |
| --- | --- | --- |
| `qwen_image_2.1_int8_convrot.safetensors` | UNET | `models/unet/` |
| `qwen3vl_8b_w4a8.safetensors` | CLIP | `models/clip/` |
| `qwen_image_2.1_vae_bf16.safetensors` | VAE | `models/vae/` |

来源：Comfy-Org 在 HuggingFace / ModelScope 发布的 Qwen-Image 量化版本。可用 `hf-mirror.com` 或 ModelScope 直链配合 `wget -c` 断点续传下载。

## MiniMax-H3 图生视频

| 模型文件 | ComfyUI 目录 |
| --- | --- |
| `minimax_h3_video_vae_int8_convrot.safetensors` | `models/vae/` |
| `minimax_h3_audio_vae_fp32.safetensors` | `models/audio_vae/` |
| `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | `models/clip/` |
| `minimax_h3_hybrid_fl2va_ref2va_b25-49-int8.safetensors` | `models/unet/` |

来源：`Comfy-Org/MiniMax-H3`（HuggingFace / ModelScope）。原实例下载记录保存在 `t8-common-downloads.txt`、`t8-modelscope-downloads.txt`，可作为版本参考。

## 下载后验证

```bash
ls -lh /root/autodl-tmp/ComfyUI/models/unet/ /root/autodl-tmp/ComfyUI/models/clip/ /root/autodl-tmp/ComfyUI/models/vae/
```

确认文件非 0 字节且与上表文件名一致，再运行 `python scripts/qwen21_gen.py` 验证。
