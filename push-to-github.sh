#!/usr/bin/env bash
# 一键：用 GitHub Token 新建仓库 + 推送代码
# 用法：在 Git Bash 中运行  bash push-to-github.sh
set -uo pipefail

USER="Emory12"
REPO="qwen2.1-repro"
TOKEN="${GITHUB_TOKEN:-}"

if [ -z "$TOKEN" ]; then
  echo "请先设置 Token：export GITHUB_TOKEN='你的token'"
  echo "获取地址：https://github.com/settings/tokens  ->  Generate new token (classic)"
  echo "勾选权限：repo （全部），生成后复制粘贴"
  exit 1
fi

echo "[1/2] 在 GitHub 新建公开仓库 $USER/$REPO ..."
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/user/repos \
  -d "{\"name\":\"$REPO\",\"description\":\"Qwen-Image 2.1 / MiniMax-H3 workflow repro environment for AutoDL Art\",\"private\":false}" \
  | grep -E '"full_name"|"message"|"html_url"' | head -5

echo "[2/2] 推送代码..."
git remote remove origin 2>/dev/null || true
git remote add origin "https://${TOKEN}@github.com/${USER}/${REPO}.git"
git branch -M main
git push -u origin main
rc=$?

# 推送后把 remote 改回不含 token 的地址，避免明文泄露
git remote set-url origin "https://github.com/${USER}/${REPO}.git"

if [ "$rc" -eq 0 ]; then
  echo ""
  echo "✓ 完成！仓库地址：https://github.com/${USER}/${REPO}"
  echo "现在去 autodl.art 发布页，GitHub 仓库地址框填： ${USER}/${REPO}"
else
  echo "[!] 推送失败，检查 Token 权限是否勾选 repo"
fi
