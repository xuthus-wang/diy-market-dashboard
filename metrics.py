#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""metrics.py — 销量证据分级 + 区间估计 + 周度量序列

证据分级（sales_grade）：
  A 官方披露   财报/招股书/官方战报直接推得该机型销量        区间 ±15%
  B 评论增量   平台评论数周增量 ÷ 留评率区间(1%~2%)          区间 ±25%
  C 平台聚合   Accio/JungleScout/Keepa 等第三方单源          区间 ±40%
  D 锚点推算   品牌级锚点(财报/份额) × 机型占比或价格弹性     区间 ±50%(anchored) / ±80%(low)
  E 待积累     新品未开售/在售不足一个月                      无区间

周增长口径（自 2026-W42 起废弃手工 pp 调整）：
  growth_proxy = 本周评论增量 / 上周评论增量 - 1   （无上周基线时为 null）
  旧字段 weekly_growth_pct 保留展示但标注「热度代理·旧口径」。
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weekly_data")
HISTORY_DIR = os.path.join(DATA_DIR, "history")

GRADES = {
    "A": {"label": "官方披露", "half": 0.15, "color": "#10b981"},
    "B": {"label": "评论增量", "half": 0.25, "color": "#3b82f6"},
    "C": {"label": "平台聚合", "half": 0.40, "color": "#a855f7"},
    "D": {"label": "锚点推算", "half": 0.50, "color": "#f59e0b"},
    "E": {"label": "待积累", "half": None, "color": "#6b7280"},
}


def grade_of(d):
    """从旧字段推断证据分级。新采集流程直接写 sales_grade 时以显式字段优先。"""
    if d.get("sales_grade"):
        return d["sales_grade"]
    status = d.get("sales_data_status") or "estimated_model"
    conf = d.get("sales_confidence")
    if (d.get("monthly_sales") or 0) <= 0:
        return "E"
    if status == "real_reported":
        return "A"
    if status == "review_delta":          # 新采集流程使用
        return "B"
    if status == "aggregator":            # 新采集流程使用
        return "C"
    # anchored / estimated_model / estimated → D
    return "D"


def interval_of(d):
    """返回 (low, high)，E 级返回 None。"""
    g = grade_of(d)
    if g == "E":
        return None
    half = GRADES[g]["half"]
    if g == "D":
        half = 0.80 if (d.get("sales_confidence") in ("low", "estimated")) else 0.50
    s = d.get("monthly_sales") or 0
    return (max(0, round(s * (1 - half) / 10) * 10), round(s * (1 + half) / 10) * 10)


def enrich(d):
    """就地为设备补齐 sales_grade / sales_interval / growth_basis。"""
    g = grade_of(d)
    d["sales_grade"] = g
    it = interval_of(d)
    if it:
        d["sales_interval"] = list(it)
    elif "sales_interval" in d:
        del d["sales_interval"]
    if not d.get("growth_basis"):
        d["growth_basis"] = "legacy_heat_proxy"   # 待首个评论增量基线建立后改为 review_delta
    return d


def snapshot(devices, week_label, summary=None, category_breakdown=None, weekly_changes=None):
    """把本周全量度量写入 history/<week>.json（序列基线，供下周算评论增量环比）。"""
    os.makedirs(HISTORY_DIR, exist_ok=True)
    rec = {
        "week_label": week_label,
        "summary": summary or {},
        "category_breakdown": category_breakdown or {},
        "weekly_changes": weekly_changes or [],
        "devices": [
            {"id": x["id"], "monthly_sales": x.get("monthly_sales") or 0,
             "sales_grade": x.get("sales_grade"), "sales_interval": x.get("sales_interval"),
             "growth_basis": x.get("growth_basis"),
             "review_count": x.get("review_count"),
             "review_delta_week": x.get("review_delta_week")}
            for x in devices
        ],
    }
    p = os.path.join(HISTORY_DIR, "%s.json" % week_label)
    json.dump(rec, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return p


def growth_proxy(d, prev_by_id):
    """评论增量周环比：本周(增量) / 上周(增量) - 1；缺基线返回 None。"""
    cur, prev = d.get("review_delta_week"), (prev_by_id.get(d["id"]) or {}).get("review_delta_week")
    if cur is None or not prev:
        return None
    return round((cur / prev - 1) * 100, 1)


if __name__ == "__main__":
    p = os.path.join(DATA_DIR, "devices.json")
    devs = json.load(open(p, encoding="utf-8"))
    for x in devs:
        enrich(x)
    json.dump(devs, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    import collections
    print("分级分布:", dict(collections.Counter(x["sales_grade"] for x in devs)))
    print("示例:", {k: devs[0][k] for k in ("id", "sales_grade", "sales_interval") if k in devs[0]})
