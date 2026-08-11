#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从本机真实 Chrome 提取小红书(xiaohongshu.com)的 Cookie，供 Spider_XHS 注入。

使用 browser_cookie3（维护良好，支持现代 Chrome 的 AES-GCM/v20 加密方案），
避免手写解密因 IV 方案不同而产生控制字符污染。
输出：本脚本同目录下的 .env.cookies（XHS_COOKIE=...），与 load_cookie() 读取位置一致。
"""
import os
import browser_cookie3 as bc

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(SCRIPTS, ".env.cookies")


def main():
    try:
        cj = bc.chrome(domain_name="xiaohongshu.com")
    except Exception as e:
        raise SystemExit("读取 Chrome cookie 失败: %r" % e)
    d = {c.name: c.value for c in cj}
    if not d:
        raise SystemExit("未在 Chrome 找到 xiaohongshu.com 的 cookie（请先登录小红书网页版）")
    header = "; ".join("%s=%s" % (k, v) for k, v in d.items())
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("# XHS cookies extracted from local Chrome via browser_cookie3\n")
        f.write("XHS_COOKIE=%s\n" % header)
    print("XHS_COOKIE_COUNT:", len(d))
    print("HAS_web_session:", "web_session" in d)
    print("HAS_a1:", "a1" in d)
    print("HAS_webId:", "webId" in d)
    print("SAVED:", OUT, "(len=%d)" % len(header))


if __name__ == "__main__":
    main()
