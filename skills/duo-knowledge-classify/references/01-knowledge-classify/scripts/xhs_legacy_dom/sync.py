import sys, os, json, time, datetime
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
from scrape import collect_links, scrape_details, extract_note_id
import process

VAULT = process.VAULT

def load_boards():
    cfg = json.load(open(os.path.join(SC, 'boards.json'), encoding='utf-8'))
    return [(b['id'], b['name']) for b in cfg['boards']]

ALBUMS = [("https://www.xiaohongshu.com/board/%s" % bid, name) for bid, name in load_boards()]
IMPORTED = os.path.join(SC, "imported_ids.json")
OUT = lambda name: "/Users/Zhuanz/Downloads/xhs_%s.json" % name

def load_imported():
    if os.path.exists(IMPORTED):
        try:
            return json.load(open(IMPORTED, encoding='utf-8'))
        except Exception:
            pass
    return {}

def save_imported(d):
    json.dump(d, open(IMPORTED, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def sync_one(url, name):
    # 强制重新采集链接（不用缓存），以发现新收藏
    lp = os.path.join(SC, 'links_%s.json' % name)
    if os.path.exists(lp):
        os.remove(lp)
    links = collect_links(url, name)
    out = OUT(name)
    if os.path.exists(out):
        d = json.load(open(out, encoding='utf-8'))
    else:
        d = {'boardName': name, 'boardUrl': url, 'notes': []}
    existing_ids = set(n.get('noteId') for n in d.get('notes', []))
    imported = set(load_imported().get(name, []))
    known = existing_ids | imported
    new_links = [c for c in links if extract_note_id(c) not in known]
    print("[%s] 链接 %d，已知 %d，新增 %d" % (name, len(links), len(known), len(new_links)))
    if not new_links:
        return 0
    # 只抓取新增的笔记详情
    scrape_details(name, new_links, out)
    d = json.load(open(out, encoding='utf-8'))
    new_ids = set(extract_note_id(c) for c in new_links)
    album_dir = os.path.join(VAULT, name)
    os.makedirs(album_dir, exist_ok=True)
    used = {}
    written = 0
    for n in d.get('notes', []):
        if n.get('noteId') not in new_ids:
            continue
        if not n.get('valid'):   # 风控/验证页抓空的，不写脏笔记，留待下周重试
            continue
        title = n.get('title') or '(无标题)'
        timev = n.get('time') or process.COLLECTED
        base = process.sanitize("%s - %s" % (title, timev))
        fname = base
        if fname in used:
            used[fname] += 1
            fname = "%s_%d" % (base, used[fname])
        else:
            used[fname] = 1
        open(os.path.join(album_dir, fname + ".md"), "w", encoding='utf-8').write(process.note_md(n, name))
        written += 1
    # 只把成功抓到的 id 记入去重表；被风控的留空，下周重试
    valid_new = set(n.get('noteId') for n in d.get('notes', []) if n.get('noteId') in new_ids and n.get('valid'))
    imp = load_imported()
    imp[name] = sorted(set(imp.get(name, [])) | valid_new)
    save_imported(imp)
    # 清理检查点：只保留有效笔记，被风控的移除以便重试
    cp = os.path.join(SC, 'done_%s.jsonl' % name)
    if os.path.exists(cp):
        good = [l for l in open(cp, encoding='utf-8') if l.strip() and json.loads(l).get('valid')]
        open(cp, 'w', encoding='utf-8').writelines(good)
    process.rebuild_index(name)
    print("[%s] 新增写入 %d 篇（有效）" % (name, written))
    return written

if __name__ == '__main__':
    os.environ['XHS_COLLECTED_DATE'] = datetime.date.today().isoformat()
    boards = load_boards()
    print("本次同步 %d 个专辑: %s" % (len(boards), "、".join(n for _, n in boards)))
    total = 0
    for url, name in ALBUMS:
        try:
            total += sync_one(url, name)
        except Exception as e:
            print("!! %s 失败: %s" % (name, e))
    print("=== 本次共新增 %d 篇 ===" % total)
