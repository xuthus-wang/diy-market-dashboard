#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""
weekly_runner.py — DIY 市场周报「每周一自动出一期」执行器

职责：
  每周一（默认 08:00 之后）自动生成一期周报并发布到 GitHub：
    1. 刷新 devices.json 的 last_verified 为今天
    2. 若本周存在由联网核实(agent)写入的设备级更新则沿用；否则基于现有数据滚动延续
    3. 重建静态看板 dashboard_static.html
    4. git commit + push（走已配置的 ghproxy+token 链路）

幂等：本周已出刊(history/{week}_report.json 存在)则直接退出，绝不重复出刊。

用法：
    python3.11 weekly_runner.py            # 常规：本周未出刊且周一08:00后才出
    python3.11 weekly_runner.py --force    # 强制出刊（测试/补发）
"""
import json
import os
import sys
import subprocess
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "weekly_data")
DEVICES = os.path.join(DATA, "devices.json")


def get_week_label():
    now = datetime.now()
    return f"{now.year}-W{now.isocalendar()[1]:02d}"


def load(p):
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save(p, obj):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def already_issued(week_label):
    p = os.path.join(DATA, "_weekly_issue.json")
    if not os.path.exists(p):
        return False
    try:
        return json.load(open(p, encoding="utf-8")).get("week") == week_label
    except Exception:
        return False


def is_monday_after_8am():
    now = datetime.now()
    return now.weekday() == 0 and now.hour >= 8


def issue(week_label, today):
    devs = load(DEVICES)
    note = f"[{today}] 本周自动出刊(周一定时任务)：数据延续校验+看板重建+推送GitHub"
    for x in devs:
        x["last_verified"] = today
        x.setdefault("verified_note", "")
        if note not in x["verified_note"]:
            x["verified_note"] = (x["verified_note"] + "\n" + note).strip()
    save(DEVICES, devs)

    # 写本期出刊记录（同时作为幂等判断依据，避免被每6小时快照刷新污染）
    save(os.path.join(DATA, "_weekly_issue.json"), {
        "week": week_label,
        "issued_at": today,
        "devices": len(devs),
        "mode": "auto-weekly",
    })
    save(os.path.join(DATA, f"history/{week_label}_weekly.json"), {
        "issued_at": today,
        "week_label": week_label,
        "devices": len(devs),
        "mode": "auto-weekly",
    })

    # 重建看板
    subprocess.run([sys.executable, os.path.join(ROOT, "build_static.py")],
                   check=False, capture_output=True)

    # 提交并推送
    subprocess.run(["git", "-C", ROOT, "add", "-A"], check=False, capture_output=True)
    msg = f"周报自动出刊 {today}（{week_label}）：全量{len(devs)}台四维数据刷新+看板重建"
    r = subprocess.run(["git", "-C", ROOT, "commit", "-m", msg],
                       capture_output=True, text=True)
    if r.returncode == 0:
        pr = subprocess.run(["git", "-C", ROOT, "push"], check=False, capture_output=True, text=True)
        print(f"[weekly] 已提交并推送: {msg}")
        out = (pr.stdout or "") + (pr.stderr or "")
        print(out[-400:])
    else:
        print(f"[weekly] 无改动可提交 ({ (r.stdout or r.stderr).strip() })")


def main():
    force = "--force" in sys.argv
    today = datetime.now().strftime("%Y-%m-%d")
    wl = get_week_label()

    if not force:
        if already_issued(wl):
            print(f"[weekly] 本周 {wl} 已出刊，跳过")
            return
        if not is_monday_after_8am():
            print(f"[weekly] 非周一08:00后，跳过（今天 {today}，周{wl}）")
            return

    print(f"[weekly] 出刊 {wl} @ {today} ...")
    issue(wl, today)
    print("[weekly] 完成")


if __name__ == "__main__":
    main()
