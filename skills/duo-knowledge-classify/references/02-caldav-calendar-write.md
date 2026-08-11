# iCloud 日历写入（原 skill: duoduo-caldav-calendar-write）

# duoduo-caldav-calendar-write (加固版 iCloud 日历写入)

This environment cannot use EventKit (sandbox TCC denies calendar access). The only working bridge to
多多's iCloud calendars is **CalDAV**, via the prebuilt tool at `~/.workbuddy/caldav/caldav_tool.py`.

## When to use
- Any "add / move / delete an event in my calendar" request from this agent.
- Any automation that writes calendar events (diary→calendar, weekly plan, time-block rules).

## Hard rules (do NOT skip)
1. **Normalize datetimes.** Always emit basic format `YYYYMMDDTHHMMSS`
   (e.g. `20260723T010000`). iCloud stores the extended form `2026-07-23T01:00` as garbage
   (`20251206`). Never pass extended/hyphenated datetimes.
2. **Proxy off + direct connect.** Before every call, `unset HTTP_PROXY HTTPS_PROXY http_proxy
   https_proxy`. The tool also pops proxies on import (`trust_env=False`), but unsetting is the
   double-safety net. Proxy left on causes intermittent 502.
3. **Retry on 5xx.** If a request returns a 5xx, retry (with backoff) up to 3 times. Do not report
   success on a failed write.
4. **Verify after add.** After adding, read the calendar back for that date range and confirm the
   event exists (`VERIFY: OK`). Only then report completion.
5. **Scoped deletes only.** Deleting an event MUST use `--from/--to` date bounds OR an exact event
   href / exact title match. NEVER a title `contains` with no date guard — that can wipe unrelated
   historical events. Match title + date guard together.
6. **Follow 多多's original calendar color & system.** Use the calendar/color 多多 already designated
   for that category (work=黄, 个人=紫, 美美美/美丽=粉, 个人提升=橙, 探索·旅游=蓝, etc.). Do NOT invent
   new calendars or recolor.
7. **Color-conflict handling.** If the target time slot is already occupied:
   - same color as the existing event → place directly (same category, no conflict).
   - **different color** → STOP and ask 多多 to confirm before placing. Never auto-overwrite a
     different-category event.
8. **1-hour default block.** If the source (journal/todo) has NO explicit time, default the event to a
   **1-hour block** (start at the implied slot, duration 1h) rather than leaving it timeless.

## Tool & credentials
- Tool: `~/.workbuddy/caldav/caldav_tool.py` (run with the managed venv python:
  `/Users/Zhuanz/.workbuddy/binaries/python/envs/default/bin/python`).
- Credentials: `~/.workbuddy/caldav_config.json` (apple_id + app-specific password, perms 600).
  Password is an Apple app-specific password — NEVER write it into any file, log, or memory.
- Confirm exact subcommand flags by running `python caldav_tool.py --help` before first use in a
  session (subcommands seen: `list`, `events --calendar`, `add`, `delete`).

## Reference: known failure modes this skill prevents
| Symptom | Root cause | Fix |
|---|---|---|
| Event time shows wrong date (e.g. 20251206) | Extended datetime format | Use `YYYYMMDDTHHMMSS` |
| Intermittent 502 / connection reset | Proxy intercepting iCloud | `unset` proxies, direct connect |
| Write "succeeds" but event missing | No readback check | Always verify after add |
| Old events deleted by mistake | Unscoped `contains` delete | Always scope by date + exact title |
| Wrong color / new calendar spawned | Ignored 多多's system | Rule 6 — use designated calendar/color |
| Overwrote a different-category event | No conflict check | Rule 7 — different color → ask 多多 |
| Timeless todo lost | No default duration | Rule 8 — 1-hour default block |

## 动作节点（多多能听懂的）
1. 你说"把 X 写进日历"，我先把时间整理成标准格式（年-月-日 时:分:秒），不让 iCloud 把时间存成乱码。
2. 写之前先关掉代理、直连 iCloud，遇 5xx 报错自动重试，不让你白等。
3. 写完后立刻读回来核对"真的写进去了吗"——确认 OK 才向你汇报完成。
4. 删除事件时一定圈定时间范围或精确标题，绝不清空式删除，防止误删你别的历史日程。
5. 按你原来日历的颜色和系统来放（工作黄/个人紫/美丽粉/个人提升橙/探索蓝…）；同一时段若已被占用：**同色直接放，不同色先问你确认**，绝不擅自覆盖别的类别。
6. 日记里没写明确时间的待办，自动填一个 **1 小时块**，不会丢。
7. 工具在我本地 `~/.workbuddy/caldav/`，凭证是 iCloud 应用专用密码（不进任何文件）。
