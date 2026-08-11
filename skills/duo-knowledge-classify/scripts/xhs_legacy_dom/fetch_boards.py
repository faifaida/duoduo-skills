import sys, time, json, os
sys.path.insert(0, '/Users/Zhuanz/Downloads/xhs_scraper')
from core import launch, run_js, close_win

PROFILE = "https://www.xiaohongshu.com/user/profile/583a9ac67fc5b85a7fa37305?tab=fav&subTab=board"

def main():
    win = launch(PROFILE)
    time.sleep(10)
    # scroll to load all boards
    for _ in range(15):
        try:
            run_js(win, 'scroll_bottom.js', 20)
        except: pass
        time.sleep(1.5)
    # collect board ids
    raw = run_js(win, 'boards_probe.js', 30)
    try:
        boards = json.loads(raw)
    except Exception as e:
        print("PARSE FAIL:", e, "RAW:", raw[:300])
        boards = []
    close_win(win)
    print(json.dumps(boards, ensure_ascii=False, indent=1))

if __name__ == '__main__':
    main()
