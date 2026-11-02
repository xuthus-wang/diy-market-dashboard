#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply 4-dimensional (price/sales/growth/consumable) verified updates to devices.json.
Date: 2026-11-02 (W45 周一例行核实).
情报采集日: 2026-11-02 联网核实 (预算 20/20 次). 无伪造: 仅写入有来源的信号, 冲突口径只标注不改数.
要点:
  - Amazon 评论抓取本周全量被反爬封锁(dp 页 3.8KB 机器人墙 + product-reviews 页 21KB 统一墙, 双端点双 UA 均失败):
    10 台追踪 ASIN 全部无增量, 如实留空不写 0, 维持旧基线; growth_proxy 本周无新评论增量输入.
  - 补基线 2 台(经 site:amazon.com 检索, 评论数来自搜索快照, 下周起记增量):
    anycubic-kobra-s1-combo(B0DBDT2ZZJ, 248 评分 3.5星) / cricut-joyxtra(B0CF6L9SMJ, 1182 评分 4.5星).
  - 价格: 仅 bambu-h2s 官店促销 $1,399→$1,249(-10.7%, 官店自标 Typical $1,399 证实 W44 的 $1,499 假设不成立).
  - 放弃补链 3 台: xTool O1 Omni 两 SKU 与 HeyGears G1X 均官网直营, Amazon 无官方整机在售(多家媒体佐证).
  - 新收录: 无 — H3C Tool Changer 明日(11-3)上市, 今日未开售, 按纪律不收录.
"""
import json

SRC = "weekly_data/devices.json"
TODAY = "2026-11-02"
INTEL = "2026-11-02"

d = json.load(open(SRC, encoding="utf-8"))
by_id = {x["id"]: x for x in d}

# ---- 1) 价格变更（>5% 规则; 官方商店优先）----
price_changes = {
    "bambu-h2s": (1249, -10.7,
        "Bambu US 官店 H2S 页 11-2 抓取: 现价 $1,249, 官店自标 Typical Price $1,399(-10.7%, 证据强·官方商店). "
        "官店 Typical $1,399 与基线同值, 证实 W44 '常态价 $1,499' 系二手转述不成立, 基线口径正确; "
        "当前为黑五档期促销价(官店直采, 非第三方), 按官方商店优先纪律记入; "
        "注意: 官店页未明示单机/Combo(装箱含 AMS 2 Pro 疑 Combo 口径), 与基线 $1,399 同源同价可比; "
        "促销结束后如回弹 $1,399 将按回弹记 +12.3%"),
}

# ---- 2) 口径冲突（有媒体/第三方价与基线冲突, 按纪律不改数只标注）----
conflict_notes = {
    "bambu-p1s":     "Bambu US 官店 P1S 页 11-2 抓取: 单机 $509(官店自标 Typical $579); 基线 $499 为 Amazon Combo 口径"
                     "(ASIN B0CHDS1DMC), 配置与渠道口径仍不对齐; 若按单机口径比 $499→$509 仅 +2.0% <5%, 不构成变更; 维持基线待口径对齐",
}

# ---- 3) 评论增量（同 ASIN 同口径; 抓取失败如实记录, 不写 0）----
# 本周 Amazon 全量反爬封锁(dp/product-reviews 双端点, 桌面/移动双 UA 均 3.8KB/21KB 机器人墙), 无任何新增量.
review_updates = {
    "bambu-p1s": {"review_count": 914, "review_count_date": "2026-10-26", "review_delta_week": None,
        "review_note": "11-2 抓取遇 Amazon 全站反爬封锁(dp 页+评论页双端点均机器人墙), 无增量如实留空不计 0; 维持 10-26 基线 914; 下周重试同口径"},
    "bambu-p2s": {"review_count": 26, "review_count_date": "2026-10-26", "review_delta_week": None,
        "review_note": "11-2 抓取遇 Amazon 全站反爬封锁, 无增量如实留空不计 0; 维持 10-26 基线 26(清洁 7 日窗口作废, 下周窗口为 14 日)"},
    "prusa-core-one": {"review_count": 39, "review_count_date": "2026-10-26", "review_delta_week": None,
        "review_note": "11-2 抓取遇 Amazon 全站反爬封锁, 无增量如实留空不计 0; 维持 10-26 基线 39(Kit 口径)"},
    "bambu-a1mini-combo": {"review_count": 381, "review_count_date": "2026-10-14", "review_delta_week": None,
        "review_note": "11-2 抓取遇 Amazon 全站反爬封锁(连续三周失败), 无增量如实留空不计 0; 下周重试同口径"},
    "bambu-a1": {"review_count": 657, "review_count_date": "2026-10-14", "review_delta_week": None,
        "review_note": "11-2 抓取遇 Amazon 全站反爬封锁(连续三周失败), 无增量如实留空不计 0; 下周重试同口径"},
    "creality-k2plus": {"review_count": 866, "review_count_date": "2026-10-19", "review_delta_week": None,
        "review_note": "11-2 抓取遇 Amazon 全站反爬封锁, 无增量如实留空不计 0; 下周重试同口径"},
    "silhouette-cameo5": {"review_count": 124, "review_count_date": "2026-10-19", "review_delta_week": None,
        "review_note": "11-2 抓取遇 Amazon 全站反爬封锁, 无增量如实留空不计 0; 下周重试同口径"},
    "cricut-explore5": {"review_count": 30, "review_count_date": "2026-10-14", "review_delta_week": None,
        "review_note": "11-2 抓取遇 Amazon 全站反爬封锁(连续三周失败), 无增量如实留空不计 0; 下周重试同口径"},
    "cricut-maker4": {"review_count": None, "review_count_date": None, "review_delta_week": None,
        "review_note": "11-2 抓取遇 Amazon 全站反爬封锁(连续三周失败), 基线仍未建立; 下周重试"},
}

# ---- 4) 补链接（营收 Top20 无追踪机型按降序; 当日评论基线, 评论数来自搜索快照）----
tracking_adds = {
    "anycubic-kobra-s1-combo": {"amazon": "https://www.amazon.com/dp/B0DBDT2ZZJ"},
    "cricut-joyxtra": {"amazon": "https://www.amazon.com/dp/B0CF6L9SMJ"},
}
tracking_notes = {
    "anycubic-kobra-s1-combo": "Amazon US ASIN B0DBDT2ZZJ(Kobra S1 Combo 含 ACE PRO, ANYCUBIC 官方店): "
        "248 评分 3.5 星, 2024-07-27 上架, 3D Printers 类目 #33, 近月 200+ 购买(搜索快照 11-2); "
        "另见新代际 ASIN B0GSPHJQB2(88 评分 3.2 星, 2026-03 上架)与 B0DQPD5QS3(130 评分)备查不入基线"
        "(本基线选评分数最多/历史最长/与 $459 价位匹配的官方整机 ASIN); 2026-11-02 起建立增量基线; "
        "注意: 评论数取自 Amazon 搜索结果快照而非直抓页面(直抓被反爬封锁), 口径为 ASIN 自身评分数",
    "cricut-joyxtra": "Amazon US ASIN B0CF6L9SMJ(Cricut Joy Xtra Machine Only, Amazon 自营): "
        "1,182 评分 4.5 星(搜索快照 11-2); 同 ASIN 存在 Digital Bundle/Starter Kit 等变体, 本基线取 Machine Only 口径; "
        "评论数取自搜索快照而非直抓页面, 口径为 ASIN 自身评分数; 2026-11-02 起建立增量基线",
}
# Top20 补链未完成的机型（如实记录, 本周判定放弃/下周继续）
tracking_misses = {
    "bambu-h2d":  "本周未再耗预算(沿用 10-26 结论: site:amazon.com 仅命中配件 ASIN); Bambu 官网直营为主, 判定放弃 Amazon 补链, 后续以官店价核实",
    "xtool-o1-omni-uv-fabric": "xTool O1 Omni 系列官网直营(xtool.pxf.io 官方链), Amazon 无官方整机在售"
        "(basic-tutorials 10月: 'no list price available on Amazon'; 本周 site:amazon.com 检索仅联盟测评站); 判定放弃补 ASIN, 以官店价 $2,799(UV+Fabric 版)核实",
    "xtool-o1-omni-dual-uv": "同上, O1 Omni Dual UV 版官网直营 $2,699 预售价(CGMagazine), Amazon 无官方整机; 放弃补 ASIN",
    "heygears-g1x": "HeyGears G1X 官网直营+Kickstarter, 无官方 Amazon ASIN(检索仅命中 Reflex RS 的 B0GMQC8CRQ, 非本机型); 放弃补 ASIN; "
        "定价情报: G1X Starter VIP $2,999/MSRP $4,999, Full-3D Pack VIP $3,299/MSRP $5,499(OddityMall 称 Kickstarter $3,599, 来源弱); 基线 $3,299 与 Full-3D Pack 早鸟价一致, 维持",
}

# ---- 5) 本周新收录（销量一律 pending 不编造）----
new_models = [
    # 无: H3C Tool Changer 已官宣 11-3 上市, 本周(11-2)未开售, 按纪律不收录, 见 market_notes
]

# ---- 6) 市场动态备注（不改任何设备数值）----
market_notes = {
    "bambu-h2d": "Bambu H3C Tool Changer 定档 11-3 上市(官宣), 本周未开售不收录; 黑五档期已开跑(竞品 Amazon 列表已现黑五倒计时标签), Bambu 官店 H2S 已进促销价 $1,249, 关注 H2D/P 系列是否跟进促销",
    "anycubic-kobra-s1-combo": "平台聚合信号(单源不改数): ASIN B0DBDT2ZZJ 近月 200+ 购买, 同系列新列表近月 300+ 购买且挂黑五特价; 3.2~3.5 星评分偏低为品类口碑风险点",
    "cricut-maker4": "营收 Top20 无追踪机型剩余: maker4(有 ASIN 无基线)/h2d/h2s/x1c/v1070/g1x/o1-omni×2/joyxtra 已全部处置(补链或判定放弃), 本周起新增量优先补 maker4 评论基线",
}

def append_note(dev, line):
    dev["verified_note"] = (dev.get("verified_note") or "") + "\n" + line

generic = ("[%s] 联网核实(情报日 %s): 价格无>5%%变动维持; 销量无新权威锚点维持; "
           "增长无方向性新信号维持; 耗材价稳维持" % (TODAY, INTEL))

n_price = n_conflict = n_review = n_track = 0
for dev in d:
    dev["last_verified"] = TODAY
    did = dev["id"]

    if did in price_changes:
        new_p, pct, why = price_changes[did]
        dev["price_usd"] = new_p
        dev["price_change_pct"] = pct
        append_note(dev, "[%s] 价格 %s; 销量/增长/耗材维持" % (TODAY, why))
        n_price += 1
    elif did in conflict_notes:
        append_note(dev, "[%s] 口径冲突(情报日 %s): %s" % (TODAY, INTEL, conflict_notes[did]))
        n_conflict += 1
    elif did in market_notes:
        append_note(dev, "[%s] %s" % (TODAY, market_notes[did]))
    else:
        append_note(dev, generic)

    if did in tracking_misses:
        append_note(dev, "[%s] %s" % (TODAY, tracking_misses[did]))

    # 评论增量(独立于价格分支, 可叠加)
    if did in review_updates:
        ru = review_updates[did]
        dev["review_count"] = ru["review_count"]
        dev["review_count_date"] = ru["review_count_date"]
        dev["review_delta_week"] = ru["review_delta_week"]
        dev["review_note"] = ru["review_note"]
        if ru.get("growth_basis"):
            dev["growth_basis"] = ru["growth_basis"]
        n_review += 1

    # 补追踪链接 + 当日评论基线
    if did in tracking_adds:
        dev["tracking_urls"] = {**(dev.get("tracking_urls") or {}), **tracking_adds[did]}
        append_note(dev, "[%s] %s" % (TODAY, tracking_notes[did]))
        n_track += 1

existing = {x["id"] for x in d}
added = []
for rec in new_models:
    if rec["id"] not in existing:
        rec.setdefault("monthly_sales_legacy", 0)
        rec.setdefault("sales_confidence", "estimated")
        d.append(rec)
        added.append(rec["id"])

json.dump(d, open(SRC, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print("Total devices: %d (was %d, +%d: %s)" % (len(d), len(d) - len(added), len(added), added))
print("Price changes applied: %d" % n_price)
for k, (np, pct, _) in price_changes.items():
    print("  %s: -> $%s (%+s%%)" % (k, np, pct))
print("Conflict notes (no change): %d -> %s" % (n_conflict, list(conflict_notes.keys())))
print("Review updates: %d -> %s" % (n_review, list(review_updates.keys())))
print("Tracking links added: %d -> %s" % (n_track, list(tracking_adds.keys())))
print("Tracking misses noted: %d -> %s" % (len(tracking_misses), list(tracking_misses.keys())))
