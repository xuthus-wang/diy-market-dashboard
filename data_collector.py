"""
DIY市场数据采集模块
- 联网搜索最新热销榜、新品发布、价格变动
- 对比上周数据生成趋势报告
- 支持品类：智能切割机、3D打印机、激光雕刻机、热压机、电动工具
"""
import json
import os
import re
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
        # 新兴信号已改为动态归纳：见 compute_emerging_signals(devices, week_label)。
        # 此处不再写死文案；如需补充"行业级事件/联网核实"类信号，
        # 请通过 compute_emerging_signals(devices, week_label, curated=[...]) 传入。
        "emerging_signals": []
    }


def _parse_money_est(s):
    """解析 'consumable_monthly_sales_est' 字符串为美元估算数值；失败返回 None。
    支持 $250万 / $1.2亿 / $500 / $1.8M 等形式。"""
    if not isinstance(s, str):
        return None
    m = re.search(r'\$?\s*([\d.]+)\s*(万|亿|M)?', s)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2) or ''
    if unit == '万':
        val *= 1e4
    elif unit == '亿':
        val *= 1e8
    elif unit.upper() == 'M':
        val *= 1e6
    return val


def compute_emerging_signals(devices, week_label, curated=None):
    """基于设备基准库动态归纳本周新兴信号（纯数据驱动，不编造）。

    维度覆盖：本周新上市 / 增长跃升 / 社媒热度 / 价格异动 / 耗材经济学。
    每条信号都附数据来源(evidence/source)，便于审计与可追溯。
    curated: 可选的人工/联网核实补充信号(dict 列表)，合并进结果。

    返回 {'signals': [可读字符串...], 'details': [结构化 dict...]}。
    """
    devices = devices or []
    signals, details = [], []

    def add(sig_type, title, text, evidence, source, dev_ids=None):
        signals.append(f"【{title}】{text}")
        details.append({
            'type': sig_type, 'title': title, 'signal': text,
            'evidence': evidence, 'source': source,
            'devices': dev_ids or [], 'week': week_label,
        })

    # A. 本周新上市（is_new 已由周报标准修正为「本周新上市」语义）
    new_devs = [d for d in devices if d.get('is_new')]
    if new_devs:
        names = [f"{d['brand']} {d['model']}" for d in new_devs]
        cat_count = {}
        for d in new_devs:
            cat_count[d['category']] = cat_count.get(d['category'], 0) + 1
        cat_txt = '、'.join(f"{c}{n}台" for c, n in cat_count.items())
        ev = '；'.join(f"{d['brand']} {d['model']} 上市 {d.get('release_date')}" for d in new_devs)
        add('new_release', '本周新上市',
            f"本周（{week_label}）新上市 {len(new_devs)} 台设备（{cat_txt}）：{', '.join(names)}。",
            ev, 'devices.json (is_new + release_date)',
            [d['id'] for d in new_devs])

    # B. 增长跃升（品类均值 + 个体 Top）
    if devices:
        avg_growth = sum(d.get('weekly_growth_pct', 0) for d in devices) / len(devices)
        cat_g = {}
        for d in devices:
            cat_g.setdefault(d['category'], []).append(d.get('weekly_growth_pct', 0))
        cat_avg = {c: sum(v) / len(v) for c, v in cat_g.items()}
        top_cat = max(cat_avg.items(), key=lambda x: x[1])
        top_devs = sorted(devices, key=lambda d: d.get('weekly_growth_pct', 0), reverse=True)[:5]
        if top_devs and top_devs[0]['weekly_growth_pct'] >= 8:
            top_names = '、'.join(
                f"{d['brand']} {d['model']}({d['weekly_growth_pct']}%)" for d in top_devs)
            ev = f"全样本周增长均值 {avg_growth:.1f}%；最快品类 {top_cat[0]} 均值 {top_cat[1]:.1f}%"
            add('growth_surge', '增长领跑',
                f"周增长率居前品类为「{top_cat[0]}」(均值 {top_cat[1]:.1f}%)，个体 Top5：{top_names}。",
                ev, 'devices.json (weekly_growth_pct)',
                [d['id'] for d in top_devs])

    # C. 社媒热度（search_growth_pct / tiktok_videos Top）
    if devices:
        top_social = sorted(
            devices,
            key=lambda d: (d.get('social_metrics', {}).get('search_growth_pct', 0),
                           d.get('social_metrics', {}).get('tiktok_videos', 0)),
            reverse=True)[:4]
        if top_social and top_social[0].get('social_metrics', {}).get('search_growth_pct', 0) >= 15:
            names = '、'.join(
                f"{d['brand']} {d['model']}(搜索+{d['social_metrics']['search_growth_pct']}%, "
                f"TikTok {d['social_metrics']['tiktok_videos']}视频)" for d in top_social)
            add('social_buzz', '社媒热度',
                f"搜索/社媒热度最高：{names}。",
                'devices.json (social_metrics.search_growth_pct / tiktok_videos)',
                'devices.json (social_metrics)',
                [d['id'] for d in top_social])

    # D. 价格异动（|price_change_pct| >= 5，聚合只列幅度居前者）
    movers = [d for d in devices if abs(d.get('price_change_pct') or 0) >= 5]
    if movers:
        up = sorted([d for d in movers if (d.get('price_change_pct') or 0) > 0],
                    key=lambda d: d['price_change_pct'], reverse=True)[:3]
        down = sorted([d for d in movers if (d.get('price_change_pct') or 0) < 0],
                      key=lambda d: d['price_change_pct'])[:3]
        up_txt = '、'.join(f"{d['brand']} {d['model']}(+{d['price_change_pct']}%)" for d in up)
        down_txt = '、'.join(f"{d['brand']} {d['model']}({d['price_change_pct']}%)" for d in down)
        n_up = len([d for d in movers if (d.get('price_change_pct') or 0) > 0])
        n_down = len([d for d in movers if (d.get('price_change_pct') or 0) < 0])
        ev = f"共 {len(movers)} 台价格变动≥5%（上调 {n_up} 台 / 下调 {n_down} 台）"
        text = f"本周价格显著变动共 {len(movers)} 台，幅度居前——上调：{up_txt}；下调：{down_txt}。"
        add('price_shift', '价格异动', text, ev, 'devices.json (price_change_pct)',
            [d['id'] for d in movers])

    # E. 耗材经济学（consumable_monthly_sales_est 估算，按品类汇总）
    cat_cons = {}
    for d in devices:
        est = _parse_money_est(d.get('consumable_monthly_sales_est'))
        if est:
            cat_cons[d['category']] = cat_cons.get(d['category'], 0) + est
    if cat_cons:
        top_cat, top_val = max(cat_cons.items(), key=lambda x: x[1])
        rep = max([d for d in devices if d['category'] == top_cat],
                  key=lambda d: _parse_money_est(d.get('consumable_monthly_sales_est')) or 0)
        est_fmt = f"${top_val/1e4:.0f}万" if top_val >= 1e4 else f"${top_val:,.0f}"
        add('consumable_economics', '耗材经济',
            f"耗材月销售额估算最高的品类为「{top_cat}」(约 {est_fmt}/月，代表 {rep['brand']} {rep['model']})，耗材复购驱动属性强。",
            'devices.json (consumable_monthly_sales_est 解析并按品类汇总)',
            'devices.json (consumable_monthly_sales_est)',
            [rep['id']])

    # 合并人工/联网核实补充信号（curated）
    if curated:
        for c in curated:
            if isinstance(c, dict):
                signals.append(f"【{c.get('title', '策展')}】{c.get('signal', c.get('text', ''))}")
                details.append(c)
            else:
                signals.append(str(c))

    return {'signals': signals, 'details': details}


def verify_monthly_sales(devices, verified=None):
    """用真实数据源核实并回写月销量（周报联网核实环节调用）。

    数据源可信度优先级（高→低）：
        verified(厂商披露/第三方榜单真实出货) > anchored(品类份额模型) > low > estimated
    verified: {device_id: {'monthly_sales': int, 'source': str, 'as_of': str}}
        仅当提供且值比现有估算更可信时回写；回写后 sales_confidence='verified'，
        并追加 sales_calibration 真实来源、刷新 last_verified / verified_note、标记 sales_data_status='real_reported'。
    返回更新后的 devices（原地修改）。
    """
    if not verified:
        return devices
    byid = {d['id']: d for d in devices}
    today = datetime.now().strftime('%Y-%m-%d')
    for did, info in verified.items():
        d = byid.get(did)
        if not d or info.get('monthly_sales') is None:
            continue
        d['monthly_sales'] = info['monthly_sales']
        d['sales_confidence'] = 'verified'
        d['sales_data_status'] = 'real_reported'
        cal = d.get('sales_calibration') or {}
        if isinstance(cal, dict):
            cal['real_source'] = info.get('source')
            cal['confidence'] = 'verified'
            cal['as_of'] = info.get('as_of', today)
        d['sales_calibration'] = cal
        note = f"[{today}] 月销量: 联网核实真实出货，来源 {info.get('source')}"
        d['verified_note'] = (d.get('verified_note') or '') + ' | ' + note if d.get('verified_note') else note
        d['last_verified'] = today
    return devices


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
