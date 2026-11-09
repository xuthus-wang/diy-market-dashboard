#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply 4-dimensional (price/sales/growth/consumable) verified updates to devices.json.
Date: 2026-11-09 (W46 周一例行核实).
情报采集日: 2026-11-09 联网核实 (预算 18/20 次). 无伪造: 仅写入有来源的信号, 冲突口径只标注不改数.
要点:
  - Amazon 反爬本周解除(dp 页可读 + average-customer-review popover 直出 rating 总数):
    12 台追踪 ASIN 全部取得当前评分数, 0 失败(上两周全量失败). 增量口径首度打通.
    但 3 台历史基线取自搜索结果快照(k2plus/cameo5/joyxtra), 与本页总评分数不可比
    (124→761 / 1182→1584 / 866→2142), 判定口径变更: 仅重建基线, 本周不计增量(不喂 growth_proxy).
  - 价格: 5 台官方商店黑五促销价记入(同配置同 list, 仅成交价下调):
    h2d $1,749→$1,599 / p2s $549→$449 / x2d $649→$589 / h2c $2,199→$1,899 / a2l $469→$439.
    陷阱排除: 官店合集页「From」价为最低配 SKU, 与 Combo 基线不同配置, 不可直接比:
    h2s 合集页 From $1,049 曾疑似 -16%, 但商品页同配置仍为 $1,249/Typical $1,399 = 基线, 判定无变动.
  - 新收录: bambu-h3c(九材料 Tool Changer, 11-3 上市, 官店 $2,499 起, 已开售), 销量 pending.
  - 评论基线: cricut-maker4 连续四周失败后首次建立(684 评分); prusa-mk4 首次落盘(26, 与 10-26 持平).
"""
import json

SRC = "weekly_data/devices.json"
TODAY = "2026-11-09"
INTEL = "2026-11-09"

d = json.load(open(SRC, encoding="utf-8"))
by_id = {x["id"]: x for x in d}

# ---- 1) 价格变更（>5% 规则; 官方商店优先; 同配置同 list 才比）----
price_changes = {
    "bambu-h2d": (1599, -8.6,
        "Bambu US 官店 H2D 商品页 11-9 抓取: 现价 $1,599, 官店自标 Typical Price $1,749(=基线原值), "
        "同一 AMS Combo 变体 list 未变、成交价下调 -8.6%(证据强·官方商店, 黑五档期促销); "
        "注: 合集页 'From $1,399' 为单机(无 AMS)低配 SKU 口径, 与基线不同配置, 不采; "
        "促销结束后如回弹 $1,749 将按回弹记 +9.4%"),
    "bambu-p2s": (449, -18.2,
        "Bambu US 官店 P2S 合集页 11-9 抓取: From $449, 自标 Typical Price $549(=基线单机价), "
        "同配置 list 未变、成交价下调 -18.2%(证据强·官方商店, 黑五促销); "
        "促销结束回弹 $549 将记 +22.3%"),
    "bambu-x2d": (589, -9.2,
        "Bambu US 官店 X2D 合集页 11-9 抓取: From $589, 自标 Typical Price $649(=基线), "
        "同配置 list 未变、成交价下调 -9.2%(证据强·官方商店, 黑五促销)"),
    "bambu-h2c": (1899, -13.6,
        "Bambu US 官店 H2C 合集页 11-9 抓取: From $1,899, 自标 Typical Price $2,199(=基线首发价), "
        "上市一个月后首次进入促销档 -13.6%(证据强·官方商店); 该机型销量仍 pending, 价格先行走"),
    "bambu-a2l": (439, -6.4,
        "Bambu US 官店 A2L 合集页 11-9 抓取: From $439, 自标 Typical Price $469(=基线), "
        "同配置 list 未变、成交价下调 -6.4%(证据强·官方商店, 黑五促销); 幅度刚过 5% 阈值, 按纪律记入"),
}

# ---- 2) 口径冲突（不同配置/渠道价与基线冲突, 按纪律不改数只标注）----
conflict_notes = {
    "bambu-h2s":     "Bambu US 官店 11-9 复核: 商品页同配置(AMS Combo)仍为 $1,249 / Typical $1,399, 与基线完全一致, 本周无变动; "
                     "但合集页显示 'From $1,049 / Typical $1,199', 经核实为 H2S 单机(无 AMS)SKU 口径 —— "
                     "若直接采 'From' 价会误判为 -16% 降价, 实为配置不同, 不采; 基线维持 $1,249",
    "bambu-p1s":     "Bambu US 官店合集页 11-9: From $349 / Typical $399(单机口径, 上周为 $509/$579, 即单机亦进入黑五促销 -31%); "
                     "基线 $499 为 Amazon Combo 口径(ASIN B0CHDS1DMC), 配置与渠道口径仍不对齐, 不构成同口径变更; 维持基线待口径对齐",
    "bambu-a1":      "Bambu US 官店合集页 11-9: From $259 / Typical $299 —— 为 A1 单机口径; 基线 $399 为 A1 Combo 口径, 配置不同不可直接比 "
                     "(与 10-9 记录的 $299 单机价一致), 维持基线",
    "bambu-a1mini-combo": "Bambu US 官店合集页 11-9: From $199 / Typical $219 —— 为 A1 mini 单机口径; 基线 $329 为 A1 mini Combo 口径, 配置不同不可直接比, 维持基线",
}

# ---- 3) 评论增量（同 ASIN 同口径; 窗口不足 7 日不折算, 超 7 日按日折周）----
# 数据源: amazon.com/gp/customer-reviews/widgets/average-customer-review/popover/?asin=<ASIN>
#         返回的 "N global ratings" 为该 ASIN 全站评分数, 与历史基线同口径(dp 页 Product information 亦一致).
review_updates = {
    # —— 有效增量（用于 growth_proxy）——
    "bambu-p1s": {"review_count": 975, "review_count_date": "2026-11-09", "review_delta_week": 31,
        "growth_basis": "review_delta",
        "review_note": "11-9 抓取 975 评分 4.3星(ASIN B0CHDS1DMC 全站评分数); 上期基线 914(10-26), 14 日窗口增量 +61, 折周 +31; "
                       "含黑五促销窗口, 增量偏高需下周复核常态"},
    "bambu-p2s": {"review_count": 31, "review_count_date": "2026-11-09", "review_delta_week": 2.5,
        "growth_basis": "review_delta",
        "review_note": "11-9 抓取 31 评分 4.6星(ASIN B0FT7ZLSSC 单机口径); 上期 26(10-26), 14 日窗口 +5, 折周 +2.5; "
                       "绝对量级小, 单条评论即可显著扰动折周值"},
    "prusa-core-one": {"review_count": 40, "review_count_date": "2026-11-09", "review_delta_week": 0.5,
        "growth_basis": "review_delta",
        "review_note": "11-9 抓取 40 评分 4.7星(ASIN B0FKNGJPK2, Kit 口径); 上期 39(10-26), 14 日窗口 +1, 折周 +0.5; 接近零增长"},
    "prusa-mk4": {"review_count": 26, "review_count_date": "2026-11-09", "review_delta_week": 0.0,
        "growth_basis": "review_delta",
        "review_note": "11-9 抓取 26 评分 4.8星(ASIN B0CKSX4M9F); 与 10-26 记录的 26 持平, 14 日窗口 0 增量 —— 如实记 0, 不写 null; "
                       "首次把该值落盘到基线(此前仅存于运行记录)"},
    "bambu-a1mini-combo": {"review_count": 408, "review_count_date": "2026-11-09", "review_delta_week": 7.3,
        "growth_basis": "review_delta",
        "review_note": "11-9 抓取 408 评分 4.2星(ASIN B0CRYZWJLG); 上期 381(10-14), 26 日窗口 +27, 折周 +7.3; "
                       "窗口过长(两周反爬未取到数), 折算值置信度低于 7 日窗口"},
    "bambu-a1": {"review_count": 735, "review_count_date": "2026-11-09", "review_delta_week": 21.0,
        "growth_basis": "review_delta",
        "review_note": "11-9 抓取 735 评分 4.6星(ASIN B0D17TMWFB); 上期 657(10-14), 26 日窗口 +78, 折周 +21; 同上, 26 日窗口折算"},
    "cricut-explore5": {"review_count": 71, "review_count_date": "2026-11-09", "review_delta_week": 11.0,
        "growth_basis": "review_delta",
        "review_note": "11-9 抓取 71 评分 4.6星(ASIN B0GS9S3HDQ); 上期 30(10-14), 26 日窗口 +41, 折周 +11; "
                       "新品放量期, 相对增速(+137%)显著, 但基数仅 71 条, 区间宽"},
    "anycubic-kobra-s1-combo": {"review_count": 272, "review_count_date": "2026-11-09", "review_delta_week": 24.0,
        "growth_basis": "review_delta",
        "review_note": "11-9 抓取 272 评分 3.7星(ASIN B0DBDT2ZZJ); 上期 248(11-2), 7 日窗口 +24, 无需折算; "
                       "3.7 星为本次追踪机型中最低, 与 W45 记录的 3.5 星口碑风险一致(略回升)"},
    # —— 口径变更: 历史基线取自搜索快照, 与全站总评分数不可比, 仅重建基线 ——
    "creality-k2plus": {"review_count": 2142, "review_count_date": "2026-11-09", "review_delta_week": None,
        "review_note": "口径变更: 11-9 直抓 popover 得 2,142 评分 4.2星(ASIN B0DQTQQBZ9 全站总评分数), "
                       "上周基线 866(10-19) 取自 Amazon 搜索结果快照, 二者非同一口径(搜索快照疑为子变体/滞后值), "
                       "3 周内 +1,276 不合常理, 判定口径变更 → 本周不计增量、不喂 growth_proxy, 以 2,142 重建基线, 下周起记增量"},
    "silhouette-cameo5": {"review_count": 761, "review_count_date": "2026-11-09", "review_delta_week": None,
        "review_note": "口径变更: 11-9 直抓 popover 得 761 评分 4.4星(ASIN B0CHY4NWPX 全站总评分数), "
                       "上期基线 124(10-19) 取自搜索快照, 6 倍差异不可能是真实增长, 判定口径变更 → 本周不计增量, 以 761 重建基线, 下周起记增量"},
    "cricut-joyxtra": {"review_count": 1584, "review_count_date": "2026-11-09", "review_delta_week": None,
        "review_note": "口径变更: 11-9 直抓 popover 得 1,584 评分 4.6星(ASIN B0CF6L9SMJ Machine Only 全站总评分数), "
                       "上期基线 1,182(11-2) 取自搜索快照, 7 日 +402(+34%) 对成熟机型不合常理, 判定口径变更 → 本周不计增量, 以 1,584 重建基线, 下周起记增量"},
    "cricut-maker4": {"review_count": 684, "review_count_date": "2026-11-09", "review_delta_week": None,
        "review_note": "11-9 抓取 684 评分 4.5星(ASIN B0DTQBZ3J3) —— 连续四周抓取失败后首次建立基线(W43/W44/W45 均被反爬阻断); "
                       "本周无上期基线, 不计增量; 下周起记增量"},
}

# ---- 4) 补链接（营收 Top20 缺链机型已于 W45 全部处置完毕, 本周无需新增）----
tracking_adds = {}
tracking_notes = {}
tracking_misses = {}

# ---- 5) 本周新收录（销量一律 pending 不编造）----
new_models = [
    {
        "id": "bambu-h3c",
        "brand": "Bambu Lab",
        "model": "H3C",
        "category": "3D打印机",
        "price_usd": 2499,
        "price_change_pct": 0,
        "monthly_sales": 0,
        "weekly_growth_pct": 0,
        "description": "拓竹九材料换头(Tool Changer)旗舰，2026-11-03 上市、美国官店已开售。"
                       "9 条独立料路、6 秒换头、料架内置并带烘干，330×320×325mm 成型空间，"
                       "可选激光/切割/绘图/压印多工艺模块，工具头与 X 轴减重 40%，"
                       "9 个硬化钢喷嘴均支持 350°C，双区主动腔体加热至 65°C。",
        "key_features": [
            "9 材料独立料路",
            "6 秒换头(Tool Changer)",
            "内置料架+烘干",
            "330×320×325mm",
            "可选激光/切割/绘图/压印",
            "350°C 喷嘴+65°C 腔体",
            "9 硬化钢喷嘴",
            "25,000mm/s 加速度",
        ],
        "is_new": True,
        "social_metrics": {},
        "sales_channels": ["Bambu 官方商店", "Amazon"],
        "consumables": ["PLA/PETG 丝料", "工程材料(ABS/PC/PA-CF/PET-CF)"],
        "consumable_monthly_sales_est": "$0(待积累)",
        "first_tracked_week": "2026-W46",
        "sales_maturity": "new_launch",
        "sales_data_status": "pending",
        "monthly_sales_legacy": 0,
        "sales_confidence": "estimated",
        "sales_grade": "E",
        "growth_basis": "legacy_heat_proxy",
        "last_verified": TODAY,
        "verified_note": "[2026-11-09] 首次收录(11-9 联网核实): Bambu 官宣 11-3 上市、美国官店已开售(合集页 'New' 标记); "
                         "官店 $2,499 起(单机, 未见 Typical 标价即无折扣); 上市 6 天, 月销量无锚点 → pending, 待积累; "
                         "9 材料换头为拓竹首次进入 Tool Changer 赛道(对标 Prusa CORE One/Bambu 自家 AMS 多色路线升级)",
    },
]

# ---- 6) 市场动态备注（不改任何设备数值）----
market_notes = {
    "bambu-h2c": "黑五档期: Bambu 全线官店进促销(H2D/H2S/P2S/X2D/H2C/A2L/P1S/A1 均挂典型价折扣), 折扣率 6.4%~31%, "
                 "为今年观察到的最大幅度官店促销; H3C 新品未参与折扣(维持 $2,499)",
    "cricut-maker4": "营收 Top20 缺链机型已于 W45 全部处置完毕, 本周补链工作量 0; maker4 评论基线四周后终于建立(684 评分), 下周起可算增量",
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

    # price_change_pct 语义 = 「本周」变动率。历史实现从不归零, 导致上上周/上月的变动率
    # 无限期挂在排行榜箭头上、且看板「价格异动」KPI 累计虚报(W45 实报 34 而真实仅 1 台)。
    # 本周起按周归零: 未变动机型一律 0; 历史变动幅度已逐条写在 verified_note, 不丢信息。
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
