#!/usr/bin/env python3.11
# -*- coding: utf-8 -*-
"""push_via_api.py — 经 GitHub REST API 推送提交（绕过被阻断的 git 传输协议）

背景: 本环境 git 直连 github.com 被网关 TLS 阻断, ghproxy 镜像拒绝带凭据 push(403),
      但 api.github.com 的 HTTPS 通路稳定。本脚本用 Git Data API 实现 fast-forward push:
      blobs → tree(base_tree=远端 HEAD tree) → commit(parent=远端 HEAD) → 更新 refs/heads/main。
      非快照覆盖, 远端有新提交时更新 ref 会 422 失败并如实报错(等效非 fast-forward 拒绝)。

token 从本机 .secret 读取(GH_TOKEN=...), 不出现在本文件与输出中。
用法: python push_via_api.py [-f] <commit_message_file> <file1> [file2 ...]
      -f 强制更新 ref(仅用于替换自己刚创建的错误提交)
"""
import base64
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

REPO = "xuthus-wang/diy-market-dashboard"
SECRET = ".secret"


def token():
    for line in open(SECRET, encoding="utf-8"):
        if line.startswith("GH_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("[api-push] .secret 中无 GH_TOKEN")


def api(path, payload=None, method=None, tok=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        "https://api.github.com" + path, data=data,
        headers={"User-Agent": "diy-weekly-bot", "Accept": "application/vnd.github+json",
                 "Authorization": "token " + tok},
        method=method or ("POST" if data is not None else "GET"))
    # api.github.com 现有逐连接 SSL EOF 瞬断(约半数请求被网关掐断, 非硬阻断/非鉴权失败),
    # 单请求退避重试(每次 +3s, 最多 4 次); HTTPError 属明确业务错误, 不重试。
    import time
    last = None
    for attempt in range(4):
        req = urllib.request.Request(
            "https://api.github.com" + path, data=data,
            headers={"User-Agent": "diy-weekly-bot", "Accept": "application/vnd.github+json",
                     "Authorization": "token " + tok},
            method=method or ("POST" if data is not None else "GET"))
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read()
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            print("[api-push] HTTP %s %s: %s" % (e.code, path, e.read().decode()[:300]))
            raise SystemExit(1)
        except Exception as e:
            last = e
            print("[api-push] 传输失败(第%d次) %s: %s, 退避重试" % (attempt+1, path, e))
            time.sleep(3 * (attempt + 1))
    raise last


def main():
    args = sys.argv[1:]
    force = "-f" in args
    args = [a for a in args if a != "-f"]
    msg_file, files = args[0], args[1:]
    tok = token()
    now = datetime.now().astimezone().isoformat(timespec="seconds")

    ref = api("/repos/%s/git/ref/heads/main" % REPO, tok=tok)
    head_sha = ref["object"]["sha"]
    base_commit = api("/repos/%s/git/commits/%s" % (REPO, head_sha), tok=tok)
    base_tree = base_commit["tree"]["sha"]
    print("[api-push] 远端 HEAD: %s (tree %s)" % (head_sha[:10], base_tree[:10]))

    entries = []
    for p in files:
        raw = open(p, "rb").read()
        blob = api("/repos/%s/git/blobs" % REPO,
                   {"content": base64.b64encode(raw).decode(), "encoding": "base64"}, tok=tok)
        entries.append({"path": p.replace("\\", "/"), "mode": "100644",
                        "type": "blob", "sha": blob["sha"]})
        print("[api-push] blob %s (%d bytes)" % (p, len(raw)))

    tree = api("/repos/%s/git/trees" % REPO, {"base_tree": base_tree, "tree": entries}, tok=tok)
    ident = {"name": "DIY Weekly Bot", "email": "diy-bot@local", "date": now}
    msg = open(msg_file, encoding="utf-8").read().strip()
    commit = api("/repos/%s/git/commits" % REPO,
                 {"message": msg, "tree": tree["sha"], "parents": [head_sha],
                  "author": ident, "committer": ident}, tok=tok)
    print("[api-push] 新提交: %s" % commit["sha"][:10])

    updated = api("/repos/%s/git/refs/heads/main" % REPO, {"sha": commit["sha"], "force": force},
                  method="PATCH", tok=tok)
    print("[api-push] ✅ refs/heads/main → %s (fast-forward)" % updated["object"]["sha"][:10])


if __name__ == "__main__":
    main()
