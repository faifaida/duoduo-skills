#!/usr/bin/env bash
# 播客同步总入口：确保 headless Chrome -> 同步 Apple Podcasts RSS -> 同步喜马拉雅。
# 用法：bash run_sync.sh
# 后台运行，绝不占屏幕。只动 Apple 的 GitHub RSS 与喜马拉雅专辑 127170840。
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
PY=/Users/Zhuanz/.workbuddy/binaries/python/envs/default/bin/python

# 1) 自愈 headless Chrome（9222 不在线才启动，绝不碰用户真实 Chrome）
bash "$HERE/ensure_headless.sh" || { echo "[run] headless 启动失败，中止"; exit 1; }

# 2) Apple Podcasts RSS 同步
echo "========== [1/2] Apple Podcasts RSS =========="
"$PY" "$HERE/apple_rss_sync.py"
APPLE_RC=$?

# 3) 喜马拉雅上传同步
echo "========== [2/2] 喜马拉雅 =========="
"$PY" "$HERE/ximalaya_sync.py"
XM_RC=$?

echo "----------------------------------------"
echo "Apple RC=$APPLE_RC | Ximalaya RC=$XM_RC"
if [ "$APPLE_RC" = "0" ] && [ "$XM_RC" = "0" ]; then
  echo "DONE"
else
  echo "DONE_WITH_WARNINGS"
fi
exit 0
