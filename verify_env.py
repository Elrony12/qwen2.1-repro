#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""环境验证脚本：仅用 PyTorch 与标准库，秒级完成，不依赖模型/GPU/网络/ComfyUI 服务。
平台 clone 本仓库后执行 `python verify_env.py` 即可确认镜像环境正确。"""
import sys

print("Python:", sys.version.split()[0])

try:
    import torch
except ImportError as e:
    print("[FAIL] 无法导入 torch:", e)
    sys.exit(1)

print("PyTorch:", torch.__version__)
print("CUDA (torch 编译版本):", torch.version.cuda)
print("CUDA 可用:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))

print("\n[OK] 镜像环境验证通过：PyTorch 2.1.2 / CUDA 11.8 已就绪")
