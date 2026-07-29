---
name: duoduo-expert-hourly-patrol
description: >
  The hourly self-pickup mechanism for 多多's three WorkBuddy expert employees (content-ops /
  researcher / product-manager). Each expert polls its own folder every hour (local 10:00–23:00),
  executes any new instruction, marks it done in the release list to avoid repeats, and scans
  06_待多多审核/ for files whose Owner == itself (内容运营 / 资料员 / 产品经理) to claim 多多's == ==
  marks. Non-employee-owned == == files are handled by duoduo-approval-detect-and-release (run by 总办
  10:00/23:00); this skill does NOT re-scan those. Replaces the dead ChatGPT/IMA "read local files" approach.
agent_created: true
---

# duoduo-expert-hourly-patrol (专家每小时巡检自取)

Core运转机制 of the multi-agent company. Three experts run hourly patrols.

## When to use
- The hourly patrol automations (content-ops / product-mgr / researcher).
- Any "make the employees pick up their tasks" request.

## Schedule note (IMPORTANT — fixes the 3am-run bug)
- Intended window: **local 10:00–23:00** (14 runs/day). 多多白天工作段，夜间不跑。
- The scheduler evaluates HOURLY `BYHOUR` in **UTC**, not local. So the rrule uses
  `BYHOUR=2,3,4,5,6,7,8,9,10,11,12,13,14,15` (UTC) which maps to local 10:00–23:00 and
  explicitly excludes local 00:00–09:00. If a patrol ever appears outside 10:00–23:00 local,
  the rrule drifted and must be re-set to those UTC values.

## Procedure (per expert)
1. **Poll own folder** (`02_内容运营/` / `03_资料员/` / `04_产品经理/`) for new `指令_` / `通知_` files.
1b. **Poll 待审 for own items.** Scan `06_待多多审核/` for files whose `Owner` header == this expert (内容运营 / 资料员 / 产品经理). If 多多 highlighted `== ==` new content/approval there, claim and act on it.
2. **Execute** any new instruction found.
3. **Mark done** in `01_总经办/已审放行清单.md` (or the instruction's own tracking) so the same item is
   never run twice.
4. **Claim approvals (two sources).** (a) Released items from `duoduo-approval-detect-and-release`
   (non-employee-owned files) appear in `01_总经办/已审放行清单.md` — pick them up. (b) Employee-owned
   `== ==` marks in `06_待多多审核/` (step 1b) — claim directly here. Both flow without 多多 manual notify.
5. 多多 never needs to manually tell an employee "approved" — the system flows it.

## Known failure modes
| Symptom | Root cause | Fix |
|---|---|---|
| Employee does nothing | Old design read local files cross-platform (impossible) | Self-pickup from own folder |
| Same task done twice | No done-marking | Mark in release list |
| Patrol at 0–9am | HOURLY BYHOUR read as UTC | Use UTC 2..15 → local 10–23 |
| Approved task stalls | Manual notify assumed | Detect via duoduo-approval-detect-and-release |

## 动作节点（多多能听懂的）
1. 三位员工每小时（本地 10:00–23:00，共 14 次/日）自动巡检自己的文件夹 + 待审里 owner=自己的文件。**不会在 23:00 之后或凌晨跑**（时区设错已修）。
2. 发现新指令→执行→在放行清单标 done，防止重复做。
3. 你用 == == 高亮批复「员工 owner」的待审文件，员工下一轮巡检直接认领并执行；非员工 owner 的待审由专门批复检测 skill（总办 10:00/23:00 跑）收进放行清单。
4. 你不用手动通知员工"已审批"，系统自己流转。
