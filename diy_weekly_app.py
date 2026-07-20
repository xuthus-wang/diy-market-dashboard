"""
DIY市场周报系统 — Flask 后端 API (v2 — 集成数据采集)
"""
import json
import os
import sys
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template, send_file
from prediction_engine import PredictionEngine
from data_collector import search_market_updates, compute_weekly_changes, generate_week_report

app = Flask(__name__)
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weekly_data')

def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def save_json(filename, data):
    path = os.path.join(DATA_DIR, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_week_label():
    now = datetime.now()
    year = now.year
    week = now.isocalendar()[1]
    return f"{year}-W{week:02d}"

def generate_week_data():
    """
    生成本周数据 — 结合设备基准库 + 市场动态采集 + 上周对比
    """
    devices = load_json('devices.json') or []
    week_label = get_week_label()

    # 1. 获取市场动态情报
    market_updates = search_market_updates()

    # 查找上一个周报用于对比（优先找最近的非本周历史）
    history_dir = os.path.join(DATA_DIR, 'history')
    previous_week = None
    if os.path.exists(history_dir):
        past_files = sorted([f for f in os.listdir(history_dir) if not f.endswith('_report.json')], reverse=True)
        # 跳过当前周标签
        for pf in past_files:
            if pf.replace('.json', '') != week_label:
                prev_data = load_json(f'history/{pf}')
                if prev_data:
                    previous_week = prev_data
                    break

    # 2. 构建当周设备快照（基于基准 + 市场动态微调）
    week_devices = []
    total_monthly_sales = 0
    categories = {}

    for d in devices:
        cat = d['category']
        if cat not in categories:
            categories[cat] = {'count': 0, 'sales': 0, 'growth': 0, 'hot_models': []}

        device_week = dict(d)
        device_week['price_change_this_week'] = 0
        device_week['current_price'] = d['price_usd']
        device_week['sales_change_this_week'] = 0
        device_week['current_weekly_growth'] = d.get('weekly_growth_pct', 0)

        # 从市场情报注入真实变化（而非随机模拟）
        cat_info = market_updates['market_movements'].get(cat, {})
        if cat_info:
            price_trend = cat_info.get('price_trend', '')
            hot_models = cat_info.get('hot_models', [])

            # 价格变动
            if d.get('is_new'):
                device_week['price_change_this_week'] = 0  # 新品价格稳定
            elif '降价' in price_trend and d['brand'] in price_trend:
                # 有降价趋势的品牌
                device_week['price_change_this_week'] = -10
                device_week['current_price'] = int(d['price_usd'] * 0.9)
            elif '促销' in price_trend and d['brand'] in price_trend:
                device_week['price_change_this_week'] = -5
                device_week['current_price'] = int(d['price_usd'] * 0.95)

            # 销量增长（根据是否在 hot_models 中）
            is_hot = any(d['brand'] in m and d['model'] in m for m in hot_models)
            if is_hot:
                device_week['sales_change_this_week'] = round(
                    d.get('weekly_growth_pct', 5) * 1.5, 1
                )
                device_week['current_weekly_growth'] = round(
                    d.get('weekly_growth_pct', 5) * 1.5, 1
                )
                categories[cat]['hot_models'].append(f"{d['brand']} {d['model']}")

        # 与上周对比
        if previous_week:
            prev_devices = {p['id']: p for p in previous_week.get('devices', [])}
            prev = prev_devices.get(d['id'])
            if prev:
                device_week['previous_price'] = prev.get('current_price', d['price_usd'])
                device_week['previous_sales'] = prev.get('monthly_sales', d.get('monthly_sales', 0))

        week_devices.append(device_week)
        categories[cat]['count'] += 1
        categories[cat]['sales'] += d.get('monthly_sales', 0)
        categories[cat]['growth'] += device_week['current_weekly_growth']
        total_monthly_sales += d.get('monthly_sales', 0)

    # 计算品类平均增长
    for cat in categories:
        if categories[cat]['count'] > 0:
            categories[cat]['growth'] = round(categories[cat]['growth'] / categories[cat]['count'], 1)

    # 找最热品类
    hottest_cat = max(categories.items(), key=lambda x: x[1]['growth'])

    # 计算价格变动数
    price_changes = sum(1 for d in week_devices if d['price_change_this_week'] != 0)

    week_data = {
        'week_label': week_label,
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_devices': len(devices),
            'new_devices': sum(1 for d in devices if d.get('is_new')),
            'price_changes': price_changes,
            'hottest_category': hottest_cat[0],
            'hottest_growth': hottest_cat[1]['growth'],
            'total_monthly_sales_est': total_monthly_sales,
            'categories': len(categories),
        },
        'devices': week_devices,
        'category_breakdown': categories,
        'market_updates': {
            cat: {'trend': info['trend'], 'news': info['news'][:120]}
            for cat, info in market_updates['market_movements'].items()
        },
        'emerging_signals': market_updates['emerging_signals'],
    }

    # 计算真实周环比变化
    weekly_changes = compute_weekly_changes(week_devices, previous_week)
    week_data['weekly_changes'] = weekly_changes

    # 保存
    save_json('current_week.json', week_data)
    save_json(f'history/{week_label}.json', week_data)

    # 生成周报摘要
    report = generate_week_report(market_updates, weekly_changes, devices)
    save_json(f'history/{week_label}_report.json', report)

    return week_data

# ===== 自动刷新调度器（实现"实时更新"）=====
def _refresh_pipeline():
    """重算本周数据 + 爆款预测 + 静态快照，返回周标签"""
    week_data = generate_week_data()
    engine = PredictionEngine(os.path.join(DATA_DIR, 'devices.json'))
    engine.save_predictions(os.path.join(DATA_DIR, 'predictions.json'))
    try:
        import subprocess
        subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_static.py')],
                       timeout=120, capture_output=True)
    except Exception as e:
        print(f"[scheduler] 静态快照重建跳过: {e}")
    return week_data['week_label']

def _scheduler_loop(interval_seconds):
    while True:
        time.sleep(interval_seconds)
        try:
            wl = _refresh_pipeline()
            print(f"[scheduler] 数据已自动刷新至 {wl} @ {datetime.now().isoformat()}")
        except Exception as e:
            print(f"[scheduler] 自动刷新失败: {e}")

def start_scheduler(interval_hours=6):
    """启动后台守护线程，定时重算数据/预测/快照"""
    t = threading.Thread(target=_scheduler_loop, args=(interval_hours * 3600,), daemon=True)
    t.start()
    print(f"⏰ 自动刷新调度器已启动（每 {interval_hours} 小时）")
    return t

# ===== API Routes =====

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/static-dashboard')
def static_dashboard():
    """无需服务器实时数据的静态快照版（后台进程被回收也能看）"""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dashboard_static.html')
    if os.path.exists(path):
        return send_file(path)
    return '静态仪表盘尚未生成，请运行 python3.11 build_static.py', 404

@app.route('/api/summary')
def api_summary():
    week_data = load_json('current_week.json')
    if not week_data:
        week_data = generate_week_data()
    return jsonify(week_data['summary'])

@app.route('/api/devices')
def api_devices():
    category = request.args.get('category', '')
    sort = request.args.get('sort', 'monthly_sales')
    order = request.args.get('order', 'desc')

    week_data = load_json('current_week.json')
    if not week_data:
        week_data = generate_week_data()

    devices = week_data['devices']
    if category:
        devices = [d for d in devices if d['category'] == category]

    reverse = order == 'desc'
    devices.sort(key=lambda x: x.get(sort, 0), reverse=reverse)

    return jsonify(devices)

@app.route('/api/trends')
def api_trends():
    """获取历史趋势数据 + 本周市场动态"""
    history_dir = os.path.join(DATA_DIR, 'history')
    trends = []

    if os.path.exists(history_dir):
        files = sorted([f for f in os.listdir(history_dir) if not f.endswith('_report.json')])
        for f in files[-8:]:
            data = load_json(f'history/{f}')
            if data:
                trends.append({
                    'week': data['week_label'],
                    'summary': data['summary'],
                    'categories': data.get('category_breakdown', {}),
                    'changes': data.get('weekly_changes', [])[:5],
                })

    return jsonify(trends)

@app.route('/api/market_updates')
def api_market_updates():
    """获取本周市场动态情报"""
    week_data = load_json('current_week.json')
    if not week_data:
        week_data = generate_week_data()
    return jsonify({
        'categories': week_data.get('market_updates', {}),
        'emerging_signals': week_data.get('emerging_signals', []),
        'weekly_changes': week_data.get('weekly_changes', [])[:10],
    })

@app.route('/api/predictions')
def api_predictions():
    preds = load_json('predictions.json')
    if not preds:
        engine = PredictionEngine(os.path.join(DATA_DIR, 'devices.json'))
        preds = engine.save_predictions(os.path.join(DATA_DIR, 'predictions.json'))

    top_n = request.args.get('top', 10, type=int)
    return jsonify({
        'generated_at': preds.get('generated_at', ''),
        'predictions': preds.get('top_10', [])[:top_n],
        'all': preds.get('all', [])
    })

@app.route('/api/refresh', methods=['POST'])
def api_refresh():
    """触发数据更新 — 联网采集 + 趋势分析 + 爆款预测"""
    try:
        week_data = generate_week_data()
        engine = PredictionEngine(os.path.join(DATA_DIR, 'devices.json'))
        engine.save_predictions(os.path.join(DATA_DIR, 'predictions.json'))
        return jsonify({
            'success': True,
            'message': f'✅ 数据已更新至 {week_data["week_label"]} — 追踪{week_data["summary"]["total_devices"]}款设备，{week_data["summary"]["categories"]}个品类',
            'week_label': week_data['week_label'],
            'summary': week_data['summary'],
            'top_changes': week_data.get('weekly_changes', [])[:5],
            'emerging_signals': week_data.get('emerging_signals', [])[:3],
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/history')
def api_history():
    history_dir = os.path.join(DATA_DIR, 'history')
    weeks = []
    reports = []
    if os.path.exists(history_dir):
        for f in sorted(os.listdir(history_dir), reverse=True):
            if f.endswith('_report.json'):
                reports.append(f.replace('_report.json', ''))
            elif not f.endswith('_report.json'):
                weeks.append(f.replace('.json', ''))

    return jsonify({
        'weeks': weeks,
        'reports': reports,
        'count': len(weeks)
    })

@app.route('/api/categories')
def api_categories():
    week_data = load_json('current_week.json')
    if not week_data:
        week_data = generate_week_data()
    return jsonify(week_data.get('category_breakdown', {}))

@app.route('/api/weekly_report')
def api_weekly_report():
    """获取最新周报摘要"""
    week_label = get_week_label()
    report = load_json(f'history/{week_label}_report.json')
    if not report:
        generate_week_data()
        report = load_json(f'history/{week_label}_report.json')
    return jsonify(report or {})

if __name__ == '__main__':
    if not load_json('current_week.json'):
        generate_week_data()
    if not load_json('predictions.json'):
        engine = PredictionEngine(os.path.join(DATA_DIR, 'devices.json'))
        engine.save_predictions(os.path.join(DATA_DIR, 'predictions.json'))
    start_scheduler(interval_hours=6)
    print("🚀 DIY市场周报系统 v3 启动中 (http://0.0.0.0:8080)...")
    app.run(host='0.0.0.0', port=8080, debug=False)
