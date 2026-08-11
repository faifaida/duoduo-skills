#!/usr/bin/env python3
"""把 faifaida/duoduo-skills 的最新 GitHub Release 同步到本地 ~/.workbuddy/skills/。

设计要点：
- 只用 Python 标准库（urllib/zipfile），无需 pip install，任何机器可跑。
- 走 GitHub REST API 下载 release zipball；**支持 private 仓库**（自动带鉴权）。
- 本仓库是技能的**唯一权威源**；本地只是一份自动同步的镜像，不要手改本地。
- 仅同步本仓库包含的技能（按文件夹名匹配、且含 SKILL.md），不会删除本地其它技能。

用法：
    python3 scripts/sync_skills.py                 # 同步到最新 release
    python3 scripts/sync_skills.py --dry-run       # 只看会改哪些，不落盘
    python3 scripts/sync_skills.py --version=v1.2.0 # 同步到指定 tag

鉴权（private 仓库必须）：脚本按以下顺序取 token
    1. 环境变量 GITHUB_TOKEN
    2. `gh auth token`（本机 gh CLI）
取不到则匿名请求（仅对 public 仓库有效）。
"""
import json
import os
import sys
import shutil
import subprocess
import tempfile
import urllib.request
import urllib.error
import zipfile

REPO = "faifaida/duoduo-skills"
API = f"https://api.github.com/repos/{REPO}"
LOCAL_SKILLS = os.path.expanduser("~/.workbuddy/skills")

DRY_RUN = "--dry-run" in sys.argv
SPECIFIC = None
for a in sys.argv[1:]:
    if a.startswith("--version="):
        SPECIFIC = a.split("=", 1)[1]


def get_token():
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        return tok
    # 退回本机 gh CLI
    for cand in (
        "/Users/Zhuanz/Documents/文稿 - Mac/Codex/bin/gh",
        "gh",
    ):
        try:
            out = subprocess.run(
                [cand, "auth", "token"],
                capture_output=True,
                text=True,
                timeout=20,
            )
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
        except (FileNotFoundError, subprocess.SubprocessError):
            continue
    return None


TOKEN = get_token()


def http_get(url):
    headers = {
        "User-Agent": "duoduo-skill-sync",
        "Accept": "application/vnd.github+json",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read(), r.headers
    except urllib.error.HTTPError as e:
        # 手动跟随重定向，跨到 codeload.github.com 时带上 token（urllib 默认会丢 header）
        if e.code in (301, 302, 303, 307, 308):
            loc = e.headers.get("Location")
            if loc:
                if TOKEN and "codeload.github.com" in loc and "token=" not in loc:
                    loc += ("&" if "?" in loc else "?") + "token=" + TOKEN
                return http_get(loc)
        raise


def resolve_target():
    if SPECIFIC:
        http_get(f"{API}/releases/tags/{SPECIFIC}")  # 校验存在
        return SPECIFIC, f"{API}/zipball/refs/tags/{SPECIFIC}"
    try:
        data, _ = http_get(f"{API}/releases/latest")
        rel = json.loads(data)
        return rel["tag_name"], rel["zipball_url"]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "(default branch)", f"{API}/zipball/refs/heads/main"
        raise


def main():
    version, zip_url = resolve_target()
    print(f"[sync] target version : {version}")
    print(f"[sync] downloading    : {zip_url}")
    if not TOKEN:
        print("[sync] 警告: 未检测到 token，private 仓库会失败；public 仓库可正常。")
    raw, _ = http_get(zip_url)

    tmp = tempfile.mkdtemp(prefix="duoduo-sync-")
    zpath = os.path.join(tmp, "rel.zip")
    with open(zpath, "wb") as f:
        f.write(raw)

    extract_dir = os.path.join(tmp, "extracted")
    with zipfile.ZipFile(zpath) as z:
        z.extractall(extract_dir)

    top = os.path.join(extract_dir, os.listdir(extract_dir)[0])
    skills_src = os.path.join(top, "skills")
    if not os.path.isdir(skills_src):
        print("[sync] ERROR: skills/ 不在 release 包里", file=sys.stderr)
        sys.exit(1)

    names = [
        d
        for d in os.listdir(skills_src)
        if os.path.isdir(os.path.join(skills_src, d))
        and os.path.exists(os.path.join(skills_src, d, "SKILL.md"))
    ]
    print(f"[sync] release 内含 {len(names)} 个技能")

    os.makedirs(LOCAL_SKILLS, exist_ok=True)
    copied = []
    for n in names:
        dst = os.path.join(LOCAL_SKILLS, n)
        if DRY_RUN:
            print(f"[dry-run] 将复制 {n} -> {dst}")
        else:
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(os.path.join(skills_src, n), dst)
            copied.append(n)

    if DRY_RUN:
        print(f"[dry-run] 完成。将同步 {len(names)} 个技能。")
    else:
        print(f"[sync] 完成。已同步 {len(copied)} 个技能 -> {LOCAL_SKILLS}")
        print(f"[sync] 已应用版本 {version}。重启 WorkBuddy 会话以加载新技能。")


if __name__ == "__main__":
    main()
