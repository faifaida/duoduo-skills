import sys, time, json, re, os, random
sys.path.insert(0, '/Users/Zhuanz/Downloads/xhs_scraper')
from core import launch, run_js, close_win, osa, relaunch_chrome

SC = '/Users/Zhuanz/Downloads/xhs_scraper'

def extract_note_id(url):
    m = re.search(r'/explore/([a-f0-9]{24})', url) or re.search(r'/board/[^/]+/([a-f0-9]{24})', url)
    return m.group(1) if m else url

def to_explore(card_url):
    m = re.search(r'/board/[^/]+/([a-f0-9]{24})', card_url)
    tok = re.search(r'xsec_token=([^&]+)', card_url)
    if m and tok:
        return "https://www.xiaohongshu.com/explore/%s?xsec_token=%s&xsec_source=pc_user" % (m.group(1), tok.group(1))
    return card_url

def collect_links(board_url, name):
    lp = os.path.join(SC, 'links_%s.json' % name)
    if os.path.exists(lp):
        arr = json.load(open(lp))
        print("links cache hit: %d for %s" % (len(arr), name))
        return arr
    win = launch(board_url)
    time.sleep(8)
    for _ in range(20):
        try:
            n = run_js(win, 'collect.js', 30)
            if n and int(n) > 0: break
        except Exception as e:
            print("poll err", e)
        time.sleep(1.5)
    prev = -1
    for i in range(45):
        try: run_js(win, 'scroll_bottom.js', 20)
        except: pass
        time.sleep(1.5)
        try: n = int(run_js(win, 'collect.js', 30))
        except: n = 0
        if n == prev and i > 5: break
        prev = n
    arr = json.loads(run_js(win, 'get_arr.js', 30))
    close_win(win)
    json.dump(arr, open(lp, 'w'))
    print("collected %d links for %s" % (len(arr), name))
    return arr

def scrape_details(name, links, out_json):
    cp = os.path.join(SC, 'done_%s.jsonl' % name)
    done = {}
    if os.path.exists(cp):
        for l in open(cp):
            l = l.strip()
            if not l: continue
            try: d = json.loads(l); done[d.get('noteId')] = 1
            except: pass
    win = None
    total = len(links)
    count = len(done)
    print("resuming %s: %d/%d already done" % (name, count, total))
    pending = [c for c in links if extract_note_id(c) not in done]
    consec_throttle = 0        # 连续限流计数
    MAX_CONSEC = 6             # 连续限流达到此值则本轮优雅中止，留待下次
    since_rest = 0             # 距上次长休息抓了多少篇
    i = 0
    while i < len(pending):
        card = pending[i]
        nid = extract_note_id(card)
        exp = to_explore(card)
        if win is None:
            win = launch(exp); time.sleep(6)
        else:
            try:
                osa('tell application "Google Chrome" to set URL of tab 1 of window id %d to "%s"' % (win, exp), 30)
            except Exception as e:
                print("nav err, new window:", e)
                try: close_win(win)
                except: pass
                try: win = launch(exp); time.sleep(6)
                except Exception:
                    relaunch_chrome(); win = launch(exp); time.sleep(6)
        time.sleep(random.uniform(3.5, 6.0))   # 降速：拉长每篇间隔
        ok = False
        for _ in range(10):
            try:
                if run_js(win, 'has_title.js', 20) == '1':
                    ok = True; break
            except Exception as e:
                print("wait err, relaunch:", e)
                try: close_win(win)
                except: pass
                relaunch_chrome(); win = launch(exp); time.sleep(6)
            time.sleep(1)
        note = {'noteId': nid, 'url': exp, 'valid': False}
        throttled = False
        try:
            p = json.loads(run_js(win, 'probe.js', 30))
            note.update(p)
            throttled = bool(p.get('throttled'))
            note['valid'] = bool(p.get('title') and p.get('title') != '(无标题)' and not p.get('blocked'))
        except Exception as e:
            print("probe err:", e)
        if throttled:
            consec_throttle += 1
            if consec_throttle >= MAX_CONSEC:
                print("[%s] 连续限流 %d 次，本轮中止（剩 %d 篇留待下次重试）"
                      % (name, consec_throttle, len(pending) - i))
                break
            backoff = min(30 * consec_throttle, 180)   # 30s,60s,...最多3分钟退避
            print("[%s] 命中限流(%d/%d)，退避 %ds 后重试同一篇" % (name, i+1, len(pending), backoff))
            time.sleep(backoff)
            continue   # 不写检查点、不前进，重试同一篇
        # 正常抓到（或非限流的空页），写检查点、前进
        consec_throttle = 0
        with open(cp, 'a') as f:
            f.write(json.dumps(note, ensure_ascii=False) + "\n")
        count += 1
        i += 1
        since_rest += 1
        if count % 5 == 0 or i == len(pending):
            print("[%s] %d/%d  (last: %s | %s)" % (name, count, total, note.get('time'), note.get('title')))
        if since_rest >= 30:       # 每抓 30 篇长休息一次，主动降压
            since_rest = 0
            rest = random.uniform(20, 40)
            print("[%s] 已抓 30 篇，长休息 %.0fs" % (name, rest))
            time.sleep(rest)
    notes = []
    for l in open(cp):
        l = l.strip()
        if l: notes.append(json.loads(l))
    json.dump({'boardName': name, 'boardUrl': links[0] if links else '', 'notes': notes},
              open(out_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print("WROTE %s (%d notes)" % (out_json, len(notes)))
    try: close_win(win)
    except: pass

if __name__ == '__main__':
    board = sys.argv[1]; name = sys.argv[2]; out = sys.argv[3]
    links = collect_links(board, name)
    scrape_details(name, links, out)
