#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
duoduo-voice-journal · 新版流水线（2026-08-03 起）

工作流变更（多多拍板）：
  快捷指令已能实时把音频转成 Note 丢进 notes 箱。因此 10:00 不再转录音频，
  改为「用 Note 汇总当日日记」——但仍要核对 音频↔笔记 对照。

本脚本只做【机制】部分（无 LLM）：
  --prepare  解析当天碎片笔记 → 校验每篇 embed 的录音是否真在 voice/ 箱
             （embed 写的扩展名与实文件不符时自动容错，并把 embed 就地改对
             文件名，【不移动任何音频】）→ 检测孤儿音频 → 打印 prepared fragments JSON。
  --archive  把已处理的碎片笔记从 notes 箱移进 done/。

【语义】部分（topics/highlights 反填、跨碎片合并 frontmatter、写出当日日记）
由 duoduo-day-dy skill（LLM，在 10:00 自动化里加载）完成。

约定（inbox 路径【动态发现】，兼容多多重命名/移动）：
  多多会把 duoduo_iNBox 改名/移动（如 01_INBOX/DuoDuo_dairy）。本脚本不再硬编码：
  - 优先扫 <VAULT>/01_INBOX/ 下「含 notes+voice 子目录」的文件夹；
  - 回退 <VAULT>/01_INBOX/notes、<VAULT>/01_INBOX/voice；
  - 回退旧 CloudDocs 路径 com~apple~CloudDocs/DuoDuo_Inbox/{notes,voice}。
  音频格式支持 m4a / wav / mp3（embed 写的扩展名与实文件不符时自动容错）。
  vault 日记：<VAULT>/07_Journals/01 Daily/<YYYY>/<日期>.md
  音频位置：由快捷指令决定，默认落在 <VAULT>/01_INBOX/<x>/voice/（或你指定的
            iCloud 文档位置）。【本脚本绝不移动/删除音频】——录音始终待在原地，
            Obsidian 通过 vault 内 embed 内联播放。inbox 不会 bloat（音频本就在那）。
  ※ 若把音频放到 vault 之外的 iCloud 文档（CloudDocs 非 vault 区），Obsidian 的
    ![[...]] embed 无法内联播放，日记只能放可点击的外部文件链接——是否走这条
    路线由多多决定，本脚本会相应调整 embed 写法。
"""
import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path

VAULT = Path(os.path.expanduser(
    "~/Library/Mobile Documents/iCloud~md~obsidian/"
    "Documents/DuoDuo_AI_Workspace"))
JOURNAL = VAULT / "07_Journals/01 Daily"

INBOX_CLOUD = Path(os.path.expanduser(
    "~/Library/Mobile Documents/com~apple~CloudDocs/DuoDuo_Inbox"))
INBOX_DEF_ROOT = VAULT / "01_INBOX"


def discover_inbox(sub):
    """动态定位 diary inbox 的 notes/voice 子目录。
    多多会把 duoduo_iNBox 重命名/移动（如 01_INBOX/DuoDuo_dairy），
    这里兼容：优先 01_INBOX 下含 notes+voice 的子目录，回退旧路径。"""
    cands = []
    if INBOX_DEF_ROOT.exists():
        for d in sorted(INBOX_DEF_ROOT.iterdir()):
            if d.is_dir() and (d / sub).is_dir():
                cands.append(d / sub)
        cands.append(INBOX_DEF_ROOT / sub)
    cands.append(INBOX_CLOUD / sub)
    seen, out = set(), []
    for c in cands:
        if c.exists() and c not in seen:
            seen.add(c)
            out.append(c)
    return out


NOTE_INBOXES = discover_inbox("notes")
VOICE_INBOXES = discover_inbox("voice")

PLACEHOLDER_TOPICS = "主题事项"
PLACEHOLDER_HIGHLIGHTS = "有生命力的事"


# ---------------------------------------------------------------------------
# 解析碎片笔记（兼容全角冒号 + • 项目符号，不当标准 YAML 硬解）
# ---------------------------------------------------------------------------
def parse_fragment(text):
    s = text.lstrip("\ufeff")
    if not s.startswith("---"):
        return {}, text
    end = s.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_raw = s[3:end]
    body = s[end + 4:].lstrip("\n")
    fm = {}
    cur = None
    for line in fm_raw.split("\n"):
        stripped = line.rstrip()
        if not stripped.strip():
            continue
        if stripped.strip().startswith(("•", "-", "*")):
            item = stripped.strip()[1:].strip().strip('"').strip("'").strip("”").strip("“")
            if cur and fm.get(cur) is not None:
                if not isinstance(fm[cur], list):
                    fm[cur] = [fm[cur]] if fm[cur] != "" else []
                if isinstance(fm[cur], list):
                    fm[cur].append(item)
            continue
        m = re.match(r'^([A-Za-z_一-鿿]+)\s*[:：]\s*(.*)$', stripped)
        if m:
            key = m.group(1).strip()
            val = m.group(2).strip().strip('"').strip("'").strip("”").strip("“")
            # 去掉行内注释（"值 # 注释" 中 # 后跟空格的部分；
            # wikilink 的 [[名称#课题]] 中 # 后无空格，保留）
            val = re.split(r'#\s', val, maxsplit=1)[0].strip()
            if val == "":
                fm[key] = []
                cur = key
            else:
                fm[key] = val
                cur = key
        else:
            if cur and fm.get(cur) is not None:
                if isinstance(fm[cur], list):
                    fm[cur].append(stripped.strip())
                else:
                    fm[cur] = fm[cur] + " " + stripped.strip()
    return fm, body


def find_embed(body):
    m = re.search(r'!\[\[([^\]]+\.(?:m4a|wav|mp3))\]\]', body, re.IGNORECASE)
    return m.group(1) if m else None


def audio_dt_from_name(name):
    # 兼容 12 位（YYYYMMDDHHMM，苹果语音备忘录命名）与 14 位（含秒）
    m = re.search(r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(?:(\d{2}))?', name)
    if m:
        ss = int(m.group(6)) if m.group(6) else 0
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                        int(m.group(4)), int(m.group(5)), ss)
    return datetime.now()


def note_time_from_name(name):
    m = re.search(r'(\d{4}-\d{2}-\d{2})[ _](\d{2})(\d{2})', name)
    if m:
        return f"{m.group(2)}:{m.group(3)}"
    return ""


def life_day_for_now():
    """按真版 day dy 日界线（06:00）算出「上一个生活日」归属日期。
    当前时间 >= 06:00 → 上一个生活日 = 昨天；
    当前时间 <  06:00 → 上一个生活日 = 前天。
    日记归属该生活日，范围 = 生活日06:00 ~ 次日05:59。"""
    now = datetime.now()
    if now.hour >= 6:
        d = now.date() - timedelta(days=1)
    else:
        d = now.date() - timedelta(days=2)
    return d.strftime("%Y-%m-%d")


def find_audio_file(audio_name):
    base = audio_name.rsplit(".", 1)[0]
    exts = [".m4a", ".wav", ".mp3"]
    for box in VOICE_INBOXES:
        cand = box / audio_name
        if cand.exists():
            return cand
        for ext in exts:  # embed 扩展名与实文件不符时（如写 .m4a 实 .wav）容错
            cand2 = box / (base + ext)
            if cand2.exists():
                return cand2
    return None


def _read_note(f):
    try:
        txt = f.read_text(encoding="utf-8")
    except Exception:
        return None
    fm, body = parse_fragment(txt)
    return (f, fm, body)


def collect_notes(life_day_str):
    """收集「上一个生活日」归属的碎片笔记：
    生活日当天全部 + 次日 06:00 前的笔记（属上一个生活日末尾）。
    跳过 done/ 子目录。"""
    ld = datetime.strptime(life_day_str, "%Y-%m-%d").date()
    nd = (ld + timedelta(days=1)).strftime("%Y-%m-%d")
    out = []
    for box in NOTE_INBOXES:
        for f in sorted(box.glob("*.md")):
            if f.parent.name == "done":
                continue
            name = f.name
            # 生活日当天（如 2026-08-03 2239 .md）
            if re.match(rf"{re.escape(life_day_str)}[ _]\d{{4}}\b", name):
                r = _read_note(f)
                if r:
                    out.append(r)
                continue
            # 次日 06:00 前（属上一个生活日末尾）
            m = re.match(rf"{re.escape(nd)}[ _](\d{{2}})\d{{2}}", name)
            if m and int(m.group(1)) < 6:
                r = _read_note(f)
                if r:
                    out.append(r)
    return out


def all_voice_files(life_day_str):
    """收集「上一个生活日」归属的音频：生活日当天全部 + 次日 06:00 前。
    支持 m4a/wav/mp3（新录音常为 .wav，旧逻辑只认 .m4a 会漏 orphan）。"""
    ld = datetime.strptime(life_day_str, "%Y-%m-%d").date()
    nd = ld + timedelta(days=1)
    out = []
    for box in VOICE_INBOXES:
        for ext in ("*.m4a", "*.wav", "*.mp3"):
            for f in sorted(box.glob(ext)):
                m = re.search(r"(\d{4})(\d{2})(\d{2})[ _]?(\d{2})(\d{2})", f.name)
                if not m:
                    continue  # 无日期戳的音频无法判定归属，跳过
                y, mo, d, h, _ = map(int, m.groups())
                fdate = datetime(y, mo, d).date()
                if fdate == ld:
                    out.append(f)
                elif fdate == nd and h < 6:
                    out.append(f)
    return out


def rewrite_note_embed(path, old, new):
    try:
        txt = path.read_text(encoding="utf-8")
        txt2 = txt.replace(f"![[{old}]]", f"![[{new}]]")
        if txt2 != txt:
            path.write_text(txt2, encoding="utf-8")
    except Exception:
        pass  # JSON 已带正确 embed，笔记 rewrite 失败不阻塞


def prepare(date_str, dry_run=False):
    """解析上一个生活日的碎片笔记。

    【不再搬音频】——录音由快捷指令自动落到 voice/ 箱，笔记已自带
    ![[录音名]] embed。本步只做机制（无 LLM）：
      · 用扩展名容错把笔记里的 embed（可能写 .m4a 实 .wav）对上真实文件名，
        并把 embed 就地改写成正确的文件名（【不移动任何音频文件】）；
      · 标记音频状态（ok / missing）；
      · 检测孤儿音频（voice/ 里有、但没有任何笔记引用），仅报告、不搬；
      · 打印 prepared fragments JSON 供 duoduo-day-dy（LLM）使用。

    音频始终待在原地（inbox/voice 或你指定的 iCloud 位置），
    Obsidian 通过 vault 内 embed 内联播放。
    """
    notes = collect_notes(date_str)
    fragments = []
    used_audio = set()
    cross = []

    for path, fm, body in notes:
        emb = find_embed(body)
        audio_src = find_audio_file(emb) if emb else None
        new_embed = None
        if audio_src:
            new_embed = audio_src.name  # 仅修正扩展名/文件名，不移动
            if not dry_run and emb != new_embed:
                rewrite_note_embed(path, emb, new_embed)
            used_audio.add(audio_src.name)
            cross.append({"note": path.name, "audio": emb,
                          "status": "ok", "embed": new_embed})
        else:
            cross.append({"note": path.name, "audio": emb,
                          "status": "missing"})
        fragments.append({
            "note": path.name,
            "time": note_time_from_name(path.name),
            "frontmatter": fm,
            "body": body,
            "audio_embed": new_embed,
            "audio_status": "ok" if audio_src else "missing",
        })

    orphans = []
    for av in all_voice_files(date_str):
        if av.name not in used_audio:
            orphans.append({"audio": av.name,
                            "time": audio_dt_from_name(av.name),
                            "embed": None, "note": None})
            used_audio.add(av.name)

    return {"date": date_str, "fragments": fragments,
            "orphans": orphans, "cross_check": cross,
            "dry_run": dry_run, "audio_moved": False}


def archive(date_str):
    """把已处理的碎片笔记从 notes 箱移进 done/。
    覆盖：生活日当天的笔记 + 次日 06:00 前（文件名带次日日期，属上一个生活日末尾）。"""
    moved = []
    ld = datetime.strptime(date_str, "%Y-%m-%d").date()
    nd = (ld + timedelta(days=1)).strftime("%Y-%m-%d")
    for box in NOTE_INBOXES:
        done = box / "done"
        # 生活日当天
        for f in sorted(box.glob(f"{date_str}*.md")):
            done.mkdir(parents=True, exist_ok=True)
            dest = done / f.name
            shutil.move(str(f), str(dest))
            moved.append(str(dest))
        # 次日 06:00 前（文件名带次日日期，如 2026-08-04 0142）
        for f in sorted(box.glob(f"{nd}*.md")):
            m = re.match(rf"{re.escape(nd)}[ _](\d{{2}})\d{{2}}", f.name)
            if m and int(m.group(1)) < 6:
                done.mkdir(parents=True, exist_ok=True)
                dest = done / f.name
                shutil.move(str(f), str(dest))
                moved.append(str(dest))
    return moved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None,
                    help="YYYY-MM-DD 生活日归属日期；不传则按 06:00 日界线自动算上一个生活日")
    ap.add_argument("--prepare", action="store_true")
    ap.add_argument("--archive", action="store_true")
    ap.add_argument("--dry-run", action="store_true",
                    help="prepare 仅报告，不改写任何 embed（音频本就不移动）")
    args = ap.parse_args()

    date_str = args.date or life_day_for_now()

    if args.prepare:
        result = prepare(date_str, dry_run=args.dry_run)
        # JSON 默认 default=str：兼容 datetime 等不可序列化对象
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return
    if args.archive:
        moved = archive(date_str)
        print(f"ARCHIVED {len(moved)} notes:")
        for m in moved:
            print("  -", m)
        return
    print("需要 --prepare 或 --archive", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
