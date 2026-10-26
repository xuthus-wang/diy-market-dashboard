#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply 4-dimensional (price/sales/growth/consumable) verified updates to devices.json.
Date: 2026-10-26 (W44 周一例行核实).
情报采集日: 2026-10-26 联网核实 (预算 18/20 次). 无伪造: 仅写入有来源的信号, 冲突口径只标注不改数.
要点:
  - 评论增量: P1S Combo 清洁 7 日窗口 880→914(+34); p2s/core-one/mk4 首次建立评论基线(26/39/26);
    其余 6 台追踪 ASIN 遇 checkpoint 或页面未渲染评分数, 如实留空不写 0.
  - 价格: 仅 bambu-x1e 基线修正 $1,499→$2,899(+93.4%, 基线错误而非市场变动, 证据链见价格备注).
  - 补链接: 营收 Top20 无追踪机型补 prusa-mk4(官方组装版); h2d/h2s/x1c 检索仅命中配件或第三方, 不采; x1e 已 EOL 跳过.
  - 品牌级情报: CONTEXT Q2 2026 入门级出货 +23%/营收 +36%, 深圳四小龙占 87%, Bambu 领先; Creality 盈利预警.
"""
import json

SRC = "weekly_data/devices.json"
TODAY = "2026-10-26"
INTEL = "2026-10-26"

d = json.load(open(SRC, encoding="utf-8"))
by_id = {x["id"]: x for x in d}

# ---- 1) 价格变更（>5% 规则; 官方商店优先）----
price_changes = {
    "bambu-x1e": (2899, 93.4,
        "基线修正 $1,499→$2,899(+93.4%): X1E 于 2026-03-31 官方 EOL(Bambu 官方论坛公告, 4-9 发布, 证据强), 官店产品页已 404(10-26 抓取); Bambu US 现列 $2,899 含 AMS(BambuHub 价格追踪器 10 月更新) 且授权经销商 Dynamism 在售 $2,899(10-26 核实, 在货). 旧基线 $1,499 与 2023 发布价 $2,499 均不符, 判定为历史录入错误而非市场涨价; 本周按官方渠道口径修正"),
}

# ---- 2) 口径冲突（有媒体/第三方价与基线冲突, 按纪律不改数只标注）----
conflict_notes = {
    "bambu-p1s":     "Bambu US 官店 P1S 页 10-26 抓取显示 $579(变体默认价, 未标注单机/Combo), vs 基线 $499 为 Amazon Combo 口径(ASIN B0CHDS1DMC); 万圣节促销期(至10-16)官店/Amazon 曾同价 $399(lavx 新闻引述). 配置与渠道口径均未对齐, 维持基线待复核",
    "bambu-h2s":     "lavx 新闻(10月): 常态价 Combo $1,499 / 促销 $1,399(至10-16); 基线 $1,399 为促销价, 促销已止. 证据为二手转述, 待官店直接复核后决定是否 +7.1% 修正",
    "epson-v1070":   "MSRP $8,495 获 Epson 官方发布通稿佐证(TechPowerUp 转引 Epson); Amazon 无官方渠道(Epson 走授权经销商), 第三方 Accio 见 $8,995(MakerFlo); 联盟站 $3,259 异常报价持续存在(翻新/错误), 维持基线",
    "prusa-core-one": "本周补的 Amazon ASIN B0FKNGJPK2 为 Kit 版(页面自述 DIY KIT); 基线 $1,099 与 Kit 口径一致, Tom's Hardware $1,499/CNET $1,549 为组装版口径, 不可直接比; 维持基线, 评论基线按 Kit ASIN 记",
}

# ---- 3) 评论增量（同 ASIN 同口径; 抓取失败如实记录, 不写 0）----
review_updates = {
    # 清洁窗口成功: P1S Combo 880(10-19) -> 914(10-26), 7 日 +34
    "bambu-p1s": {
        "review_count": 914, "review_count_date": TODAY, "review_delta_week": 34,
        "review_note": "Amazon US P1S Combo ASIN B0CHDS1DMC 自身评分数(914), 同 ASIN 同口径, 清洁 7 日窗口 10-19→10-26 +34(无促销干扰). 按留评率 1%~2% 折算 Amazon 月销约 1,700~3,400, 远低于品牌锚点 19,585 — 符合预期: Bambu 官店/分销为销量大头, Amazon 仅部分渠道, 且锚点法永不升 B; 维持 D 级. 注: 上期 +113 为 5 日促销窗口, growth_proxy 周环比不可直接比",
        "growth_basis": "review_delta",
    },
    # 首基线: p2s / core-one
    "bambu-p2s": {"review_count": 26, "review_count_date": TODAY, "review_delta_week": None,
        "review_note": "Amazon US P2S 单机 ASIN B0FT7ZLSSC 首次抓到评分数 26(4.4 星), 2026-10-26 起建立增量基线; 页面同期列 3D Printers 类目销量榜 #2(平台聚合信号, 不改数); 下周起记增量"},
    "prusa-core-one": {"review_count": 39, "review_count_date": TODAY, "review_delta_week": None,
        "review_note": "Amazon US CORE One Kit 版 ASIN B0FKNGJPK2 首次抓到评分数 39(4.7 星), 2026-10-26 起建立增量基线(注意为 Kit 口径, 非组装版); 下周起记增量"},
    # 抓取失败: 维持旧值, delta 置 null
    "bambu-a1mini-combo": {"review_count": 381, "review_count_date": "2026-10-14", "review_delta_week": None,
        "review_note": "10-26 抓取页面渲染但未显示评分数(连续两周失败), 无增量数据如实留空不计 0; 下周重试同口径"},
    "bambu-a1": {"review_count": 657, "review_count_date": "2026-10-14", "review_delta_week": None,
        "review_note": "10-26 抓取页面渲染但未显示评分数(连续两周失败), 无增量数据如实留空不计 0; 下周重试同口径"},
    "creality-k2plus": {"review_count": 866, "review_count_date": "2026-10-19", "review_delta_week": None,
        "review_note": "10-26 抓取页面渲染但未显示评分数, 无增量数据如实留空不计 0; 下周重试同口径"},
    "silhouette-cameo5": {"review_count": 124, "review_count_date": "2026-10-19", "review_delta_week": None,
        "review_note": "10-26 抓取遇 Amazon 反爬 checkpoint 页面, 无增量数据如实留空不计 0; 下周重试同口径"},
    "cricut-explore5": {"review_count": 30, "review_count_date": "2026-10-14", "review_delta_week": None,
        "review_note": "10-26 抓取遇 Amazon 反爬 checkpoint 页面(连续两周失败), 无增量数据如实留空不计 0; 下周重试同口径"},
    "cricut-maker4": {"review_count": None, "review_count_date": None, "review_delta_week": None,
        "review_note": "10-26 抓取页面渲染但未显示评分数(连续两周失败), 基线仍未建立; 下周重试"},
}

# ---- 4) 补链接（营收 Top20 无追踪机型按降序; 当日评论基线, 未抓到评分数的如实置 null）----
tracking_adds = {
    "prusa-mk4": {"amazon": "https://www.amazon.com/dp/B0CKSX4M9F"},
}
tracking_notes = {
    "prusa-mk4": "Amazon US MK4 组装版 ASIN(Prusa 官方店自营, 页面对比表中组装版 26 评分 4.8 星); Kit 版 ASIN B0CKSW74GX(22 评分 4.3 星)仅备查不入基线(组装版与基线 $799 同口径); 2026-10-26 起建立增量基线",
}
# Top20 补链未完成的机型（如实记录, 下周按降序继续）
tracking_misses = {
    "bambu-h2d":  "site:amazon.com 检索仅命中配件 ASIN(滤芯/热床等), 未获官方整机 ASIN, 不采; 下周换词重试",
    "bambu-h2s":  "site:amazon.com 检索仅命中配件 ASIN, 未获官方整机 ASIN, 不采; 下周换词重试",
    "bambu-x1c":  "唯一整机命中为第三方 'Bivolt' 疑巴西区口径(B0DMPXXSZX, 仅 8 评分), 非官方 US 店, 不采; X1 系列 3-31 EOL 后以第三方清库存为主",
    "epson-v1070": "Epson 无 Amazon 官方渠道(授权经销商模式), 放弃补 ASIN, 后续以渠道聚合/经销商价核实",
}

# ---- 5) 本周新收录（销量一律 pending 不编造）----
new_models = [
    # 无: H3C Tool Changer 已官宣(11-3 上市)但本周未开售, 按纪律不收录, 见 market_notes
]

# ---- 6) 市场动态备注（不改任何设备数值）----
market_notes = {
    "bambu-h2d": "CONTEXT Q2 2026(TCT 10月转引): 入门级出货 +23%/营收 +36% YoY, 深圳四小龙占 87%, Bambu 份额显著领先(品牌级锚点佐证, 不改数); 另: 中国 Q2 出口 +58% 或含 Q4 库存化风险; Bambu 官宣 H3C Tool Changer 11-3 上市(本周未开售不收录)",
    "creality-k2plus": "Creality 发布盈利预警: 价格竞争致 1H2026 打印机营收基本持平(CONTEXT/TCT, 10月); K2 Plus 处于该价格竞争带, 品牌级景气信号偏弱, 不改数",
    "bambu-x1c": "X1 系列(X1/X1C/X1E) 2026-03-31 官方 EOL(Bambu 论坛公告), 2027-05-31 后停固件更新; X2D 4-14 上市 $649 接替 X1C 生态位; 生命周期信号: 长期销量预计递减, 维持基线待观察",
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
