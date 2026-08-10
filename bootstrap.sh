#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# DIY 市场周报 · 工作区自愈引导脚本
#
# 用途：定时任务（每周一 08:00）执行核实流程前的第一步。
#       沙箱被重置导致 /workspace 全空时，自动从远端恢复完整仓库。
#
# 背景：本沙箱到 github.com 的直连被网关 TLS 阻断（git clone / api / raw
#       全部握手失败），因此走 ghproxy 镜像。镜像仅支持匿名只读，push 仍需
#       凭据，故 push URL 单独指回 github.com 原址。
#
# 用法：bash bootstrap.sh            # 缺失才恢复（定时任务用这个）
#       bash bootstrap.sh --force    # 强制重新拉取，丢弃本地未提交改动
#
# 退出码：0=工作区就绪  1=恢复失败（此时不应继续执行核实流程）
# ---------------------------------------------------------------------------
set -uo pipefail

WORKSPACE="${WORKSPACE:-/workspace}"
REPO_PATH="xuthus-wang/diy-market-dashboard"
UPSTREAM="https://github.com/${REPO_PATH}.git"
BRANCH="main"

# 镜像按可用性排序，逐个回退。2026-08-10 实测：ghproxy.net 可用，直连阻断。
MIRRORS=(
  "https://ghproxy.net/https://github.com/${REPO_PATH}.git"
  "https://gh-proxy.com/https://github.com/${REPO_PATH}.git"
  "https://github.com/${REPO_PATH}.git"
)
# git 通路全灭时的 tarball 兜底（无 .git 元数据，只保数据不保版本历史）
TARBALLS=(
  "https://ghproxy.net/https://github.com/${REPO_PATH}/archive/refs/heads/${BRANCH}.tar.gz"
  "https://cdn.jsdelivr.net/gh/${REPO_PATH}@${BRANCH}/"
)

FORCE=0
[[ "${1:-}" == "--force" ]] && FORCE=1

log()  { printf '[bootstrap] %s\n' "$*"; }
fail() { printf '[bootstrap][ERROR] %s\n' "$*" >&2; }

# --- 校验：工作区是否具备执行核实流程的最小条件 -----------------------------
workspace_healthy() {
  [[ -f "${WORKSPACE}/weekly_data/devices.json" ]] || return 1
  [[ -f "${WORKSPACE}/build_static.py"          ]] || return 1
  python3.11 - "$WORKSPACE" <<'PY' >/dev/null 2>&1 || return 1
import json, sys
d = json.load(open(sys.argv[1] + "/weekly_data/devices.json"))
assert isinstance(d, list) and len(d) >= 40, f"设备数异常: {len(d)}"
assert all("id" in x and "price_usd" in x for x in d), "字段缺失"
PY
  return 0
}

# --- 把 remote 摆正：fetch 走镜像，push 指回原址 ----------------------------
fix_remote() {
  local fetch_url="$1"
  git -C "$WORKSPACE" remote set-url origin "$fetch_url" 2>/dev/null \
    || git -C "$WORKSPACE" remote add origin "$fetch_url"
  git -C "$WORKSPACE" remote set-url --push origin "$UPSTREAM"
  log "remote: fetch=${fetch_url}"
  log "remote: push =${UPSTREAM}（需凭据；无凭据时改用 git format-patch 交付）"
}

# --- 恢复主逻辑 -------------------------------------------------------------
restore() {
  local tmp
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' RETURN

  # 覆盖前自保：工作区已有 .git 时（例如数据损坏但存在未推送的本周提交），
  # 先整体备份，避免 cp 覆盖 .git 导致提交历史丢失。
  if [[ -d "${WORKSPACE}/.git" ]]; then
    local backup="/tmp/ws_backup_$(date +%Y%m%d_%H%M%S)"
    cp -r "$WORKSPACE" "$backup" 2>/dev/null \
      && log "已备份现有工作区 → ${backup}（含 .git，如需找回未推送提交请查此处）"
  fi

  for url in "${MIRRORS[@]}"; do
    log "尝试克隆：${url%%/https*}…"
    if timeout 120 git clone --quiet --branch "$BRANCH" "$url" "$tmp/repo" 2>/dev/null; then
      log "克隆成功（含 .git 版本历史）"
      mkdir -p "$WORKSPACE"
      # 保留工作区里可能存在的沙箱元数据，只覆盖仓库内容
      cp -r "$tmp/repo/." "$WORKSPACE/"
      fix_remote "$url"
      return 0
    fi
    rm -rf "$tmp/repo"
  done

  fail "全部 git 镜像不可用，改用 tarball 兜底"
  for url in "${TARBALLS[@]}"; do
    [[ "$url" == *.tar.gz ]] || continue
    log "尝试下载快照：${url%%/https*}…"
    if timeout 120 curl -sSfL -o "$tmp/repo.tar.gz" "$url" 2>/dev/null \
       && tar tzf "$tmp/repo.tar.gz" >/dev/null 2>&1; then
      tar xzf "$tmp/repo.tar.gz" -C "$tmp"
      local root
      root="$(find "$tmp" -maxdepth 1 -type d -name '*diy-market-dashboard*' | head -1)"
      [[ -n "$root" ]] || continue
      mkdir -p "$WORKSPACE"
      cp -r "$root/." "$WORKSPACE/"
      log "快照恢复成功（⚠ 无 .git，本次只能产出 patch，无法 commit/push）"
      return 0
    fi
  done

  return 1
}

# --- 主流程 -----------------------------------------------------------------
log "工作区：${WORKSPACE}"

if [[ $FORCE -eq 0 ]] && workspace_healthy; then
  n=$(python3.11 -c "import json;print(len(json.load(open('${WORKSPACE}/weekly_data/devices.json'))))")
  log "工作区健康（${n} 台设备），跳过恢复"
  [[ -d "${WORKSPACE}/.git" ]] && fix_remote "${MIRRORS[0]}"
  exit 0
fi

[[ $FORCE -eq 1 ]] && log "--force：强制重新拉取"
log "工作区缺失或损坏，开始恢复…"

if ! restore; then
  fail "恢复失败：所有通路均不可用。请勿继续执行核实流程（无基线数据会导致编造）。"
  exit 1
fi

if workspace_healthy; then
  n=$(python3.11 -c "import json;print(len(json.load(open('${WORKSPACE}/weekly_data/devices.json'))))")
  log "✓ 恢复完成：${n} 台设备，工作区就绪"
  exit 0
fi

fail "恢复后校验未通过，devices.json 不完整"
exit 1
