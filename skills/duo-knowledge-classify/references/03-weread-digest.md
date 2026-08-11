# 微信读书周摘要（原 skill: duoduo-weread-digest）

# duoduo-weread-digest (微信读书 highlight → 读书笔记 · 资料员 每周二 9:00)

Turns 多多's WeChat-Reading highlights into organized reading notes, weekly.

## When to use
- The Tuesday 09:00 researcher automation (expertId = duoduo-researcher / 资料员).
- Any "summarize my WeChat-Reading highlights into notes" request.

## Procedure
1. **Pull highlights** from WeChat Reading using the `weread-skills` tool (search books, list notes/
   highlights, browse). Scope to 多多's own highlights.
2. **Summarize** the highlights per book — distill the key ideas 多多 marked, keep her original wording
   where it matters (do NOT rewrite into generic "correct" prose).
3. **Organize into reading notes.** Write one note file per book (or per theme) into
   `03_资料员/读书笔记/` with frontmatter (book, author, date, source=微信读书).
4. **Log** what was processed; if a book has no new highlights since last week, skip it (incremental).

## Notes
- This is a 资料员 (researcher) task; owner = 资料员.
- Uses existing `weread-skills` for the data pull — this skill is the weekly orchestration + note
  formatting on top of it.
- Reading notes are for 多多's own reference; do not publish.

## 动作节点（多多能听懂的）
1. 每周二上午 9 点，资料员从微信读书里把你这周划线的 highlight 拉出来。
2. 按书/主题总结成读书笔记（保留你原来的话，不改写成套话）。
3. 笔记整理进 `03_资料员/读书笔记/` 文件夹，带书名/作者/日期。
4. 没有新划线的书就跳过，不重复生成。
