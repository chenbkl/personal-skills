#!/usr/bin/env bash
#
# 只读地比对本地与远程版本（不拉取、不改动任何文件）。
# 用作个人 skill 的"理杏仁式"按需自更新检测：commit SHA = 版本号。
#
# 退出码：
#   0 = 已是最新 / 无法判断（离线等）→ 调用方应照常继续，绝不阻塞
#   10 = 有新版本（本地 HEAD ≠ 远程 HEAD）→ 调用方可提示用户运行 update.sh
#
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$HERE" rev-parse --show-toplevel 2>/dev/null)" || { echo "not-a-git-repo"; exit 0; }

branch="$(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null)" || exit 0
local_sha="$(git -C "$REPO" rev-parse HEAD 2>/dev/null)" || exit 0

# 轻量网络往返：只问远程 HEAD 的 SHA，不下载对象。失败（离线/无 key）则静默放过。
remote_sha="$(git -C "$REPO" ls-remote origin -h "refs/heads/$branch" 2>/dev/null | cut -f1)"
if [ -z "$remote_sha" ]; then
  echo "offline-or-unknown: 无法获取远程版本，跳过检测"
  exit 0
fi

if [ "$local_sha" = "$remote_sha" ]; then
  echo "up-to-date: personal-skills 已是最新 (${local_sha:0:7})"
  exit 0
fi

echo "⚠ update-available: personal-skills 有新版本"
echo "   本地 ${local_sha:0:7}  ≠  远程 ${remote_sha:0:7} (分支 $branch)"
echo "   运行 update.sh 即可更新（git pull --autostash + install.sh）"
exit 10
