# DIY 市场周报系统 · 设备销售追踪仪表盘

追踪 DIY 市场 8 大品类、52 款热门设备的**型号、价格、功能描述、销量、耗材类型、耗材销量**，并提供趋势分析与爆款预测。

- 🔥 最热品类：**UV 打印机**（周增 +108%）
- 🏆 爆款预测榜首：**eufyMake E1 UV Printer**（评分 92.6，2026-08-10）
- ✓ 全部 52 台设备每周**联网核实**四维数据并标注核实日期

## 本地运行

```bash
pip install flask
python3 diy_weekly_app.py          # 启动 API + 仪表盘 (http://localhost:8080)
bash start_server.sh &             # 带自愈的启动方式
python3 build_static.py            # 生成无需服务器的静态仪表盘 dashboard_static.html
```

- 实时版：`http://localhost:8080/`（依赖 Flask 服务，可点"🔄 更新数据"刷新）
- 离线版：`dashboard_static.html`（内嵌全部数据，双击即开）

## 每周自动更新流程（定时任务）

每周一 08:00 执行。**第一步必须是引导脚本** —— 沙箱被重置后 `/workspace` 会全空，
缺少基线数据时流程无法比对，强行执行只会产出编造数据：

```bash
bash /workspace/bootstrap.sh || exit 1   # ← 前置：工作区自愈，失败即终止
cd /workspace
# …… 四维核实（价格 / 月销量 / 周增长率 / 耗材）→ 写回 devices.json
rm -f weekly_data/current_week.json weekly_data/predictions.json
python3.11 build_static.py
git add -A && git commit -m "周报自动更新 $(date +%F)"
git push origin main || git format-patch -1 HEAD --stdout > weekly_update_$(date +%F).patch
```

`bootstrap.sh` 的行为：

| 工作区状态 | 动作 |
|---|---|
| 健康（devices.json 可解析且 ≥40 台） | 跳过恢复，仅校正 remote |
| 为空 / 文件缺失 / JSON 损坏 | 从远端重新拉取；覆盖前自动备份到 `/tmp/ws_backup_<时间戳>` |
| 所有通路不可用 | 退出码 1，**终止流程** |

`bash bootstrap.sh --force` 强制重新拉取（丢弃本地未提交改动）。

### ⚠ 网络约束：走 ghproxy 镜像

沙箱到 `github.com` 的直连被网关 TLS 阻断（`git clone`、`api.github.com`、
`raw.githubusercontent.com` 握手均失败），因此：

- **fetch / clone** 走镜像 `https://ghproxy.net/https://github.com/…`，脚本内置
  `gh-proxy.com` → 直连 → tarball 快照（含 jsdelivr）多级回退
- **push** 的 URL 单独指回 `github.com` 原址。镜像仅支持匿名只读；若 push 也指向
  镜像，认证失败时会报出误导性的 `could not read Username for 'https://ghproxy.net'`
- push 需要有效的 GitHub 凭据。连接器未授权时流程降级为导出 `.patch`，
  可在本地 `git am` 应用

## 数据更新

1. 编辑 `weekly_data/devices.json`（设备基准库）
2. 如需刷新市场情报，更新 `data_collector.py` 的市场快照
3. 运行 `python3 build_static.py` 重建静态仪表盘

本仓库通过 GitHub Actions 自动部署到 GitHub Pages（见 `.github/workflows/deploy.yml`）。
