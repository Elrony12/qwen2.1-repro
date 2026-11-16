# Qwen-Image 2.1 / MiniMax-H3 工作流复现环境

基于 AutoDL 保存镜像 `qwen2.1`（`image-6e5c29b75`）的 ComfyUI 生成环境，配套本仓库的 API 调用脚本与工作流 JSON，可在 AutoDL Art 上一键复现 Qwen-Image 2.1 文生图、MiniMax-H3 图生视频等工作流。

## 基本环境

| 项目 | 版本 |
| --- | --- |
| 框架 | PyTorch 2.1.2 |
| Python | 3.10 |
| CUDA | 11.8 |
| 运行时 | ComfyUI（本地 API 监听 `127.0.0.1:6006`） |

## 构建过程

### 代码 Clone

```bash
cd /root
git clone https://github.com/Elrony12/qwen2.1-repro.git
cd qwen2.1-repro
```

### 依赖安装

镜像已预装 PyTorch / CUDA / ComfyUI 及所需自定义节点，一般无需重装。如需补齐 Python 依赖：

```bash
pip install -r requirements.txt
```

### 模型准备

脚本引用的量化模型（均为 int8 / nvfp4 量化版，以适配显存）需下载到 ComfyUI 模型目录。模型体积较大，不随仓库分发，请按 `docs/MODELS.md` 中的来源下载：

- `qwen_image_2.1_int8_convrot.safetensors`
- `qwen3vl_8b_w4a8.safetensors`
- `qwen_image_2.1_vae_bf16.safetensors`
- `minimax_h3_*` 系列（H3 视频工作流）

下载后放入 `/root/autodl-tmp/ComfyUI/models/` 下对应子目录（`unet` / `clip` / `vae` 等）。

## 环境验证代码

平台 clone 本仓库后，在镜像内执行以下命令即可完成验证（秒级完成，无需 GPU、模型、网络或 ComfyUI 服务）：

```bash
cd /root/qwen2.1-repro
python verify_env.py
```

预期输出：

```
Python: 3.10.x
PyTorch: 2.1.2
CUDA (torch 编译版本): 11.8
CUDA 可用: True
[OK] 镜像环境验证通过：PyTorch 2.1.2 / CUDA 11.8 已就绪
```

完整生图流程（可选，需先按上文下载模型并启动 ComfyUI）：

```bash
cd /root/autodl-tmp/ComfyUI && python main.py --listen 0.0.0.0 --port 6006
cd /root/qwen2.1-repro && python scripts/qwen21_gen.py
```

## 目录说明

```
scripts/              API 调用脚本（qwen21_* 文生图、h3_* 视频、probe_* 探针）
workflows/api/        API 格式工作流 JSON（guhuozai / lingbao / t8 系列）
workflows/ui-comfyui/ ComfyUI UI 格式工作流（云绘基础工作流：Flux/Qwen/LTX2/MiniMax-H3 等）
docs/MODELS.md        模型下载来源与放置位置
verify_env.py         零依赖环境验证入口（平台执行此脚本）
```
