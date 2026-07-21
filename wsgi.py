"""Gunicorn 入口：启动 Flask 应用并拉起自动刷新调度器（含数据刷新 / 推送）"""
from diy_weekly_app import app, start_scheduler

start_scheduler(interval_hours=6)
