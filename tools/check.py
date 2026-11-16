#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TVBox 多仓探活脚本（纯标准库，无需第三方依赖）。

用法:
    python tools/check.py                 # 探活并原地更新 tvbox.json / tvbox-lite.json / tvbox-mini.json
    python tools/check.py --dry-run       # 只打印结果，不改文件

判定规则:
    HTTP 200 且响应体包含 "sites" / "urls" / "spider" 之一 => 存活
    其余（404 / 5xx / 返回 HTML / 超时 / 连接失败）      => 判死，从多仓里剔除
"""

import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULL = os.path.join(ROOT, "tvbox.json")
LITE = os.path.join(ROOT, "tvbox-lite.json")
MINI = os.path.join(ROOT, "tvbox-mini.json")
STATUS = os.path.join(ROOT, "STATUS.md")

UA = "okhttp/3.15"
TIMEOUT = 12
WORKERS = 16
CN = timezone(timedelta(hours=8))

# 国内可达性判断：这些前缀视为国内友好，用于生成 lite / mini
SLOW_PREFIX = ("https://raw.githubusercontent.com", "https://pastebin.com")


def probe(entry):
    url = entry.get("url", "")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
            body = r.read(512 * 1024).decode("utf-8", "ignore")
            ok = ('"sites"' in body) or ('"urls"' in body) or ('"spider"' in body)
            return dict(entry, ok=ok, size=len(body), code=r.status, note="" if ok else "非配置内容")
    except urllib.error.HTTPError as e:
        return dict(entry, ok=False, size=0, code=e.code, note="HTTP %s" % e.code)
    except Exception as e:  # noqa: BLE001
        return dict(entry, ok=False, size=0, code="ERR", note=type(e).__name__)


def load(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return data.get("urls") or data.get("stores") or []


def save(path, entries):
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"urls": entries}, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    dry = "--dry-run" in sys.argv
    entries = load(FULL)
    print("probing %d entries ..." % len(entries))

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        results = list(pool.map(probe, entries))

    alive = [r for r in results if r["ok"]]
    dead = [r for r in results if not r["ok"]]
    print("alive %d / %d" % (len(alive), len(results)))

    # 保留 ok/size/name/url，丢掉临时字段
    clean = [{"name": r["name"], "url": r["url"]} for r in alive]
    domestic = [c for c in clean if not c["url"].startswith(SLOW_PREFIX)]

    if not dry:
        save(FULL, clean)
        save(LITE, domestic[:16])
        save(MINI, domestic[:8])

        lines = [
            "# 探活结果",
            "",
            "最近更新：%s (UTC+8)" % datetime.now(CN).strftime("%Y-%m-%d %H:%M"),
            "",
            "存活 **%d** / %d" % (len(alive), len(results)),
            "",
            "## 存活",
            "",
            "| 单仓 | 大小 | 地址 |",
            "|---|---|---|",
        ]
        for r in sorted(alive, key=lambda x: -x["size"]):
            lines.append("| %s | %.0f KB | `%s` |" % (r["name"], r["size"] / 1024.0, r["url"]))
        lines += ["", "## 已失效（已从多仓剔除）", "", "| 单仓 | 原因 | 地址 |", "|---|---|---|"]
        for r in dead:
            lines.append("| %s | %s | `%s` |" % (r["name"], r["note"] or r["code"], r["url"]))
        lines.append("")
        with open(STATUS, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print("written: tvbox.json / tvbox-lite.json / tvbox-mini.json / STATUS.md")

    return 0 if alive else 1


if __name__ == "__main__":
    sys.exit(main())
