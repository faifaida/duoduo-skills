# 夜巡归档（原 skill: duoduo-company-night-patrol）

# duoduo-company-night-patrol (23:00 夜巡)

Nightly cleanup and closure sweep for 多多's personal company. Runs automatically at 23:00. The archive
triage and the pending-review emoji flag are BOTH done here, once a day, in the same pass (they used to
be separate skills; 多多 merged them into this one on 2026-07-26).

## When to use
- The 23:00 夜巡 automation (automation-1784827286151).
- Any "close out the day / tidy the vault / catch missed approvals" request.

## Procedure (run as one daily pass)
1. **Re-sweep tasks.** Walk today's tasks across employee folders; list anything not yet closed.
2. **Archive triage.** For files that are finished / approved / obsolete-and-meaningless, move them into
   `archive/` — MOVE ONLY, NEVER delete. Transparently list what moved and why (in the next 13:00
   briefing). See `archive-file-triage` concept (now inlined here).
3. **Pending-review emoji flag.** Scan `06_待多多审核/`; files unapproved >1 day → prefix filename with
   `❗️`; >2 days → `‼️`. Actually `mv`/rename the file (emoji at the very front). See
   `pending-review-emoji-flag` concept (now inlined here).
4. **Update HQ.** Refresh the company HQ status docs (under `公司总部/` — note: do NOT create new docs
   there, only modify existing ones).
5. **Fallback approval detect.** Run `duoduo-approval-detect-and-release` once more, in case a `== ==`
   highlight from the day was missed by the 13:00 pass.

## Known failure modes
| Symptom | Root cause | Fix |
|---|---|---|
| Vault piles up | No nightly archive | Step 2 every night |
| Stale pending files invisible | No emoji flag | Step 3 every night |
| Approval acted on late | Missed during day | Step 5 fallback detect |
| HQ status stale | Not refreshed | Step 4 every night |

## 动作节点（多多能听懂的）
1. 每晚 23:00，再过一遍全天任务，收拾没闭环的。
2. **归档整理**：把已完成/已审批/过期无意义的文件推进 `archive/`（只移不删），并在次日简报透明列出移了什么、为什么。
3. **待审标记**：扫 `06_待多多审核`，超 1 天文件名最前加 ❗️、超 2 天加 ‼️（实际重命名，不止简报说）。
4. 更新公司总部状态文档。
5. 兜底跑一次你的 == == 高亮批复检测，防止白天漏掉。
