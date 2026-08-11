#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读 03_补对标_家族二代等.json → 生成 03_补对标_家族二代等.md 分析报告。
报告含：每关键词小号爆款表 + 形式/互动拆解 + 为什么火(框架+观察, 待多多读原文补全)。
"""
import json, os
BASE = "/Users/Zhuanz/Library/Mobile Documents/iCloud~md~obsidian/Documents/DuoDuo_AI_Workspace/03_ACTIVE PROJECTS/ai个人公司/公司档案/02_内容运营/Human3_内容执行包"
JSON = os.path.join(BASE, "03_补对标_家族二代等.json")
OUT = os.path.join(BASE, "03_补对标_家族二代等.md")

PILLAR = {
    "家族企业二代": "支柱① 家族资源与个人主权",
    "数字游民": "支柱①/③ 数字游民 / 独立女性（流量生活方式）",
    "独立女性": "支柱①/③ 独立女性（主权叙事）",
    "身体节律": "支柱④ Follow Earth. Not Calendar. 节律",
    "非日历节律": "支柱④ Follow Earth. Not Calendar. 节律",
}

def fmt(n):
    return "{:,}".format(n) if isinstance(n, int) else str(n)

def main():
    data = json.load(open(JSON, encoding="utf-8"))
    L = []
    L.append("# 补对标分析 · 小号爆款（家族二代 / 数字游民 / 独立女性 / 身体节律）\n")
    L.append("> 数据：Spider_XHS 签名 API 搜关键词爆款笔记，过滤粉丝<2万小号，取每词 Top 小号爆款。\n")
    L.append("> 用途：对齐 Human3.0 四支柱，给多多的内容选题/形式/钩子做对标。\n")
    L.append("> ⚠️ 互动数为赞+藏+评+转合计；「为什么火」为基于形式/数据的**框架性观察**，具体火因需多多点开原文核对。\n")
    total = 0
    for kw, rows in data.items():
        total += len(rows)
        L.append("\n## %s · %s\n" % (kw, PILLAR.get(kw, "")))
        L.append("- 小号爆款样本数：**%d**\n" % len(rows))
        if not rows:
            L.append("\n（该词未取到小号爆款样本——可能热门词下小号未进前排，或账号当时受限。换词/换时间重试。）\n")
            continue
        vids = sum(1 for r in rows if r.get("form") == "video")
        L.append("- 形式分布：视频 %d / 图文 %d（视频占比 %.0f%%）\n" % (vids, len(rows) - vids, 100 * vids / len(rows)))
        L.append("\n| # | 作者 | 粉丝 | 互动合计 | 形式 | 标题 |\n|---|---|---|---|---|---|")
        for i, r in enumerate(rows, 1):
            L.append("| %d | %s | %s | %s | %s | %s |" % (
                i, r.get("author", ""), fmt(r.get("fans", 0)), fmt(r.get("interactions", 0)),
                "视频" if r.get("form") == "video" else "图文", (r.get("title") or "（标题待取）")[:40]))
        L.append("\n**形式/互动观察**")
        L.append("- 该词下小号爆款以%s为主，说明这类内容小号靠%s更易起量。" % (
            "视频" if vids >= len(rows) - vids else "图文",
            "真实出镜/ Demonstration" if vids >= len(rows) - vids else "信息密度/合集"))
        top = max(rows, key=lambda r: r.get("interactions", 0))
        L.append("- 互动最高：**%s**（%s粉，%s互动），标题《%s》——可作为该词钩子参考。" % (
            top.get("author"), fmt(top.get("fans", 0)), fmt(top.get("interactions", 0)),
            (top.get("title") or "（待取）")[:30]))
        L.append("\n**为什么火（框架，待多多读原文补全）**")
        L.append("1. 选题切口：是否戳中「现成路 vs 自己路」「身体/审美主权」这类冲突？")
        L.append("2. 开头钩子：前3秒是否抛出反直觉/具体场景？")
        L.append("3. 形式：口播对镜 vs 素材拼剪 vs 图文，哪种更贴合该人群？")
        L.append("4. 收藏动机：是否被当成「可复用的方法/清单」？")
    L.append("\n---\n## 总览\n")
    L.append("- 5 词合计小号爆款样本：**%d** 条。\n" % total)
    L.append("- 用法：每词挑 1–2 条原文精读，拆「钩子→结构→CTA」，映射到多多四支柱脚本。\n")
    L.append("- 下一步：把共性写成「小号爆款公式」，回填到视频脚本与文字包。\n")
    open(OUT, "w", encoding="utf-8").write("\n".join(L))
    print("[done] 报告已写 %s （样本 %d 条）" % (OUT, total))

if __name__ == "__main__":
    main()
