#!/usr/bin/env python3.11
"""
生成静态版仪表盘 dashboard_static.html —— 内嵌全部数据，无需 Flask 服务器即可打开。
解决沙箱后台进程被回收导致「网页打不开」的问题。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(HERE, 'weekly_data')
TEMPLATE = os.path.join(HERE, 'templates', 'dashboard.html')
OUT = os.path.join(HERE, 'dashboard_static.html')


def load_json(name):
    p = os.path.join(DATA_DIR, name)
    if os.path.exists(p):
        with open(p, 'r') as f:
            return json.load(f)
    return None


def build_embedded():
    cw = load_json('current_week.json')
    if not cw:
        sys.path.insert(0, HERE)
        import diy_weekly_app
        cw = diy_weekly_app.generate_week_data()  # 显式生成（CI 全新检出时无 current_week.json）
        if not cw:
            cw = load_json('current_week.json')

    preds = load_json('predictions.json')
    if not preds:
        from prediction_engine import PredictionEngine
        preds = PredictionEngine(os.path.join(DATA_DIR, 'devices.json')).save_predictions(
            os.path.join(DATA_DIR, 'predictions.json'))

    # === 复刻 /api/market_updates ===
    mu = {
        'categories': cw.get('market_updates', {}),
        'emerging_signals': cw.get('emerging_signals', []),
        'weekly_changes': cw.get('weekly_changes', [])[:10],
    }
    # === 复刻 /api/trends ===
    hist_dir = os.path.join(DATA_DIR, 'history')
    trends = []
    if os.path.exists(hist_dir):
        files = sorted([f for f in os.listdir(hist_dir) if not f.endswith('_report.json')])
        for f in files[-8:]:
            d = load_json(f'history/{f}')
            if d:
                trends.append({
                    'week': d['week_label'],
                    'summary': d['summary'],
                    'categories': d.get('category_breakdown', {}),
                    'changes': d.get('weekly_changes', [])[:5],
                })
    # === 复刻 /api/history ===
    weeks, reports = [], []
    if os.path.exists(hist_dir):
        for f in sorted(os.listdir(hist_dir), reverse=True):
            if f.endswith('_report.json'):
                reports.append(f.replace('_report.json', ''))
            else:
                weeks.append(f.replace('.json', ''))

    embedded = {
        'devices': cw.get('devices', []),
        'summary': cw.get('summary', {}),
        'categories': cw.get('category_breakdown', {}),
        'market_updates': mu,
        'trends': trends,
        'predictions': {
            'generated_at': preds.get('generated_at', ''),
            'predictions': preds.get('top_10', []),
            'all': preds.get('all', []),
        },
        'history': {'weeks': weeks, 'reports': reports, 'count': len(weeks)},
    }
    return embedded


def main():
    embedded = build_embedded()
    with open(TEMPLATE, 'r') as f:
        html = f.read()

    data_json = json.dumps(embedded, ensure_ascii=False)
    # 防止数据中出现 </script> 或 </ 破坏 HTML 解析
    data_json = data_json.replace('</', '<\\/')

    marker = '<script>\nvar allDevices='
    inject = '<script>\nwindow.EMBEDDED_DATA = ' + data_json + ';\nvar allDevices='
    if marker in html:
        html = html.replace(marker, inject, 1)
    else:
        # 兜底：插到 </body> 前
        html = html.replace('</body>', '<script>window.EMBEDDED_DATA = ' + data_json + ';</script></body>')

    with open(OUT, 'w') as f:
        f.write(html)
    print(f'✅ 已生成静态仪表盘: {OUT}')
    print(f'   内嵌设备 {len(embedded["devices"])} 台, 预测 {len(embedded["predictions"]["all"])} 条, 历史周 {len(embedded["history"]["weeks"])} 周')
    print(f'   文件大小: {os.path.getsize(OUT)/1024:.0f} KB')


if __name__ == '__main__':
    main()
