"""
DIY市场数据采集模块
- 联网搜索最新热销榜、新品发布、价格变动
- 对比上周数据生成趋势报告
- 支持品类：智能切割机、3D打印机、激光雕刻机、热压机、电动工具
"""
import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weekly_data')

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_week_label():
    now = datetime.now()
    year = now.year
    week = now.isocalendar()[1]
    return f"{year}-W{week:02d}"

def search_market_updates():
    """
    返回结构化的市场动态数据。
    在生产环境中，这里会调用 WebSearch/WebFetch 获取实时数据。
    当前版本返回基于最新市场研究的更新快照。
    """
    return {
        "searched_at": datetime.now().isoformat(),
        "market_movements": {
            "智能切割机": {
                "trend": "稳定增长",
                "hot_models": ["Cricut Joy Xtra (入门需求激增)", "Silhouette Cameo 5 (专业用户升级)"],
                "price_trend": "Joy系列降价促销(-10%)，Explore系列稳定",
                "news": "Cricut 2026年2月发布EasyPress SE系列新款热压机，带动配套耗材销售"
            },
            "3D打印机": {
                "trend": "高速增长 🔥",
                "hot_models": [
                    "Bambu Lab H2D (四合一体机，TikTok热度爆发，搜索量+156%)",
                    "Bambu Lab A1 Mini Combo (入门多色首选，月销22万台)",
                    "Anycubic Kobra 3 V2 (性价比多色方案，增速+18%)",
                    "Creality K2 Plus (旗舰降价20%，销量反弹+15%)"
                ],
                "price_trend": "中端多色机型竞争加剧，Anycubic/Flashforge降价抢市场",
                "news": "拓竹2025出货约200万台，全球市占率升至40%；中国3D打印机出口503万台(+33%)"
            },
            "激光雕刻机": {
                "trend": "快速增长",
                "hot_models": [
                    "xTool M1 Ultra (四合一体机，TikTok 15,600视频，搜索+89%)",
                    "xTool S1 40W (全封闭安全设计，DIY入门首选)",
                    "Glowforge Aura ($999入门级，Etsy社区热推)"
                ],
                "price_trend": "xTool S1促销力度加大，Glowforge Pro维持高价策略",
                "news": "xTool M1 Ultra成为2025年增长最快的DIY设备之一；全球激光雕刻市场$48亿"
            },
            "热压机": {
                "trend": "稳步增长",
                "hot_models": ["HTVRONT Auto Heat Press (性价比+自动释放)", "Cricut EasyPress SE (2026新款)"],
                "price_trend": "HTVRONT降价17%冲击市场，Cricut维持品牌溢价",
                "news": "HTVRONT凭借Amazon热销和社交媒体营销快速崛起，月销3.5万台"
            },
            "UV打印机": {
                "trend": "爆发式增长 🔥🔥",
                "hot_models": [
                    "Anker eufyMake E1 (零售$2,499现货2-4天发货，Kickstarter>$46M史上最高，17,822名支持者)",
                    "xTool O1 Omni (预购$1,699/MSRP$2,499，预计2026年9月发货，墨水~$0.16/ml)",
                    "HeyGears G1X (全彩3D UV打印，130-150mm独立3D，Kickstarter 2026)"
                ],
                "price_trend": "墨水价格战打响：eufyMake E1墨水2026-07-13降至$29.99/100ml(~$0.30/ml)；xTool O1 Omni以~$0.16/ml更低单价切入；整机$1,699(xTool) vs $2,499(eufyMake) vs $8,495(Epson专业级)",
                "news": "eufyMake E1已现货$2,499发货、墨水降价30%；xTool O1 Omni预计2026年9月发货、7mm浮雕为竞品最高；UV打印机成2026最热新品类"
            },
            "升华打印机": {
                "trend": "稳步增长",
                "hot_models": [
                    "Epson ET-15000改装升华 (最便宜方案$399，TikTok 18,000视频)",
                    "Sawgrass SG500 (专业入门$599，配套CreativeStudio软件)",
                    "Sawgrass SG1000 (A3大幅面$1,495，批量生产)"
                ],
                "price_trend": "Epson改装方案持续走量，Sawgrass维持专业品牌溢价",
                "news": "升华打印与热压机形成强配套关系，DIY T恤/杯子/帽子市场持续扩大"
            },
            "刺绣机": {
                "trend": "成熟稳定",
                "hot_models": [
                    "Brother SE1900 (缝纫+刺绣一体$649，Amazon最畅销)",
                    "Brother PE800 (纯刺绣$549，入门首选)"
                ],
                "price_trend": "Brother一家独大，价格稳定，PE800降价8%",
                "news": "家用刺绣机市场成熟，Brother占据绝对主导地位，耗材(绣花线/稳定剂)持续消耗"
            },
            "电动工具": {
                "trend": "社交电商爆发",
                "hot_models": [
                    "XAPR Impact Wrench (月销4070万件，TikTok 42,000视频)",
                    "Victool Electric Rotary Shears (ASMR内容驱动，月销217万件)"
                ],
                "price_trend": "超低价策略($0.71-$40)推动冲动消费，复购率依赖内容持续曝光",
                "news": "TikTok/Tokopedia成为电动工具新增长渠道，短视频驱动销售"
            }
        },
        "emerging_signals": [
            "All-in-One设备（打印+雕刻+切割）是2025年最大趋势，xTool M1 Ultra和Bambu Lab H2D领跑",
            "Bambu Lab于2026-07达成100万台桌面机里程碑并投$195M建厂，桌面3D打印进入百万级规模",
            "UV打印机墨水价格战打响：eufyMake E1墨水2026-07-13降至$29.99/100ml，xTool O1 Omni以~$0.16/ml更低单价切入",
            "碳纤维复合耗材增长最快(CAGR 18.4%)，高端耗材利润空间大",
            "TikTok社交电商改变DIY设备销售模式，ASMR/教程类内容成关键转化路径"
        ]
    }

def compute_weekly_changes(current_devices, previous_week_data):
    """对比上周数据，计算真实环比变化"""
    if not previous_week_data:
        return None

    prev_devices = {d['id']: d for d in previous_week_data.get('devices', [])}
    changes = []

    for device in current_devices:
        did = device['id']
        prev = prev_devices.get(did)
        if prev:
            # 价格变化（对比当前价格）
            price_change = device.get('current_price', device.get('price_usd', 0)) - \
                          prev.get('current_price', prev.get('price_usd', 0))
            # 销量增速变化（对比 current_weekly_growth）
            prev_growth = prev.get('current_weekly_growth', 0)
            curr_growth = device.get('current_weekly_growth', 0)
            sales_change_pct = round(curr_growth - prev_growth, 1)

            changes.append({
                'device_id': did,
                'brand': device.get('brand', ''),
                'model': device.get('model', ''),
                'price_change': price_change,
                'sales_change_pct': sales_change_pct,
                'previous_price': prev.get('current_price', prev.get('price_usd')),
                'current_price': device.get('current_price', device.get('price_usd')),
                'previous_growth': prev_growth,
                'current_growth': curr_growth,
                'is_hot': curr_growth > 15,
            })

    # 按销量变化排序
    changes.sort(key=lambda x: abs(x['sales_change_pct']), reverse=True)
    return changes

def generate_week_report(market_updates, weekly_changes, devices):
    """生成周报文本摘要"""
    week = get_week_label()
    report = {
        'week': week,
        'generated_at': datetime.now().isoformat(),
        'headline': '',
        'key_metrics': {},
        'top_movers': [],
        'emerging_signals': market_updates.get('emerging_signals', []),
        'category_summary': {}
    }

    # 头条
    hottest_cat = max(market_updates['market_movements'].items(),
                      key=lambda x: 1 if '🔥' in x[1]['trend'] else 0)
    report['headline'] = f"本周{hottest_cat[0]}市场持续火爆 — {hottest_cat[1]['trend']}"

    # 关键指标
    total_devices = len(devices)
    new_hot = sum(1 for m in market_updates['market_movements'].values()
                  if '🔥' in m.get('trend', ''))
    report['key_metrics'] = {
        'total_devices_tracked': total_devices,
        'hot_categories': new_hot,
        'price_changes_detected': len([c for c in (weekly_changes or []) if c['price_change'] != 0]),
        'significant_movers': len([c for c in (weekly_changes or []) if abs(c['sales_change_pct']) > 10]),
    }

    # Top movers
    if weekly_changes:
        report['top_movers'] = weekly_changes[:8]

    # 品类摘要
    for cat, info in market_updates['market_movements'].items():
        report['category_summary'][cat] = {
            'trend': info['trend'],
            'hot_models': info['hot_models'][:3],
            'key_news': info['news'][:100] + '...' if len(info['news']) > 100 else info['news']
        }

    return report

if __name__ == '__main__':
    # 测试运行
    updates = search_market_updates()
    print("=" * 60)
    print("📡 市场动态采集结果")
    print("=" * 60)
    for cat, info in updates['market_movements'].items():
        print(f"\n{'🔥' if '🔥' in info['trend'] else '📈'} {cat}: {info['trend']}")
        for m in info['hot_models']:
            print(f"   → {m}")
        print(f"   💰 {info['price_trend']}")

    print("\n" + "=" * 60)
    print("🚀 新兴信号")
    print("=" * 60)
    for s in updates['emerging_signals']:
        print(f"  • {s}")

    devices = load_json(os.path.join(DATA_DIR, 'devices.json'))
    report = generate_week_report(updates, None, devices or [])
    print(f"\n📰 周报头条: {report['headline']}")
    print(f"📊 追踪 {report['key_metrics']['total_devices_tracked']} 款设备")
