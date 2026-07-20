# DIY 市场周报系统 · 设备销售追踪仪表盘

追踪 DIY 市场 8 大品类、38+ 款热门设备的**型号、价格、功能描述、销量、耗材类型、耗材销量**，并提供趋势分析与爆款预测。

- 🔥 最热品类：**UV 打印机**（周增 +108%）
- 🏆 爆款预测榜首：**eufyMake E1 UV Printer**（评分 94.6）
- ✓ 关键设备价格/销量已**联网核实**并标注核实日期

## 本地运行

```bash
pip install flask
python3 diy_weekly_app.py          # 启动 API + 仪表盘 (http://localhost:8080)
bash start_server.sh &             # 带自愈的启动方式
python3 build_static.py            # 生成无需服务器的静态仪表盘 dashboard_static.html
```

- 实时版：`http://localhost:8080/`（依赖 Flask 服务，可点"🔄 更新数据"刷新）
- 离线版：`dashboard_static.html`（内嵌全部数据，双击即开）

## 数据更新

1. 编辑 `weekly_data/devices.json`（设备基准库）
2. 如需刷新市场情报，更新 `data_collector.py` 的市场快照
3. 运行 `python3 build_static.py` 重建静态仪表盘

本仓库通过 GitHub Actions 自动部署到 GitHub Pages（见 `.github/workflows/deploy.yml`）。
