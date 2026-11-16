#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply 4-dimensional (price/sales/growth/consumable) verified updates to devices.json.
Date: 2026-11-16 (W47 周一例行核实).
情报采集日: 2026-11-16 联网核实 (预算 19/20 次). 无伪造: 仅写入有来源的信号, 冲突口径只标注不改数.
要点:
  - 评论增量: popover 端点第二次全量命中, 12 台追踪 ASIN 全部取回(仅 p2s 首次被机器人墙, 换 language 参数重试成功).
    窗口 11-9→11-16 = 7 日, 无需折算. W46 重建基线的 3 台(k2plus/cameo5/joyxtra)本周起首度产出有效增量.
  - 价格: 本周无 >5% 同口径变更. h2d($1,599)/h2c($1,899) 官店复核与 W46 一致(促销持续);
    但 p2s/x2d/a2l 三台官店页面价格与 W46 采集口径全面失配(详见 conflict_notes), 按纪律只标冲突不改数.
    W46 备忘的「促销回弹记正」本周不执行: 回弹目标价(549/649/469)与页面现价(649/789/519)不匹配,
    直接记回弹会把不同变体价当成同配置涨价, 证据不足.
  - 新收录: 无(无已知本周上市新机型; H3C 已于 W46 收录).
"""
import json

SRC = "weekly_data/devices.json"
TODAY = "2026-11-16"
INTEL = "2026-11-16"

d = json.load(open(SRC, encoding="utf-8"))
by_id = {x["id"]: x for x in d}

# ---- 1) 价格变更（>5% 规则; 官方商店优先; 同配置同 list 才比）----
# 本周无: h2d $1,599 / h2c $1,899 官店复核与 W46 采集一致(促销持续);
# p2s/x2d/a2l 页面价与基线口径失配 → 见 conflict_notes, 不改数.
price_changes = {}

# ---- 2) 口径冲突（不同配置/渠道价与基线冲突, 按纪律不改数只标注）----
conflict_notes = {
    "bambu-p2s": "官店 P2S 商品页 11-16 抓取: 现价 $649 / Typical $749, 无多变体可切换; "
                 "与 W46 采集价 $449/Typical $549 及 8 月基线 $549 均不匹配. "
                 "黑五(11-27)未到促销价先回 +44.5% 不合常理, Typical 亦从 $549 变 $749, 判定页面展示口径已变(W46 疑采自合集页 From 价/另一变体), "
                 "两种口径均无法与基线对齐 → 按纪律只标冲突不改数, 维持 $449; 下周用合集页+商品页双页复核定死口径",
    "bambu-x2d": "官店 X2D 商品页 11-16 抓取: 现价 $789 / Typical $899, 与 W46 采集价 $589/Typical $649 及基线 $649 均不匹配, "
                 "失配幅度(+$200)与 p2s 同模式, 判定同一口径变更问题 → 只标冲突不改数, 维持 $589; 下周与 p2s 一并复核",
    "bambu-a2l": "官店 A2L 商品页 11-16 抓取: 现价 $519 / Typical $569; Typical $569 恰为已知 Combo 官价(基线备注: 基础版 $469/Combo $569), "
                 "即页面默认变体为 Combo 而基线为基础版, 配置不同不可比 → 只标冲突不改数, 维持 $439; "
                 "基础版是否仍在促销需下周单独复核",
    "bambu-h2d": "官店 H2D 商品页 11-16 复核: 仍为 $1,599 / Typical $1,749, 与 W46 采集完全一致, 黑五促销持续、未回弹, 本周无变动",
    "bambu-h2c": "官店 H2C 商品页 11-16 复核: 仍为 $1,899 / Typical $2,199, 与 W46 采集完全一致, 促销持续、无变动",
}

# ---- 3) 评论增量（同 ASIN 同口径; 窗口 11-9→11-16 = 7 日, 无需折算）----
# 数据源: amazon.com/gp/customer-reviews/widgets/average-customer-review/popover/?asin=<ASIN>
#         返回的 "N global ratings" 为该 ASIN 全站评分数, 与历史基线同口径.
review_updates = {
    "bambu-p1s": {"review_count": 1015, "review_count_date": "2026-11-16", "review_delta_week": 40,
        "growth_basis": "review_delta",
        "review_note": "11-16 抓取 1,015 评分 4.2星(ASIN B0CHDS1DMC 全站评分数); 上期基线 975(11-9), 7 日窗口 +40, 无需折算; "
                       "黑五前窗口(11-9~11-16)增量显著高于此前常态(+31/14日折周), 促销拉动明显"},
    "bambu-a1": {"review_count": 750, "review_count_date": "2026-11-16", "review_delta_week": 15,
        "growth_basis": "review_delta",
        "review_note": "11-16 抓取 750 评分 4.6星(ASIN B0D17TMWFB); 上期 735(11-9), 7 日窗口 +15; 首次为干净 7 日窗口(此前 26 日折算), 置信度提升"},
    "cricut-maker4": {"review_count": 694, "review_count_date": "2026-11-16", "review_delta_week": 10,
        "growth_basis": "review_delta",
        "review_note": "11-16 抓取 694 评分 4.5星(ASIN B0DTQBZ3J3); 上期 684(11-9, W43 以来首次建立的基线), 7 日窗口 +10; 首个有效增量"},
    "cricut-explore5": {"review_count": 74, "review_count_date": "2026-11-16", "review_delta_week": 3,
        "growth_basis": "review_delta",
        "review_note": "11-16 抓取 74 评分 4.6星(ASIN B0GS9S3HDQ); 上期 71(11-9), 7 日窗口 +3; 增速较上周(折周+11)明显回落"},
    "bambu-p2s": {"review_count": 33, "review_count_date": "2026-11-16", "review_delta_week": 2,
        "growth_basis": "review_delta",
        "review_note": "11-16 抓取 33 评分 4.6星(ASIN B0FT7ZLSSC 单机口径); 上期 31(11-9), 7 日窗口 +2; "
                       "首次请求被机器人墙拦('Continue shopping' 空页), 加 language=en_US 参数重试成功 —— 下周失败时先试该参数"},
    "anycubic-kobra-s1-combo": {"review_count": 274, "review_count_date": "2026-11-16", "review_delta_week": 2,
        "growth_basis": "review_delta",
        "review_note": "11-16 抓取 274 评分 3.7星(ASIN B0DBDT2ZZJ); 上期 272(11-9), 7 日窗口 +2; 增速较上周(+24)大幅回落, 黑五前动能减弱"},
    "silhouette-cameo5": {"review_count": 762, "review_count_date": "2026-11-16", "review_delta_week": 1,
        "growth_basis": "review_delta",
        "review_note": "11-16 抓取 762 评分 4.4星(ASIN B0CHY4NWPX); 上期 761(11-9, W46 重建的全站口径基线), 7 日窗口 +1; 重建基线后首个有效增量"},
    "bambu-a1mini-combo": {"review_count": 409, "review_count_date": "2026-11-16", "review_delta_week": 1,
        "growth_basis": "review_delta",
        "review_note": "11-16 抓取 409 评分 4.2星(ASIN B0CRYZWJLG); 上期 408(11-9), 7 日窗口 +1"},
    "creality-k2plus": {"review_count": 2142, "review_count_date": "2026-11-16", "review_delta_week": 0,
        "growth_basis": "review_delta",
        "review_note": "11-16 抓取 2,142 评分 4.2星(ASIN B0DQTQQBZ9); 上期 2,142(11-9, W46 重建的全站口径基线), 7 日窗口 0 增量 —— 如实记 0"},
    "cricut-joyxtra": {"review_count": 1584, "review_count_date": "2026-11-16", "review_delta_week": 0,
        "growth_basis": "review_delta",
        "review_note": "11-16 抓取 1,584 评分 4.6星(ASIN B0CF6L9SMJ); 上期 1,584(11-9, W46 重建基线), 7 日窗口 0 增量 —— 如实记 0"},
    "prusa-mk4": {"review_count": 26, "review_count_date": "2026-11-16", "review_delta_week": 0.0,
        "growth_basis": "review_delta",
        "review_note": "11-16 抓取 26 评分 4.8星(ASIN B0CKSX4M9F); 与上期 26(11-9)持平, 7 日窗口 0 增量 —— 如实记 0"},
    "prusa-core-one": {"review_count": 40, "review_count_date": "2026-11-16", "review_delta_week": 0.0,
        "growth_basis": "review_delta",
        "review_note": "11-16 抓取 40 评分 4.7星(ASIN B0FKNGJPK2, Kit 口径); 与上期 40(11-9)持平, 7 日窗口 0 增量 —— 如实记 0"},
}

# ---- 4) 补链接（营收 Top20 缺链机型已全部处置, 本周无需新增）----
tracking_adds = {}
tracking_notes = {}
tracking_misses = {}

# ---- 5) 本周新收录（销量一律 pending 不编造）----
new_models = []

# ---- 6) 市场动态备注（不改任何设备数值）----
market_notes = {
    "bambu-h2d": "黑五促销持续复核(11-16): 官店价与上周一致($1,599/Typical $1,749), 主黑五(11-27)临近, 预计促销价延续至月末",
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

    # price_change_pct 语义 = 「本周」变动率, 未变动机型一律归零(历史幅度保留在 verified_note).
    if did not in price_changes:
        dev["price_change_pct"] = 0

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
