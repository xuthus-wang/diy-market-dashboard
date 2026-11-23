#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply 4-dimensional (price/sales/growth/consumable) verified updates to devices.json.
Date: 2026-11-23 (W48 周一例行核实).
情报采集日: 2026-11-23 联网核实 (预算 20/20 次). 无伪造: 仅写入有来源的信号, 冲突口径只标注不改数.
要点:
  - 评论增量: popover 端点本周 11/12 命中, 仅 cameo5 两次均为机器人墙('Continue shopping'), 如实留空不写 0.
    窗口 11-16→11-23 = 7 日, 无需折算.
  - 价格: 本周 0 台 >5% 变更. 全部官店值与 W47 完全一致(黑五 11-27 未到, 促销价延续).
  - **p2s/x2d/a2l 口径门案本周结案**: 合集页 "From" 价与基线完全一致(449/589/439, Typical 549/649/469),
    商品页默认价(649/789/519)为 Combo 变体(+$200/+$200/+$80 配件差). 故 W47 判定的「黑五前反常回弹 +44.5%」不成立,
    实为「合集页 From(基础版) vs 商品页默认(Combo)」的口径错配; 基线值正确, 维持不动, 撤销回弹假设.
  - 新收录: qidi-q3d(Formnext 2026-11-17 发布, 官店 $599 预售已开放, 销量 pending/E).
"""
import json

SRC = "weekly_data/devices.json"
TODAY = "2026-11-23"
INTEL = "2026-11-23"

d = json.load(open(SRC, encoding="utf-8"))
by_id = {x["id"]: x for x in d}

# ---- 1) 价格变更（>5% 规则; 官方商店优先; 同配置同 list 才比）----
# 本周无: 官店 11-23 抓取值与 W47(11-16) 逐台一致, 黑五(11-27)未到、促销价延续.
price_changes = {}

# ---- 2) 口径冲突（不同配置/渠道价与基线冲突, 按纪律不改数只标注）----
conflict_notes = {
    "bambu-p2s": "口径门案结案(11-23 合集页+商品页双页复核): 合集页 'From $449 / Typical $549' 与基线 $449 完全一致; "
                 "商品页默认 $649 / Typical $749 为另一(Combo/AMS)变体, 差额 $200 即 AMS 套件溢价. "
                 "→ W47 判定的「黑五前反常回弹 +44.5%、页面口径已变」不成立, 撤销该假设; 基线 $449 = 基础版 From 价, 正确且连续两周稳定, 维持不动",
    "bambu-x2d": "口径门案结案(11-23 同上双页复核): 合集页 'From $589 / Typical $649' 与基线 $589 一致; 商品页默认 $789 / Typical $899 为 Combo 变体(+$200). "
                 "→ W47 的「失配 +$200」即变体差, 非涨价; 基线维持 $589",
    "bambu-a2l": "口径门案结案(11-23 同上双页复核): 合集页 'From $439 / Typical $469' 与基线 $439 一致; 商品页默认 $519 / Typical $569 为已知 Combo 官价(+$80). "
                 "→ W47 的「默认变体为 Combo」判断正确, 基线 = 基础版, 维持 $439",
    "bambu-h2d": "官店 11-23 复核: 商品页 $1,599 / Typical $1,749, 与 W47 及基线完全一致, 黑五促销延续、无回弹",
    "bambu-h2s": "官店 11-23 复核: 商品页 $1,249 / Typical $1,399 = 基线, 无变动; 合集页 'From $1,049 / Typical $1,199' 为单机(无 AMS)SKU, "
                 "与基线(含 AMS 配置)不同口径 → 仅标注不改数",
    "bambu-h2c": "官店 11-23 复核: 合集页 $1,899 / Typical $2,199 = 基线($1,899), 促销延续、无变动",
    "bambu-p1s": "官店 11-23 复核: 合集页 'From $349 / Typical $399' 为单机 SKU, 与基线 $499(Combo)不同配置 → 仅标注不改数",
    "bambu-a1": "官店 11-23 复核: 合集页 'From $259 / Typical $299' 为单机 SKU, 与基线 $399(Combo)不同配置 → 仅标注不改数",
}

# ---- 3) 评论增量（同 ASIN 同口径; 窗口 11-16→11-23 = 7 日, 无需折算）----
# 数据源: amazon.com/gp/customer-reviews/widgets/average-customer-review/popover/?asin=<ASIN>&language=en_US
#         返回的 "N global ratings" 为该 ASIN 全站评分数, 与历史基线同口径.
review_updates = {
    "bambu-p1s": {"review_count": 1059, "review_count_date": "2026-11-23", "review_delta_week": 44,
        "growth_basis": "review_delta",
        "review_note": "11-23 抓取 1,059 评分 4.3星(ASIN B0CHDS1DMC 全站评分数); 上期基线 1,015(11-16), 7 日窗口 +44, 无需折算; "
                       "连续两周高位(上周 +40), 黑五(11-27)前备货期动能未衰减"},
    "bambu-a1": {"review_count": 761, "review_count_date": "2026-11-23", "review_delta_week": 11,
        "growth_basis": "review_delta",
        "review_note": "11-23 抓取 761 评分 4.6星(ASIN B0D17TMWFB); 上期 750(11-16), 7 日窗口 +11; 与上周 +15 同量级"},
    "cricut-maker4": {"review_count": 704, "review_count_date": "2026-11-23", "review_delta_week": 10,
        "growth_basis": "review_delta",
        "review_note": "11-23 抓取 704 评分 4.5星(ASIN B0DTQBZ3J3); 上期 694(11-16), 7 日窗口 +10; 与上周 +10 持平"},
    "bambu-a1mini-combo": {"review_count": 416, "review_count_date": "2026-11-23", "review_delta_week": 7,
        "growth_basis": "review_delta",
        "review_note": "11-23 抓取 416 评分 4.1星(ASIN B0CRYZWJLG); 上期 409(11-16), 7 日窗口 +7; 较上周 +1 明显加速"},
    "cricut-explore5": {"review_count": 78, "review_count_date": "2026-11-23", "review_delta_week": 4,
        "growth_basis": "review_delta",
        "review_note": "11-23 抓取 78 评分 4.6星(ASIN B0GS9S3HDQ); 上期 74(11-16), 7 日窗口 +4; 连续两周小幅回升(+3→+4)"},
    "creality-k2plus": {"review_count": 2145, "review_count_date": "2026-11-23", "review_delta_week": 3,
        "growth_basis": "review_delta",
        "review_note": "11-23 抓取 2,145 评分 4.2星(ASIN B0DQTQQBZ9); 上期 2,142(11-16), 7 日窗口 +3; 基数大、增速温和"},
    "bambu-p2s": {"review_count": 35, "review_count_date": "2026-11-23", "review_delta_week": 2,
        "growth_basis": "review_delta",
        "review_note": "11-23 抓取 35 评分 4.5星(ASIN B0FT7ZLSSC 单机口径); 上期 33(11-16), 7 日窗口 +2; 与上周 +2 持平, 基数仍小"},
    "cricut-joyxtra": {"review_count": 1585, "review_count_date": "2026-11-23", "review_delta_week": 1,
        "growth_basis": "review_delta",
        "review_note": "11-23 抓取 1,585 评分 4.5星(ASIN B0CF6L9SMJ); 上期 1,584(11-16), 7 日窗口 +1"},
    "anycubic-kobra-s1-combo": {"review_count": 274, "review_count_date": "2026-11-23", "review_delta_week": 0,
        "growth_basis": "review_delta",
        "review_note": "11-23 抓取 274 评分 3.7星(ASIN B0DBDT2ZZJ); 与上期 274(11-16)持平, 7 日窗口 0 增量 —— 如实记 0"},
    "prusa-mk4": {"review_count": 26, "review_count_date": "2026-11-23", "review_delta_week": 0,
        "growth_basis": "review_delta",
        "review_note": "11-23 抓取 26 评分 4.8星(ASIN B0CKSX4M9F); 与上期 26(11-16)持平, 7 日窗口 0 增量 —— 如实记 0; 连续三周零增长"},
    "prusa-core-one": {"review_count": 40, "review_count_date": "2026-11-23", "review_delta_week": 0,
        "growth_basis": "review_delta",
        "review_note": "11-23 抓取 40 评分 4.7星(ASIN B0FKNGJPK2, Kit 口径); 与上期 40(11-16)持平, 7 日窗口 0 增量 —— 如实记 0; 连续三周零增长"},
}

# 抓取失败: 如实留空(不写 0, 不伪增), 保留上期基线, 下周重试
review_failures = {
    "silhouette-cameo5": "评论抓取失败(11-23 连续两次均返回 'Continue shopping' 机器人墙, 首次请求 + language=en_US 重试仍被拦); "
                         "按纪律留空不写 0, 保留上期基线 762(11-16), 下周重试",
}

# ---- 4) 补链接（营收 Top20 缺链机型已于 W45 全部处置完毕, 本周无需新增）----
tracking_adds = {}
tracking_notes = {}
tracking_misses = {}

# ---- 5) 本周新收录（销量一律 pending 不编造）----
new_models = [
    {
        "id": "qidi-q3d",
        "brand": "QIDI",
        "model": "Q3D",
        "category": "3D打印机",
        "price_usd": 599,
        "price_change_pct": 0,
        "monthly_sales": 0,
        "weekly_growth_pct": 0,
        "description": "QIDI 首款双独立热端封闭机，2026-11-17 Formnext 发布、美国官店已开预售($30 定金)。260×260×260mm 单喷嘴成型(双喷嘴 240×260×255mm)，双热端各自独立料路与挤出模块(换料靠换头而非冲刷)，主热端 350°C、主动腔体加热 70°C、热床 120°C，4 寸触摸屏、玻璃前门。官店 $599(单机)/$749(Combo)，预售定金可全额退并转 $100 券，发货约订单后 3 个月。",
        "key_features": [
            "双独立热端(各带料路/挤出模块)",
            "260×260×260mm 成型",
            "70°C 主动腔体加热",
            "350°C 双金属快换喷嘴",
            "120°C 热床",
            "封闭式+玻璃前门",
            "4 寸触摸屏",
            "$30 定金预售(可全额退)",
        ],
        "is_new": True,
        "social_metrics": {},
        "sales_channels": [
            "QIDI 官方商店(预售)",
            "Amazon(未上架)",
        ],
        "consumables": [
            "PLA/PETG 丝料",
            "工程材料(ABS/ASA/PA/PC)",
        ],
        "consumable_monthly_sales_est": "$0(待积累)",
        "first_tracked_week": "2026-W48",
        "sales_maturity": "new_launch",
        "sales_data_status": "pending",
        "monthly_sales_legacy": 0,
        "sales_confidence": "estimated",
        "sales_grade": "E",
        "growth_basis": "legacy_heat_proxy",
        "verified_note": "[2026-11-23] 首次收录(11-23 联网核实): 11-17 Formnext 2026 发布(3DPrinting.com 报道), "
                         "QIDI 美国官店已挂商品页并可付 $30 定金预售 → 判定「已开售(预售)」故收录; "
                         "官店 $599 单机 / $749 Combo(两档仅毛重 42kg vs 35kg 可见差异, Combo 含配件未明示); "
                         "发货为订单后约 3 个月(即 2027-02 前后), 独立评测尚无 → 月销量无锚点, pending/E 待积累; "
                         "定位: 家用双喷头封闭机 $599 档, 直接对标 Bambu P2S($649)/X2D($789) 与 Prusa CORE One",
    },
]

# ---- 6) 市场动态备注（不改任何设备数值）----
market_notes = {
    "bambu-h2d": "黑五主档期(11-27)倒计时 4 天: 官店 $1,599/Typical $1,749 已连续三周不变, 若 11-27 后仍维持则该价即新常态价、届时可终结「促销价」标注",
    "bambu-h2c": "黑五主档期(11-27)倒计时 4 天: 官店 $1,899/Typical $2,199 连续三周不变, 同上待 11-27 后定性",
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

    if did in review_failures:
        append_note(dev, "[%s] %s" % (TODAY, review_failures[did]))
        # 抓取失败 → 本周增量置 null(未采集), 不保留上期增量冒充本周值; 评论数/日期保留为上期基线.
        dev["review_delta_week"] = None
        dev["review_delta_status"] = "fetch_failed"

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
print("Review failures (blank): %d -> %s" % (len(review_failures), list(review_failures.keys())))
print("Tracking links added: %d -> %s" % (n_track, list(tracking_adds.keys())))
print("Tracking misses noted: %d -> %s" % (len(tracking_misses), list(tracking_misses.keys())))
