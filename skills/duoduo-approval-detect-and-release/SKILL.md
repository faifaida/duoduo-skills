---
name: duoduo-approval-detect-and-release
description: >
  Detect 多多's == == highlight approvals in Obsidian and drive the downstream release: move approved
  pending-review files into archive/ (task-type ones), and append them to 01_总经办/已审放行清单.md so
  expert employees claim them on their next hourly patrol. This is the SINGLE dedicated approval-detect
  skill — invoked by the 10:00 and 23:00 总办 passes. SCOPE: only processes 06_待多多审核/ files whose
  Owner is NOT one of the three employees (内容运营/资料员/产品经理); employee-owned files are claimed by
  the employees' own hourly patrol. 多多 only needs to highlight — no manual notify.
agent_created: true
---

# duoduo-approval-detect-and-release (== == 批复检测与放行)

The approval hub of the company OS. This is the ONLY place that scans `== ==` highlights.

## When to use
- Invoked by `duoduo-company-daily-os` (13:00), `duoduo-company-night-patrol` (23:00), and the hourly
  patrols (`duoduo-expert-hourly-patrol` consumes its output — it does NOT re-detect).
- Any "check what 多多 approved" request.

## Procedure
1. **Scan for `== ==` highlights** across `06_待多多审核/`. **Skip any file whose `Owner` header is one of
   the three employees (内容运营 / 资料员 / 产品经理)** — those are claimed by the employee's own hourly
   patrol. Process only non-employee-owned files (Owner = 总办 / 多多 / 其他).
2. For an approved file:
   - If it is a **task-type** item → move it into `archive/` AND append a row to
     `01_总经办/已审放行清单.md` describing the released task.
   - If it is a **reference/doc** item → move to `archive/` (no release-list row needed).
3. Employees claim release-list rows on their next hourly patrol (`duoduo-expert-hourly-patrol`).
4. 多多 only highlights — the rest is automatic.

## Notes
- `== ==` is the ONLY approval signal; do not invent others.
- Move-only into `archive/`, never delete.
- Do NOT re-describe this flow inside the patrol skill — that caused duplication; the patrol just calls
  this skill.

## 动作节点（多多能听懂的）
1. 扫描你用 `== ==` 高亮批复的内容（全公司唯一批复检测点，但**只处理 owner 非三员工的待审文件**；员工 owner 的由员工每小时巡检自行认领）。
2. 批复的非员工 owner 待审文件→移进 `archive/`（任务类）→写进 `已审放行清单.md`。
3. 员工每小时巡检时来认领放行清单里非员工 owner 的任务。
4. 你只需要高亮，其余不用管。
