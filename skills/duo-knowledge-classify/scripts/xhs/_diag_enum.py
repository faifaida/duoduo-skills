#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断枚举步: 打开某 board, 看 Chrome 页面状态 / 登录态 / note-item 数量 / 链接提取。"""
import sys, os, time
SP = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SP)
import xhs_obsidian_sync as S

def diag(board_name, board_id):
    print("=== 诊断 %s ===" % board_name, flush=True)
    S.chrome_open("https://www.xiaohongshu.com/board/%s/" % board_id)
    time.sleep(4)
    cur = S.osa('tell application "Google Chrome" to get URL of active tab of front window')
    print("当前URL:", cur.stdout.strip(), "| err:", cur.stderr.strip(), flush=True)
    login_hint = S.run_js("(function(){var t=document.body?document.body.innerText:'';return (t.indexOf('登录')>=0||t.indexOf('扫码')>=0)?'LOGIN_PAGE':(t.indexOf('小红书')>=0?'has_xhs_text':'unknown');})()", 20)
    print("登录态hint:", login_hint, flush=True)
    cnt = S.run_js("document.querySelectorAll('section.note-item').length", 20)
    print("note-item 数量:", cnt, flush=True)
    links = S.run_js(S.JS_LINKS, 20)
    print("links 原始(前300):", (links or "")[:300], flush=True)
    body = S.run_js("(function(){var t=document.body?document.body.innerText:'';return t.slice(0,150);})()", 20)
    print("body 文本(前150):", (body or "")[:150], flush=True)

for nm, bid in [("职业", "5b11035933e4604d71a59368"), ("养生大法", "5b11753120acbb134527435e")]:
    diag(nm, bid)
