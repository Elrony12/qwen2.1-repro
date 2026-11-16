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
git clone https://github.com/Emory12/qwen2.1-repro.git
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

启动 ComfyUI（镜像内已配置）：

```bash
cd /root/autodl-tmp/ComfyUI
python main.py --listen 0.0.0.0 --port 6006
```

另开终端执行验证脚本，提交一次 Qwen-Image 2.1 文生图任务并等待完成：

```bash
cd /root/qwen2.1-repro
python scripts/qwen21_gen.py
```

预期输出：队列显示 5 个角色任务（`hutao/ganyu/firefly/zero2/ai`），随后逐个打印 `DONE`，图片保存在 ComfyUI 的 `output/qwen21_beach_cosplay2/` 目录。

其他示例：

```bash
python scripts/h3_run.py submit     # 提交 H3 图生视频任务
python scripts/h3_run.py poll <id>  # 轮询任务状态
```

## 目录说明

```
scripts/              API 调用脚本（qwen21_* 文生图、h3_* 视频、probe_* 探针）
workflows/api/        API 格式工作流 JSON（guhuozai / lingbao / t8 系列）
workflows/ui-comfyui/ ComfyUI UI 格式工作流（云绘基础工作流：Flux/Qwen/LTX2/MiniMax-H3 等）
docs/MODELS.md        模型下载来源与放置位置
```
