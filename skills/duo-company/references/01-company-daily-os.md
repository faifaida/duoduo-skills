# 每日参谋长例程（原 skill: duoduo-company-daily-os）

# duoduo-company-daily-os (多员工公司每日 13:00 总办)

The daily operating heartbeat of 多多's personal company. Runs automatically at 13:00.

## When to use
- The 13:00 总办 automation (automation-1784643393209).
- Any "run the daily company briefing / acceptance / planning" request.

## Outputs (three artifacts)
1. **简报 (Briefing)** — what happened across the company today, per employee. **File it in the
   `公司简报/` folder** (under `01_总经办/`), not loose in the root.
2. **验收清单 (Acceptance checklist)** — cross-check against ACTUAL files produced, NOT the plan.
   A planned item is NOT "done" until its deliverable exists on disk. Flag gaps explicitly.
3. **次日计划 (Next-day plan)** — concrete tasks for each employee for tomorrow.

## Procedure
1. Aggregate prior-day output from `02_内容运营/`, `03_资料员/`, `04_产品经理/` and `01_总经办/`.
2. Build the three artifacts above. Acceptance MUST verify real files (grep the folders), never trust
   the plan as completion.
3. **Pending-review flagging:** scan `06_待多多审核/`. Files unapproved >1 day → prefix filename with
   `❗️`; >2 days → `‼️`. Actually `mv`/rename the file (emoji at the very front), not just note it.
   (This emoji flag is also done once nightly in `duoduo-company-night-patrol`; the 13:00 pass is a
   fast re-check.)
4. **Dispatch (新指令下发).** The instruction dispatched to each employee is the **previous night
   patrol's produced, 多多-approved (📩-marked) next-day plan** — NOT a fresh ad-hoc instruction. Take
   that 📩-marked plan from `06_待多多审核/` (or its archive) and route it to the matching employee
   folder; move approved files out of `06_待多多审核/` (to `archive/` if done).
5. **Approval detect:** scan for 多多's `== ==` highlight approvals → route per
   `duoduo-approval-detect-and-release`. See that skill.
5b. **多多口述指令优先（2026-07-26 学到）:** if `指令_<tomorrow>` files already exist in employee
   folders with `generated_by: … 按多多口述生成立即生效`, they are the HIGHEST authority — do NOT
   overwrite them with the automation's derived plan. The 次日计划 file consolidates/annotates them;
   supplements go in separate `通知_` files. Dictation may override the default 10:00 start time
   (e.g. "明天1点准时开始" → 13:00). Files already prefixed `！！` skip re-flagging with ❗️/‼️.
6. **Strategic anchor:** align priorities to human3.0 (主线 二代 Beta / 支线 泳衣 / 底层 节律).

## Known failure modes
| Symptom | Root cause | Fix |
|---|---|---|
| Plan reported as done | Acceptance didn't check files | Grep actual deliverables |
| 多多 overwhelmed at 14:00 | Too much unverified output | Briefing + checklist + plan, scoped |
| Wrong instruction sent | Dispatched ad-hoc vs approved plan | Use previous night's 📩 next-day plan |

## 动作节点（多多能听懂的）
1. 每天 13:00，汇总三个员工（内容/资料/产品）前一天的成果。
2. 产出**简报**（今天发生了什么）+ **验收清单**（对照实际文件，不把计划当完成）+ **次日计划**；简报放进 `公司简报/` 文件夹。
3. 扫描 `06_待多多审核` 里超过 1 天/2 天没审的文件，在文件名最前打 ❗️/‼️。
4. **下发新指令**：下发给每个员工的，是**前一天夜巡产出的、你已经审过并标 📩 的次日计划**（不是临时现编的指令）。
5. 这一套全自动跑，你 14:00 来验收当日成果即可。
