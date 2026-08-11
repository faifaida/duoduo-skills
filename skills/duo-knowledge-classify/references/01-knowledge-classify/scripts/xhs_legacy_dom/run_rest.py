import sys, time, json, os
sys.path.insert(0, '/Users/Zhuanz/Downloads/xhs_scraper')
import scrape, process

DOWNLOADS = '/Users/Zhuanz/Downloads'
BOARDS = [
    ("文旅",         "663a464c000000001c0190c8"),
    ("青旅",         "6923f149000000001103ca4a"),
    ("技能",         "660a7d2a0000000018006d19"),
    ("剪辑",         "699ddc38000000002600eaea"),
    ("职业拓展",     "660adbc10000000001029122"),
]

STATUS = os.path.join('/Users/Zhuanz/Downloads/xhs_scraper', 'status.log')
def log(msg):
    with open(STATUS, 'a') as f:
        f.write("[%s] %s\n" % (time.strftime('%H:%M:%S'), msg))
    print(msg)

if __name__ == '__main__':
    for name, bid in BOARDS:
        url = "https://www.xiaohongshu.com/board/%s" % bid
        out = os.path.join(DOWNLOADS, "xhs_%s.json" % name)
        log("=== START board %s (%s) ===" % (name, url))
        try:
            links = scrape.collect_links(url, name)
            scrape.scrape_details(name, links, out)
            n = process.process(out, name)
            log("=== DONE board %s: %d notes written ===" % (name, n))
        except Exception as e:
            log("!!! ERROR board %s: %s" % (name, e))
        time.sleep(2)
    log("=== ALL BOARDS FINISHED ===")
