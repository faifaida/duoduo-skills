---
name: notion-journal-split
description: 把 Notion 里"一个月日记放在一个 page 下"的聚合页,按正文写的 M/D 日期拆分成独立 Obsidian daily note。适用:Notion journal 批量迁移到 Obsidian 后,发现有些页是按月聚合的,需要拆开。
agent_created: true
---

# Notion 月度聚合日记 → Obsidian 拆分

## 何时用
- Notion 里某数据库页面是"一个月的日记塞在一个 page 下",正文用 `7/17`、`11/2` 等标记每天。
- 已迁移到 Obsidian 但仍是聚合页,需要按日期拆成 `YYYY-MM-DD.md`。
- 年份取聚合页自身年份(用户写 M/D 时创作年)。

## 关键坑(必看)
1. **本地文件日期已被 Notion 渲染打散**(如 `7/`+`1`+`2` 三个段落 = 7/12),不能直接在本地拆。必须回 Notion 拉原始 block 流(`blocks.children.list` 递归)在干净数据上拆。
2. **日期识别三态**:(a) 行首日期 `11/2 这两天…`(b) 段落内日期 (c) 被打散碎片 `7/`+`1`+`2`。状态机都要覆盖。
3. **过滤假日期**:正文顺带提的日期(如"从现在到8/12是三周")不是新日记起点。规则:**只有「行首日期」或「带星期(周X)的日期」才算新日记起点**,其余当正文。
4. **Notion v3 API**:`databases.*` 已改名 → 用 `client.data_sources.query(data_source_id=...)` + 搜索 `client.search(filter={"property":"object","value":"data_source"})`。**每次 block 读取 `time.sleep(0.34)`** 防限流。
5. **ai_block 容错**:含 Notion AI 块的页 `blocks.children.list` 会抛异常,需 try/except 跳过并留占位。
6. **边写边落盘 + 可续跑**:先全部拉再统一写会因进程被回收而零落盘。按目标日期逐个写,已存在文件跳过。

## 字段映射(本用户 vault 约定)
- `media: knowledge work`、`source: notion` 固定。
- `occasion`/`focus`:逐条无数据时留空(不要硬塞 Monthly)。
- `people`/`location`:正文按审定词典抽(中文无可靠 NER,只抽有把握的)。
- 模板=T05 八段式(今日发生/当时的我/我在想什么/灵感与创造/工作与推进/明日与以后/今天留下来的几句话/今日小结)。

## 流程
1. 扫描 vault 找聚合页(本例 `occasion: Monthly`)。
2. dry-run:回 Notion 拉每页原始 block → tokenize → 打印每页拆出条数,人工核对有无假日期/漏识别。
3. 用户确认排除名单(工作笔记等不拆的页)。
4. 备份聚合源文件 → `--write` 执行 → 核对:排除页仍在、聚合源删除(或同名被新日记覆盖)、抽查格式。
