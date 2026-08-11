import sys, time, json, re, os
sys.path.insert(0, '/Users/Zhuanz/Downloads/xhs_scraper')
from core import launch, run_js, close_win, osa

raw = open('/tmp/boards_raw.json', encoding='utf-8').read()
ids = sorted(set(re.findall(r'[a-f0-9]{24}', raw)))

def resolve(bid):
    url = "https://www.xiaohongshu.com/board/%s" % bid
    win = launch(url)
    time.sleep(6)
    for _ in range(8):
        try:
            r = run_js(win, 'board_title.js', 25)
            d = json.loads(r)
            if d.get('name') and d['name'] != '(无标题)':
                close_win(win)
                return d
        except Exception as e:
            pass
        time.sleep(1.5)
    try:
        r = run_js(win, 'board_title.js', 25)
        d = json.loads(r)
    except Exception:
        d = {'name': None, 'count': None}
    close_win(win)
    return d

out = {}
for bid in ids:
    d = resolve(bid)
    out[bid] = d
    print("%s  ->  %s  (笔记%s)" % (bid, d.get('name'), d.get('count')))
json.dump(out, open('/tmp/boards_resolved.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print("=== saved /tmp/boards_resolved.json ===")
