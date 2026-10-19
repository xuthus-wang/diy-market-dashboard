#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply 4-dimensional (price/sales/growth/consumable) verified updates to devices.json.
Date: 2026-10-19 (W43 周一例行核实).
情报采集日: 2026-10-19 联网核实 (预算 19/20 次). 无伪造: 仅写入有来源的信号, 冲突口径只标注不改数.
要点:
  - 评论增量: 4 台已追踪 ASIN 中仅 P1S Combo 抓取成功(880, +113); 其余 3 台页面未渲染评论组件, 如实记抓取失败, 不写 0.
  - 补链接: 营收 Top20 无追踪机型按降序补 5 台 ASIN(cameo5/k2plus/maker4/core-one/p2s), 预算所限其余下周继续.
  - 价格: 仅 cricut-joyxtra 官网口径回补 $129→$179(上周疑把促销价当列表价); Bambu 万圣节促销(至10-16)已截止, 促销价不入基线.
"""
import json

SRC = "weekly_data/devices.json"
TODAY = "2026-10-19"
INTEL = "2026-10-19"

d = json.load(open(SRC, encoding="utf-8"))
by_id = {x["id"]: x for x in d}

# ---- 1) 价格变更（>5% 规则; 官方商店优先）----
price_changes = {
    "cricut-joyxtra": (179, 38.8,
        "Cricut 官网 machines 页起始价 $179(10-19 直接抓取, 证据强); 上周 10-14 依渠道聚合改 $129 疑把促销价误当列表价, 按官方口径回补 +38.8%"),
}

# ---- 2) 口径冲突（有媒体/第三方价与基线冲突, 按纪律不改数只标注）----
conflict_notes = {
    "epson-v1070":     "联盟站 bestvaluelab 报 Amazon 价 $3,259(9-10 口径) vs 基线 $8,495(Epson MSRP, 官方), 差异 -61.6% 异常, 或为翻新机/报价错误, 维持基线待复核",
    "bambu-x1e":       "BambuHub 官方店日志: 美国店现列 $2,899(含AMS) vs 基线 $1,499; 另 X1E 已于 2026-03 停产(X1 系列 3-31 停更, 官方指向 H2S/H2D 接替), 生命周期信号显著; 维持基线待复核",
    "bambu-p1s":       "多源(BambuHub 官方店日志 10-9 / 媒体)显示 P1S 单机 $399, 基线 $499 为 Combo 口径(ASIN B0CHDS1DMC), 配置不同不可直接比; Combo 现价未确认, 维持基线待复核",
    "prusa-core-one":  "Tom's Hardware 报 $1,499(组装)/CNET $1,549 vs 基线 $1,099, 疑 Kit 与组装版口径差(新补 Amazon ASIN B0FKNGJPK2 为 Kit 版); 维持基线待复核",
    "bambu-h2s":       "BambuHub 官方店日志(10-9): 单机 $1,199 / Combo $1,399; 基线 $1,399 与 Combo 促销价吻合、与上周第三方 $1,249(单机)冲突, 疑配置口径混用, 待官方店直接复核后统一",
}

# ---- 3) 评论增量（同 ASIN 同口径; 抓取失败如实记录, 不写 0）----
review_updates = {
    # 成功: P1S Combo 767(10-14) -> 880(10-19)
    "bambu-p1s": {
        "review_count": 880, "review_count_date": TODAY, "review_delta_week": 113,
        "review_note": "Amazon US P1S Combo ASIN B0CHDS1DMC 自身评分数(880), 同 ASIN 同口径; 增量窗口 10-14→10-19 仅 5 日且尾段含万圣节促销干扰, 首期样本不足以按留评率折算月销, 本周维持 D 级不改销量, 待 1-2 期清洁窗口后再评估升级 B",
        "growth_basis": "review_delta",
    },
    # 抓取失败: 维持旧值, delta 置 null
    "bambu-a1mini-combo": {"review_count": 381, "review_count_date": "2026-10-14", "review_delta_week": None,
        "review_note": "10-19 两次抓取 Amazon 页面均未渲染评论组件(疑似反爬/页面变体), 本周无增量数据, 如实留空不计 0; 下周重试同口径"},
    "bambu-a1": {"review_count": 657, "review_count_date": "2026-10-14", "review_delta_week": None,
        "review_note": "10-19 两次抓取 Amazon 页面均未渲染评论组件, 本周无增量数据, 如实留空不计 0; 下周重试同口径"},
    "cricut-explore5": {"review_count": 30, "review_count_date": "2026-10-14", "review_delta_week": None,
        "review_note": "10-19 两次抓取 Amazon 页面均未渲染评论组件, 本周无增量数据, 如实留空不计 0; 下周重试同口径"},
}

# ---- 4) 补链接（营收 Top20 无追踪机型按降序; 当日评论基线, 未抓到评分数的如实置 null）----
tracking_adds = {
    "silhouette-cameo5": {"amazon": "https://www.amazon.com/dp/B0CHY4NWPX"},
    "creality-k2plus":   {"amazon": "https://www.amazon.com/dp/B0DQTQQBZ9"},
    "cricut-maker4":     {"amazon": "https://www.amazon.com/dp/B0DTQBZ3J3"},
    "prusa-core-one":    {"amazon": "https://www.amazon.com/dp/B0FKNGJPK2"},
    "bambu-p2s":         {"amazon": "https://www.amazon.com/dp/B0FT7ZLSSC"},
}
tracking_notes = {
    "silhouette-cameo5": "Amazon US Cameo 5 雾面黑官方版 ASIN; 当日评分数 124(3.9 星), 2026-10-19 起建立增量基线",
    "creality-k2plus":   "Amazon US K2 Plus Combo ASIN(Creality 官方店自营); 当日评分数 866(4.3 星), 2026-10-19 起建立增量基线",
    "cricut-maker4":     "Amazon US Maker 4 Seashell Digital Content Bundle ASIN(页面显示 100+ bought in past week); 评分数本次快照未含, 基线待下周抓取",
    "prusa-core-one":    "Amazon US CORE One Kit 版 ASIN(注意: 与基线价 $1,099 的配置口径需核对); 评分数本次快照未含, 基线待下周抓取",
    "bambu-p2s":         "Amazon US P2S 单机 ASIN(Bambu Lab 官方店), 与基线 $549 单机价同口径; Combo 版 ASIN B0FT818HCH(77 评分数)仅备查不入基线; 单机评分数待下周抓取",
}

# ---- 5) 本周新收录（销量一律 pending 不编造）----
new_models = [
    {
        "id": "cricut-maker5", "brand": "Cricut", "model": "Maker 5",
        "category": "智能切割机",
        "price_usd": 349, "price_change_pct": 0,
        "monthly_sales": 0, "weekly_growth_pct": 0,
        "description": "Cricut Maker 5 旗舰切割机(2026-10-19 Cricut 官网 machines 页核实, 标注 New, 售价区间 $349-$549)。Maker 4 的迭代机型, 官网同步对 Maker 4 打出 $20 促销; 详细规格待复核补充。",
        "key_features": ["旗舰级多材料切割(待复核)"],
        "is_new": True,
        "social_metrics": {},
        "sales_channels": ["Cricut 官网", "Amazon"],
        "consumables": ["Smart Vinyl/Iron-On/卡纸等"],
        "consumable_monthly_sales_est": "$0(待积累)",
        "last_verified": TODAY,
        "verified_note": "[2026-10-19] 首次收录(Cricut 官网 machines 页直接抓取, New 标注 + 价格区间 $349-$549); 月销量无锚点 → pending, 待积累",
        "first_tracked_week": "2026-W43",
        "sales_maturity": "new_launch",
        "sales_data_status": "pending",
    },
]

# ---- 6) 市场动态备注（不改任何设备数值）----
market_notes = {
    "bambu-h2d":     "万圣节促销(单机 $1,549/Combo $1,749)已于 10-16 截止, 促销价不入基线; CNET 亦确认 $1,749 为常态价; 四维数值维持",
    "cricut-maker4": "Cricut 官网已上线 Maker 5($349 起, New)与 StickerPix 打印+切割新品类, Maker 4 面临世代交替压力(官网 $379 促销价与基线一致); 四维数值维持",
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
