#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""Apply 4-dimensional (price/sales/growth/consumable) verified updates to devices.json.
Date: 2026-10-14 (W42 补刊; 原周一沙箱失效, 数据恢复后补发).
情报采集日: 2026-10-09 联网核实. 无伪造: 仅写入有来源的信号, 冲突口径只标注不改数.
"""
import json

SRC = "weekly_data/devices.json"
TODAY = "2026-10-14"
INTEL = "2026-10-09"

d = json.load(open(SRC, encoding="utf-8"))
by_id = {x["id"]: x for x in d}

# ---- 1) 价格变更（>5% 规则; 证据: Cricut 官网+渠道聚合, 且与基线已核实的 Explore5=$199 交叉一致）----
price_changes = {
    "cricut-explore4": (199, -33.4,
        "Cricut 渠道聚合价 $299→$199(-33.4%); 与同系 Explore 5 官方价 $199 交叉一致, 证据较强(Maker 5 上市后全系压价)"),
    "cricut-joyxtra": (129, -27.9,
        "Cricut 渠道聚合价 $179→$129(-27.9%), 证据: 渠道聚合(中等)"),
    "cricut-maker4": (379, -5.0,
        "Cricut 渠道聚合价 $399→$379(-5.0%,压线过>5%阈值), 证据: 渠道聚合(中等); 受 Maker 5($349) 上市挤压"),
}

# ---- 2) 口径冲突（有媒体/第三方价但与 9-29 基线冲突, 按纪律不改数只标注）----
conflict_notes = {
    "xtool-f1":        "基线 $999 vs 媒体渠道(engraverhq 10-09) $1,099, 差异或为含配件套餐价, 维持基线待官方店复核",
    "xtool-p2s":       "基线 $2,799 vs 媒体渠道 $3,399(+21.4%), 6周内涨幅异常, 疑套餐价, 维持基线待复核",
    "xtool-s1":        "基线 $1,299 vs 媒体渠道 $1,699(+30.8%), 疑套餐价, 维持基线待复核",
    "xtool-m1ultra":   "基线 $999 vs 媒体渠道 $1,099(+10.0%), 与同门 F1/P2S/S1 疑似套餐价干扰同源, 维持基线待复核",
    "bambu-h2s":       "基线 $1,399 vs 第三方对比表 $1,249(-10.7%), 或为促销价, 维持基线待官方店复核",
    "bambu-a1":        "基线 $399 vs 官网页 $299(-25.1%), 可能 Combo/单机口径差异, 维持基线待复核",
    "eufymake-e1":     "基线 $2,299 vs 文章口径 $2,499, 渠道差异; 另国内二手价跌至约¥7,000(首发¥13,999, 腰斩), 喷头堵塞/耗材成本为投诉焦点(需求端预警信号)",
}

# ---- 3) 本周新收录（基线未收录, 来源: 10-09 联网核实; 销量无锚点 → pending 不编造）----
new_models = [
    {
        "id": "bambu-h2c", "brand": "Bambu Lab", "model": "H2C",
        "category": "FDM 3D打印机",
        "price_usd": 2199, "price_change_pct": 0,
        "monthly_sales": 0, "weekly_growth_pct": 0,
        "description": "拓竹 H2C 多色 FDM 机型(2026-10-09 联网核实首发价 $2,199)。此前 9-29 基线未收录, 本次首次登记; 详细规格待复核补充。",
        "key_features": ["多色打印(待复核)"],
        "is_new": True,
        "social_metrics": {},
        "sales_channels": ["Bambu 官方商店", "Amazon"],
        "consumables": ["PLA/PETG/ABS 丝料"],
        "consumable_monthly_sales_est": "$0(待积累)",
        "last_verified": TODAY,
        "verified_note": "[2026-10-14] 首次收录(10-09 联网搜索+官方商店页发现, 首发价 $2,199); 月销量无锚点 → pending, 待积累; 规格待复核",
        "first_tracked_week": "2026-W42",
        "sales_maturity": "new_launch",
        "sales_data_status": "pending",
    },
    {
        "id": "bambu-x2d", "brand": "Bambu Lab", "model": "X2D",
        "category": "FDM 3D打印机",
        "price_usd": 649, "price_change_pct": 0,
        "monthly_sales": 0, "weekly_growth_pct": 0,
        "description": "拓竹 X2D 入门机型(2026-10-09 联网核实首发价 $649)。此前 9-29 基线未收录, 本次首次登记; 详细规格待复核补充。",
        "key_features": ["入门级(待复核)"],
        "is_new": True,
        "social_metrics": {},
        "sales_channels": ["Bambu 官方商店", "Amazon"],
        "consumables": ["PLA/PETG 丝料"],
        "consumable_monthly_sales_est": "$0(待积累)",
        "last_verified": TODAY,
        "verified_note": "[2026-10-14] 首次收录(10-09 联网搜索发现, 首发价 $649); 月销量无锚点 → pending, 待积累; 规格待复核",
        "first_tracked_week": "2026-W42",
        "sales_maturity": "new_launch",
        "sales_data_status": "pending",
    },
]

# ---- 4) 市场动态备注（不改任何设备数值, 写入对应设备 note）----
market_notes = {
    "heygears-g1x":   "UV 赛道资本涌入: HeyGears G1 众筹 24h $722 万(10-09 口径)",
    "morpho-uv-standard": "Morpho 众筹 48h 超 $900 万(10-09 口径); UV 赛道竞争加剧",
}

def append_note(dev, line):
    dev["verified_note"] = (dev.get("verified_note") or "") + "\n" + line

generic = ("[%s] 联网核实(情报日 %s): 价格无>5%%变动维持; 销量无新权威锚点维持; "
           "增长无方向性新信号维持; 耗材价稳维持" % (TODAY, INTEL))

n_price = n_conflict = 0
for dev in d:
    dev["last_verified"] = TODAY
    did = dev["id"]

    if did in price_changes:
        new_p, pct, why = price_changes[did]
        old_p = dev["price_usd"]
        dev["price_usd"] = new_p
        dev["price_change_pct"] = pct
        append_note(dev, "[%s] 价格 %s; 销量/增长/耗材维持" % (TODAY, why))
        n_price += 1
        continue

    if did in conflict_notes:
        append_note(dev, "[%s] 口径冲突(情报日 %s): %s" % (TODAY, INTEL, conflict_notes[did]))
        n_conflict += 1
        continue

    if did in market_notes:
        append_note(dev, "[%s] %s; 四维数值维持" % (TODAY, market_notes[did]))
        continue

    append_note(dev, generic)

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
    print("  %s: -> $%s (%s%%)" % (k, np, pct))
print("Conflict notes (no change): %d -> %s" % (n_conflict, list(conflict_notes.keys())))
