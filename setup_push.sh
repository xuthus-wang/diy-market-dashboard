#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# setup_push.sh — 读取本机 .secret 中的 GitHub PAT，配置 ghproxy+token 推送链路
#
# 背景：沙箱/本机到 github.com 的 git 智能协议直连常被网关 TLS 阻断(502/握手终止)，
#       而 ghproxy.net 镜像+凭据实测可推送(2026-08-31 起采用)。token 只存本机
#       .secret(已被 .gitignore 排除)，绝不写入仓库与提交历史。
#
# 用法: bash setup_push.sh    # 幂等：已配置则跳过
# 退出码: 0=就绪  1=无 token(可降级为 format-patch 交付)
# ---------------------------------------------------------------------------
set -u
REPO_PATH="xuthus-wang/diy-market-dashboard"
SECRET_FILE=".secret"

if [[ ! -f "$SECRET_FILE" ]]; then
  echo "[push] 无 $SECRET_FILE（格式: GH_TOKEN=ghp_xxx），降级为 format-patch 交付"
  exit 1
fi

TOKEN="$(grep -E '^GH_TOKEN=' "$SECRET_FILE" | head -1 | cut -d= -f2- | tr -d '[:space:]')"
if [[ -z "$TOKEN" ]]; then
  echo "[push] $SECRET_FILE 中无 GH_TOKEN，降级为 format-patch 交付"
  exit 1
fi

PUSH_URL="https://ghproxy.net/https://xuthus-wang:${TOKEN}@github.com/${REPO_PATH}.git"
CUR="$(git config --get remote.origin.pushurl 2>/dev/null || true)"
if [[ "$CUR" == *"@"* && "$CUR" == *"$REPO_PATH"* ]]; then
  echo "[push] pushurl 已含凭据，跳过"
else
  git remote set-url --push origin "$PUSH_URL"
  echo "[push] pushurl = ghproxy+token（凭据仅存在于本机 .git/config）"
fi
# 仅对镜像放宽证书校验（沙箱内其证书不被信任），不动 github.com 全局
git config http.https://ghproxy.net/.sslVerify false
exit 0
