import sys, json, os, re, datetime

# VAULT 优先从 boards.json 读取，便于随技能迁移；缺省回退到固定路径
def _load_vault():
    try:
        cfg = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'boards.json'), encoding='utf-8'))
        return cfg.get('vault', "/Users/Zhuanz/Library/Mobile Documents/iCloud~md~obsidian/Documents/DuoDuo_AI_Workspace/05_CONTENT/小红书收藏")
    except Exception:
        return "/Users/Zhuanz/Library/Mobile Documents/iCloud~md~obsidian/Documents/DuoDuo_AI_Workspace/05_CONTENT/小红书收藏"

VAULT = os.environ.get("XHS_VAULT", _load_vault())
COLLECTED = os.environ.get("XHS_COLLECTED_DATE", datetime.date.today().isoformat())

TOPIC_KW = {
    "🔥个人提升／技能": ["技能","skill","方法","效率","学习","提升","习惯","sop","模板","干货","思维","逻辑","自律","自控","成长","复盘","认知","笔记","知识"],
    "🌻自我": ["自我","焦虑","迷茫","内心","情绪","心理","女性","女生","独处","能量","内耗","自信"],
    "🍓关系": ["关系","情感","社交","朋友","沟通","社群","恋","家人","亲密","恋爱","脱单","约会","暧昧","相亲","crush","男","女","前任","复合"],
    "🌍资源": ["资源","信息","搜索","工具","网站","赚钱","副业","变现","渠道","资料"],
    "💫职业": ["职业","职场","求职","产品经理","工作","面试","简历","升职","老板","岗位","规划"],
    "🦋探索": ["旅行","探索","青旅","出门","世界","目的地","攻略","游记","出国","徒步","露营"],
    "💗美丽": ["穿搭","妆","美","形象","护肤","医美","颜值","发型","穿","审美","风格","色彩"],
    "🍀生活方式／健康": ["健康","饮食","健身","生活","作息","睡眠","早晨","家居","断舍离","极简","养生","中医","调理","气血","脾胃","泡脚","艾灸","养生茶","八段锦"],
}
ALBUM_FOCUS = {
    "习惯和思考": ["🌻自我","🔥个人提升／技能"],
    "文旅": ["🦋探索"],
    "青旅": ["🦋探索","🌍资源"],
    "剪辑": ["💗美丽","🔥个人提升／技能"],
    "职业": ["💫职业"],
    "养生大法": ["🍀生活方式／健康"],
    "关系恋爱": ["🍓关系"],
    "审美": ["💗美丽"],
}
ALBUM_THREAD = {
    "习惯和思考": [],
    "文旅": ["文旅青旅"],
    "青旅": ["文旅青旅","流动生活"],
    "剪辑": ["内容"],
    "职业": ["内容"],
    "养生大法": [],
    "关系恋爱": ["关系与社群"],
    "审美": ["内容"],
}

def infer_focus(text, album):
    scores = {t:0 for t in TOPIC_KW}
    low = text.lower()
    for t, kws in TOPIC_KW.items():
        for k in kws:
            if k.lower() in low:
                scores[t]+=1
    ranked = sorted(scores.items(), key=lambda x:-x[1])
    picks = [t for t,s in ranked if s>0]
    if not picks:
        picks = list(ALBUM_FOCUS.get(album, ["🌻自我"]))
    for d in ALBUM_FOCUS.get(album, []):
        if d not in picks:
            picks.append(d)
    return picks[:2]

def infer_threads(text, album):
    th = ALBUM_THREAD.get(album, [])
    low = text.lower()
    if "内容" not in th and any(k in low for k in ["剪辑","视频","公众号","起号","选题","写作","脚本"]):
        th = th + ["内容"]
    if "关系与社群" not in th and any(k in low for k in ["社群","朋友","社交","关系"]):
        th = th + ["关系与社群"]
    return th

def first_sentence(desc, n=90):
    if not desc: return ""
    for sep in ["\n", "。", "！", "？", "!", "?"]:
        if sep in desc:
            s = desc.split(sep)[0].strip()
            if s: return s[:n]
    return desc[:n].strip()

def extract_method(desc):
    if not desc: return ""
    for kw in ["方法","步骤","流程","SOP","技巧","公式","模板","做法","方式"]:
        idx = desc.find(kw)
        if idx>=0:
            seg = desc[max(0,idx-10):idx+40]
            return seg.replace("\n"," ").strip()
    return ""

def sanitize(name):
    name = name.replace("/", "／").replace("\\","／")
    for c in [":","*","?","\"","<",">","|","\n","\r"]:
        name = name.replace(c, "_")
    name = name.strip().rstrip(".")
    return name[:80]

def note_md(note, album):
    title = note.get("title") or "(无标题)"
    author = note.get("author") or ""
    url = note.get("url") or ""
    time = note.get("time") or COLLECTED
    desc = note.get("desc") or ""
    valid = note.get("valid", True)
    text_blob = (title + " " + desc)
    focuses = infer_focus(text_blob, album)
    threads = infer_threads(text_blob, album)
    focus_list = ", ".join('"%s"' % f for f in focuses)
    thread_yaml = ("[%s]" % ", ".join(threads)) if threads else "[]"
    essence = first_sentence(desc) or title
    method = extract_method(desc) or "（结合正文提炼具体可落地的做法）"
    primary = focuses[0]
    thread_txt = ("、" + "、".join(threads)) if threads else ""
    convert_map = {
        "💫职业": "可整理为简历/面试素材或一篇职场经验帖；挑 1 条写成可复用的 SOP。",
        "🔥个人提升／技能": "可改写为一篇图文/短视频分享，或做成 Notion 模板供自己复用。",
        "🌻自我": "可设计成一个 7 天微小实验并写复盘；挑 1 条先落地。",
        "🦋探索": "可并入旅行/青旅灵感库，出发前做成清单与攻略。",
        "💗美丽": "可整理为种草清单或对比测评，落地一次尝试。",
        "🍀生活方式／健康": "可变成一周微习惯挑战，记录前后变化。",
        "🌍资源": "可沉淀为资源索引表（工具/渠道/资料），定期更新。",
        "🍓关系": "可转化为一次主动连接动作或关系复盘。",
    }
    convert = convert_map.get(primary, "可纳入周复盘挑 1 条落地；也可改写为一篇分享帖。")
    why = "[AI推断] 偏「%s」主题%s，收藏后拆为己用。" % (primary, thread_txt)
    kw = "true" if any(k in text_blob.lower() for k in ["方法","skill","学习","效率","模板","sop","职业","技能","产品","经理","思维","逻辑","复盘","认知","剪辑","视频"]) else "false"
    fm = """---
type: xhs-save
title: "%s"
collected_date: "%s"
author: %s
url: %s
category: [%s]
focus: [%s]
company_threads: %s
why_saved: "%s"
action: 待拆解
related: ""
status: categorized
knowledge_work: %s
source: xiaohongshu
---

# %s

> [!note] 边收边分工作流
> 收藏 = 立刻分。每收一条，至少填 `category` + `focus` + `why_saved` 三样，不让它躺在收藏夹吃灰。
> 每周把 `status: captured` 的过一遍：能用的推进到 `used`，能写成内容的转到 `05_CONTENT/01 ideas`，能实践的形成一个微小实验。
>
> **一级分类（category）参考**：穿搭形象 / 护肤美妆医美 / 健身塑形健康饮食 / 旅行青旅灵感 / 内容创作起号选题 / 副业变现个人公司 / 关系情感 / 自我成长思维 / 家居生活方式 / 职场求职
> **人生课题（focus）**：🔥个人提升／技能 / 🌻自我 / 🍓关系 / 🌍资源 / 💫职业 / 🦋探索 / 💗美丽 / 🍀生活方式／健康
> **个人公司主线（company_threads）**：文旅青旅 / 内容 / 流动生活 / 关系与社群

## 原帖要点

%s

## 我的提取

- 可取：%s
- 可复用方法：%s
- 想验证：这条能否变成【%s】的一个小实验 / 一篇内容？

## 可转化输出的内容

%s

> 来源：%s ｜ 作者：%s ｜ 抓取到正文：%s
""" % (title, COLLECTED, author, url, album, focus_list, thread_yaml, why, kw, title,
       desc if desc else "[未获取到正文]", essence, method, primary, convert, url, author, "是" if valid else "否")
    return fm

def process(board_json, album):
    d = json.load(open(board_json, encoding="utf-8"))
    notes = d.get("notes", [])
    album_dir = os.path.join(VAULT, album)
    os.makedirs(album_dir, exist_ok=True)
    used = {}
    links = []
    written = 0
    for n in notes:
        title = n.get("title") or "(无标题)"
        time = n.get("time") or COLLECTED
        base = sanitize("%s - %s" % (title, time))
        fname = base
        if fname in used:
            used[fname]+=1
            fname = "%s_%d" % (base, used[fname])
        else:
            used[fname]=1
        path = os.path.join(album_dir, fname + ".md")
        open(path, "w", encoding="utf-8").write(note_md(n, album))
        written+=1
        links.append((fname, title))
    # index file
    idx = "---\ntype: xhs-board\nboard_name: \"%s\"\nboard_url: %s\nnote_count: %d\ncollected_on: %s\nlife_topics: %s\nstatus: captured\nsource: xiaohongshu\n---\n\n# 专辑：%s\n\n> 自动导出自小红书收藏专辑。共 %d 篇笔记。\n\n## 笔记清单\n\n" % (
        album, d.get("boardUrl",""), len(notes), COLLECTED,
        " ".join("[[八个人生课题#%s]]" % f for f in ALBUM_FOCUS.get(album,["🌻自我"])),
        album, len(notes))
    for fname, title in links:
        idx += "- [[%s/%s|%s]]\n" % (album, fname, title)
    open(os.path.join(album_dir, "专辑-%s.md" % album), "w", encoding="utf-8").write(idx)
    print("WROTE %d notes + index for %s" % (written, album))
    return written

def rebuild_index(album):
    """按文件夹内现有笔记重建索引（用于增量同步后补索引）。"""
    import re as _re
    album_dir = os.path.join(VAULT, album)
    files = [f for f in os.listdir(album_dir) if f.endswith('.md') and not f.startswith('专辑-')]
    links = []
    for f in sorted(files):
        txt = open(os.path.join(album_dir, f), encoding='utf-8').read()
        m = _re.search(r'^title:\s*"?([^"\n]+)"?', txt, _re.M)
        title = m.group(1).strip() if m else f[:-3]
        links.append((f[:-3], title))
    idx = "---\ntype: xhs-board\nboard_name: \"%s\"\nnote_count: %d\ncollected_on: %s\nlife_topics: %s\nstatus: captured\nsource: xiaohongshu\n---\n\n# 专辑：%s\n\n> 自动导出自小红书收藏专辑。共 %d 篇笔记。\n\n## 笔记清单\n\n" % (
        album, len(links), COLLECTED,
        " ".join("[[八个人生课题#%s]]" % f for f in ALBUM_FOCUS.get(album,["🌻自我"])),
        album, len(links))
    for base, title in links:
        idx += "- [[%s/%s|%s]]\n" % (album, base, title)
    open(os.path.join(album_dir, "专辑-%s.md" % album), "w", encoding="utf-8").write(idx)
    print("INDEX rebuilt for %s (%d notes)" % (album, len(links)))
    return len(links)

if __name__ == "__main__":
    bj = sys.argv[1]; album = sys.argv[2]
    process(bj, album)
