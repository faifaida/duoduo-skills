#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""定向补抓被限流的专辑（降速+退避），只处理指定几本，不动已完成的。"""
import sys, os, json, datetime
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
import sync

# 补抓这几本（缺口最大的排后面，先抓小的热身，主动降压）
TARGETS = ["关系恋爱", "职业", "养生大法", "审美"]

def main():
    os.environ['XHS_COLLECTED_DATE'] = datetime.date.today().isoformat()
    boards = {n: bid for bid, n in sync.load_boards()}
    total = 0
    for name in TARGETS:
        bid = boards.get(name)
        if not bid:
            print("!! 找不到专辑 %s 的 board id，跳过" % name); continue
        url = "https://www.xiaohongshu.com/board/%s" % bid
        print("\n########## 补抓 %s ##########" % name)
        try:
            total += sync.sync_one(url, name)
        except Exception as e:
            print("!! %s 失败: %s" % (name, e))
    print("\n=== 补抓完成，本次新增 %d 篇 ===" % total)

if __name__ == "__main__":
    main()
