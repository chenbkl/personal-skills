#!/usr/bin/env bash
#
# 拉取最新个人 skill 并补齐软链。
# - --autostash：自动暂存本地改动（如 third-party 理杏仁自我更新弄脏的 api-docs），
#   拉完再恢复，避免被"工作区不干净"挡住。
# - --ff-only：只接受快进，避免意外产生合并提交；若远程已分叉则提示手动处理。
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$HERE" rev-parse --show-toplevel)"

echo "==> git pull --ff-only --autostash"
if ! git -C "$REPO" pull --ff-only --autostash; then
  echo
  echo "✗ 拉取失败（可能本地与远程已分叉，或 autostash 恢复时冲突）。"
  echo "  请手动处理：cd \"$REPO\" && git status"
  exit 1
fi

echo
echo "==> 重新建立软链"
bash "$REPO/install.sh"

echo
echo "✓ 更新完成。重启 Claude Code / Codex 以加载最新 skill。"
