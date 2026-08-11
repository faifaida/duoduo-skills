#!/usr/bin/env bash
# 自愈 headless Chrome：若 9222 不在线则启动；绝不打开可见窗口、绝不 pkill 用户真实 Chrome。
# 使用持久化登录态 /Users/Zhuanz/.xm_headless_profile（含 GitHub / 小宇宙 / 喜马拉雅会话）。
set -u

PROFILE=/Users/Zhuanz/.xm_headless_profile
PORT=9222
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
LOG=/tmp/duoduo_headless_chrome.log

if curl -s --max-time 3 "http://localhost:${PORT}/json/version" >/dev/null 2>&1; then
  echo "[headless] CDP 已在线，无需启动"
  exit 0
fi

echo "[headless] 启动 headless Chrome (--headless=new, 无可见窗口) ..."
# 注意：--headless=new 保证不占屏幕；--user-data-dir 为独立副本，与用户真实 Chrome 隔离。
nohup "$CHROME" \
  --headless=new \
  --remote-debugging-port=$PORT \
  --user-data-dir="$PROFILE" \
  --no-first-run \
  --no-default-browser-check \
  --disable-gpu \
  --disable-dev-shm-usage \
  --disable-background-networking \
  --mute-audio \
  >"$LOG" 2>&1 &

for i in $(seq 1 30); do
  if curl -s --max-time 2 "http://localhost:${PORT}/json/version" >/dev/null 2>&1; then
    echo "[headless] CDP 已在 ${i}s 内上线"
    exit 0
  fi
  sleep 1
done

echo "[headless] 启动失败，请检查 $LOG" >&2
exit 1
