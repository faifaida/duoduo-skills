#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_xhs_login.py — 独立检查小红书登录是否还活着（无需枚举/抓详情）。
用途：
  - 你随时想确认「现在要不要去扫码」时跑一下。
  - 每周自动化可先跑它；返回非 0 就停，不去动死 session（避免加重风控）。
实现：复用 xhs_obsidian_sync 的 load_cookie/load_proxies/check_session。
  - load_proxies 默认直连本机住宅 IP（与 Chrome 登录同 IP，不再走机房代理）。
退出码：0 = 登录有效；2 = 登录失效需扫码；1 = 环境/脚本错误。
"""
import sys, os
SCRIPTS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS)
os.chdir(os.path.join(SCRIPTS, "Spider_XHS"))
os.environ.setdefault("NODE_PATH", os.path.join(SCRIPTS, "Spider_XHS", "node_modules"))

import xhs_obsidian_sync as S

def main():
    try:
        cookie = S.load_cookie()
    except SystemExit as e:
        print("XHS_COOKIE_MISSING: 未找到 cookie，请先运行 extract_xhs_cookies.py")
        return 1
    proxies = S.load_proxies()
    ok, why = S.check_session(cookie, proxies)
    print("XHS_LOGIN_OK:", ok)
    print(why)
    return 0 if ok else 2

if __name__ == "__main__":
    sys.exit(main())
