"""
轻量用户 / 付费鉴权模块（演示用）
- 用户存于 weekly_data/users.json（已 gitignore，勿提交）
- 密码使用 werkzeug 哈希
- 预留 Stripe 接口，后续可接真实支付
生产环境建议替换为数据库 + 真实支付网关。
"""
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash

USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'weekly_data', 'users.json')


def _load():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return None


def _save(users):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def seed():
    """首次运行创建示例账号"""
    if _load() is None:
        users = {
            'admin': {'password': generate_password_hash('admin123'), 'paid': True, 'role': 'admin', 'name': '管理员'},
            'demo':  {'password': generate_password_hash('demo123'),  'paid': True, 'role': 'user',  'name': '付费示例用户'},
            'trial': {'password': generate_password_hash('trial123'), 'paid': False, 'role': 'user',  'name': '未付费示例'},
        }
        _save(users)


def authenticate(username, password):
    users = _load() or {}
    u = users.get(username)
    if u and check_password_hash(u['password'], password):
        return u
    return None


def create_user(username, password, paid=False, role='user', name=''):
    users = _load() or {}
    if not username or username in users:
        return False
    users[username] = {'password': generate_password_hash(password), 'paid': bool(paid), 'role': role, 'name': name or username}
    _save(users)
    return True


def set_paid(username, paid):
    users = _load() or {}
    if username in users:
        users[username]['paid'] = bool(paid)
        _save(users)
        return True
    return False


def list_users():
    return _load() or {}


def is_admin(username):
    return (list_users().get(username) or {}).get('role') == 'admin'


# ===== Stripe 预留接口（接入真实支付时实现）=====
# def create_checkout_session(user): ...
# def handle_webhook(payload, sig):
#     # 校验签名后，若支付成功 → set_paid(user, True)
#     ...
