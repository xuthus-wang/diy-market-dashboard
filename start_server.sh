#!/bin/bash
# DIY市场周报系统 — 服务器启动脚本（带自愈：崩溃/退出自动重启）
# 用法: bash /workspace/start_server.sh   （后台: bash /workspace/start_server.sh &）
cd /workspace
PORT=8080
LOG=/tmp/diy_server.log

# 先清理占用端口的旧进程
if command -v lsof >/dev/null 2>&1; then
  PIDS=$(lsof -ti:$PORT 2>/dev/null)
  [ -n "$PIDS" ] && kill -9 $PIDS 2>/dev/null
fi

echo "🚀 启动 DIY市场周报系统 (端口 $PORT)，日志: $LOG"
while true; do
  python3.11 diy_weekly_app.py >> "$LOG" 2>&1
  echo "[$(date)] Flask 退出，5秒后自动重启..." >> "$LOG"
  sleep 5
done
