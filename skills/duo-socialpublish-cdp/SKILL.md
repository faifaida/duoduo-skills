---
name: duo-socialpublish-cdp
description: 多多个人公司「全平台发布助手 + CDP 自动发布」唯一标准技能（Windows 侧第三常设角色）。合并原 duo-publish-assistant（发布岗位规范/配图铁律/启动条件/发布后更新/归因铁律）、duo-socialpublish-cdp（CDP 发布技术/各平台流程/排期）、cdp-chrome-profile-unify（Chrome 持久登录统一），并吸收 duo-wechat 的发布技术参考（微信草稿 API 兜底）与 to_publish 入口契约。当用户说"发布/自动发到各平台/把草稿发出去/扫描 to_publish"且本机已接 web-access 或 CDP 时触发。执行通道 = 本机已登录 Chrome 远程调试端口 + cdp-proxy / Playwright connect_over_cdp。
agent_created: true
---

# duo-socialpublish-cdp — 全平台发布（岗位规范 + CDP 技术封装）

多多 2026-07-31 下达的「发布助手」岗位规范，Windows 侧第三常设角色（与内容运营、产品经理并列）。本技能是「发布」唯一标准入口，合并了三块内容：

1. **岗位规范**（原 `duo-publish-assistant`）：启动条件、配图铁律、铁律速查、发布后文件更新、汇报格式、归因铁律、CDP 只读核验、已知无解点。
2. **CDP 发布技术**（原 `duo-socialpublish-cdp`）：Chrome 调试启动、代理路由、去重检查、各平台发布流程、发布排期模板。
3. **Chrome 持久登录统一**（原 `cdp-chrome-profile-unify`）：用用户真实 profile 启动调试 Chrome，避免反复登录/验证码。

另吸收 `duo-wechat` 的**发布技术参考（微信草稿 API 兜底）** 与 **to_publish 入口契约**（制作侧生成 to_publish 的格式标准，见下方「发布入口契约」）。

规范原文（权威版）：vault `98_Windows_work/03_发布助手/🧷 发布助手_岗位规范_20260731.md`
角色 prompt 原文另存：`~/.workbuddy/AGENTS.md`

---

## 一、日常节律（并入公司节奏，多多 2026-07-31 确认）

- 定时扫描：automation「发布助手扫描 to_publish（10:00/22:00）」每日两次扫 `03 drafts/`，无 to_publish 文件静默结束。
- 与其他角色一样按 `98_Windows_work/_setup/` + Mac 总经办指令走：09:00 自取指令（含 指令_<日期>_发布助手.md）、15:00/21:00 补跑+批复扫描（含 `03_发布助手/` 的 `== ==` 高亮）。
- 汇报文件写 `98_Windows_work/03_发布助手/汇报_<日期>_<主题>.md` 或 `回报_<日期>_执行.md`（带时间戳）。

## 路径（实际，规范原文写法有出入，以此为准）

- 发布入口目录：`E:\iCloudDrive\iCloud~md~obsidian\DuoDuo_AI_Workspace\05_CONTENT\03 drafts\`
- 已发布归档：`...\05_CONTENT\04 Published\`
- 工作文档目录：`...\98_Windows_work\03_发布助手\`

## 发布入口契约（to_publish 文件格式）

制作侧（如 `duo-wechat`）在多多 `== ==` 拍板后，按此契约生成入口文件；本技能只读它、不写它（除追加发布记录）。**格式硬性要求**：

- 文件名：`to_publish_<主题>.md` 文件 **或** `to publish_<主题>/` 文件夹（多多 2026-07-31 明确纠正：文件夹式入口也算，不要因为少了下划线就当不存在）。
- 文件/文件夹状态必须为 `approved` 或"多多已确认"（如 `to publish_播客第二期/` 即被指定为入口）。
- 字段齐全：**标题独立字段** + **正文分行**（`#话题#` 标签一并带）+ **`## 配图` 段列出全部图路径**（相对或绝对路径均可，但素材必须已本地落盘、非 iCloud 占位符，用文件大小验证）+ 明确写出 **平台 + 账号**。
- 无"待确认/待补充"/占位符、无漏字段。
- 不满足 → 停止发布，集中汇报缺失项，不补写不猜测。

---

## 二、启动条件（全部满足才动手）

1. 存在发布入口：`to_publish_*.md` 文件 **或** `to publish_<主题>/` 文件夹。
2. 文件/文件夹状态 `approved` 或"多多已确认"。
3. 文案/素材路径完整、素材已本地落盘（非 iCloud 占位符，用文件大小验证）。
4. 明确写出平台 + 账号。
4.5. 🔴 **发布前必须「实测当前登录账号」而非只看登录态**：导航到创作后台后，**抓取账号昵称/头像确认是哪个号**。URL 无 `login` ≠ 账号正确——0810 实测小红书已登录但登的是 `DUODUOWEAR 泳衣号`（品牌号），若发 EP01 个人内容即违反护栏错配；视频号则完全未登录停在 login 页。账号与 `to_publish` 目标不一致 → 直接 blocked，绝不硬发、绝不"先用当前号发"。
5. 无"待确认/待补充"/占位符。
不满足 → 停止，集中汇报缺失项，不补写不猜测。

## 🔴 配图铁律（多多 2026-08-04 明确，最高优先级）

**发布必须带图。裸文本发出 = 发布失败，禁止标 published、禁止移入 04 Published。**

- 草稿 `## 配图` 段列出的图**必须全部挂上**，一张都不能漏。
- 正文以草稿原文为准，**`#话题#` 标签一起带**；只有平台硬上限（X 280 字符）才允许压缩，且必须在发布记录里写明「原稿 N 字超限，压缩至 M 字」。
- 核验双条件：**文本命中 且 图片数 ≥ 草稿配图数**，两者都过才算成功。
- ⚠️ 核验图片时**必须排除头像**：判据 `img.closest('[class*=avatar i]')`。微博头像 naturalWidth=1024，只按尺寸过滤会把头像误计成配图，造成"有图"的假阳性。

### 实测挂图路径（工具库 `deliverables/pub_lib.py`）

- **file input 是懒加载的 —— 必须先点开 composer 编辑器，再找 `input[type=file]`。**
  实测：即刻不点编辑器 = 0 个 input，点开后 = 1 个。这是漏图的头号原因。
- 微博：composer 有隐藏 `input[type=file]`，`accept=image/*`、`multiple=true`，`set_input_files(paths)` 直传成功。
- 找不到 input 时兜底：`expect_file_chooser` + 点「图片」按钮/媒体图标。
- 挂图后 sleep `4 + 2×张数` 秒等上传完成，再点发送。

### 教训（2026-08-04 事故）

0804 五平台（微博/知识星球/即刻/Threads/X）全部裸文本发出，草稿明明每篇都指定了配图 `2025.10 油化厂生日&青旅logo.JPG`，微博的 `#家族二代#` 等 4 个话题标签也漏了。根因：调试发送按钮时用简化脚本（直接 set textarea value + 点发送）绕过了完整流程，把「让按钮能点」当成了「发布成功」。
**规避：任何时候都用 `pub_lib.publish()` 完整流程发，不允许为了调试临时写简化脚本直接发出去。**

## 铁律速查

- 只发文件 `platforms` 列出的平台，不因已登录就顺手同步别的平台。
- 不重写文案、不改素材、不自行定时间/加平台/删旧内容；只做格式级调整（换行/去不支持格式/用文件给的短版）。
- 发布前四查重：文件内已有链接？发布日志已成功？账号主页已存在？标题封面时长高度相似？疑似重复即停。
- 点击发布 ≠ 完成：必须刷新进主页/内容管理页确认真实存在 + 打开检查 + 记录链接和时间。
- 无法核验时写死这句：「已提交发布，但尚未验证真实上线，因此不计为发布成功。」
- 给多多确认用预览图（截图），不要只文字形容。
- 异常（登录失效/验证码/违规提示/截断/转码异常/疑似已发/按钮不可用）→ 立即停该平台，汇报：平台+进度+实际提示+是否可能已发布+建议；未经确认不删除不重发不换号。

## 浏览器界定（多多 2026-07-31 确认）

**CDP 调试模式 Chrome = 合规通道**（正式账号+持久登录态，仅启动方式带调试端口），不属于禁止的 Test Chrome。各平台具体操作细节见下方「五、各平台发布流程」。
禁止：临时浏览器、测试账号、新建浏览器用户、未确认的第三方工具；不退出账号不改密码。

---

## 三、前置：启动带调试端口的 Chrome（持久登录态关键）

Chrome 拒绝在**默认 User Data 目录**上开远程调试。用 junction 指向同一份配置即可骗过校验，且登录态原样保留：

```
# 只需建一次
mklink /J "C:/Users/Administrator/AppData/Local/Google/Chrome/User Data Debug" "C:/Users/Administrator/AppData/Local/Google/Chrome/User Data"
# 启动（端口避开 wrangler 占用的 9229，用 9222）
start "" "C:/Program Files/Google/Chrome/Application/chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:/Users/Administrator/AppData/Local/Google/Chrome/User Data Debug" --no-first-run
```

- **cookie 持久化 = 用户只需登录一次，之后数月免扫码/验证码**（微信系首次需手机扫码）。这是"以后不需要验证码"的核心。
- 代理连接（每次改 cdp-proxy 后需重启）：PowerShell 精确 `Stop-Process` cdp-proxy.mjs → `node check-deps.mjs`。

### 🔴 绝对禁止：`taskkill /F /IM chrome.exe`（2026-08-05 血的教训）

强杀 Chrome 会**把未落盘的 session cookie 全部丢掉** —— 那次直接把小宇宙主播后台登录态干掉了，被迫重登。
- ✅ 正确关法：`Get-Process chrome | ForEach-Object { $_.CloseMainWindow() }` → `Start-Sleep 8` → 再检查残留。
- ✅ 更好：**根本不要关**。要改 Chrome 启动参数就新开一个独立 `--user-data-dir` 实例，别动用户日常那个。
- 换端口重启后 `DevToolsActivePort` 文件仍是**旧值**，`check-deps.mjs` 会找不到浏览器。此时直接用 **Playwright `connect_over_cdp("http://127.0.0.1:9222")`** 绕过代理，比修文件快且能力更全。

### 代理与大文件上传（音视频必看）

系统全局代理（本机 Clash `127.0.0.1:7897`）会**把七牛/OSS 分片上传拖死** —— 实测小宇宙 16.9MB 音频，5 个分片跑满 340s 全部超时，进度条从 74% 回退到 35% 再卡死。
- 判据：`performance.getEntriesByType('resource')` 里 `upload.qiniup.com` 请求 `duration` 数十万 ms。
- 修：Chrome 启动加 `--proxy-bypass-list=*.qiniup.com;*.qiniu.com;*.qbox.me;*.xiaoyuzhoufm.com;localhost;127.0.0.1`。
- 注意：`Start-Process` 时若旧 Chrome 没真正退出，新参数**不会生效**（会复用旧实例）。必须先确认进程数归零，再核对 `CommandLine -like '*proxy-bypass-list*'`。

### 启动调试 Chrome 实战坑（2026-08-10 实测）

- 🔴 **别用 `cmd //c start "..." chrome.exe ...` 在 Git Bash 里启动**：引号会被 Git Bash 解析弄坏，Chrome 根本起不来且静默失败。改用 **PowerShell `Start-Process` + `-ArgumentList @(...)` 数组**传参，引号可靠（见四-B 修复步骤的 PowerShell 写法）。
- **同 profile 已存在调试实例 → 新端口参数被忽略**：若 9222 没起来，先 `Get-CimInstance Win32_Process -Filter "Name='chrome.exe'"` 查是否有别的调试口实例（如遗留无头 `9333` 占用 `User Data PubDebug`），精准 `Stop-Process -Id <pid> -Force` 那个，**绝不用 `taskkill /F /IM chrome.exe` blanket 强杀**（丢 cookie）。再优雅关闭真实 Chrome（`CloseMainWindow`）释放 profile 锁，最后用真实 profile + 9222 重启有头实例。
- **工具链**：managed Python 默认没装 playwright → 直接 `python -m pip install playwright`（`connect_over_cdp` 不需要下载浏览器内核）。Node 的 playwright 在 `connectOverCDP` 后 `browser.contexts[0]` 可能为空（版本兼容问题）→ 一律走 **Python `connect_over_cdp("http://127.0.0.1:9222")` + `contexts[0]`** 这条已验证路径。
- ⚠️ **用户在占用浏览器时 CDP 会连不上**：真人在手动操作时 `connect_over_cdp` 会 ws 连上但握手超时（180s）。这是"用户在忙"的信号——**不要硬连、不要重试抢浏览器**，先问用户是否手动发完，或等浏览器空闲再接。

### 本机 Bash 环境缺 coreutils

Git Bash 里 **没有 `nohup` / `tee` / `sleep`**。后台跑脚本用 `run_in_background` 参数 + `> log 2>&1` 重定向；要等待就用 `python -c "import time;time.sleep(N)"`。

---

## 三-C、Quark（夸克）发布浏览器 —— duoduo wear 品牌号专用（2026-08-10 定 + 实战）

**分工铁律**：`9222` = Chrome（多多OS 个人号）；`9223` = Quark（**duoduo wear 品牌号**：小红书 / 抖音 / 视频号）。两浏览器登录态不互通，绝混用，防 EP01 那种账号错配（小红书/视频号曾误登成 DUODUOWEAR 品牌号）。

- 安装：`C:\Users\Administrator\AppData\Local\Programs\Quark\quark.exe`（Chromium 144 内核）。
- 持久 profile：`C:\Users\Administrator\AppData\Local\Quark\User Data Publish`（扫码登录一次后 cookie 落盘，后续免登）。

### 🔴 启动命令（少了 flag 就废）

```powershell
Start-Process "C:\Users\Administrator\AppData\Local\Programs\Quark\quark.exe" `
  -ArgumentList "--remote-debugging-port=9223", `
                 "--remote-allow-origins=*", `
                 "--user-data-dir=C:\Users\Administrator\AppData\Local\Quark\User Data Publish", `
                 "--no-first-run", "--no-default-browser-check", "--no-proxy-server"
```

- ⚠️ **`--remote-allow-origins=*` 必带**：夸克默认拒绝非同源 ws 连接，缺它 CDP websocket 直接 `403 Forbidden`（Playwright 则表现为 `connect_over_cdp` 卡死无报错）。这个 flag 必须在**首次启动**就加上——之后想补就只能关掉重开（会丢未落盘登录态）。
- `--no-proxy-server`：93MB 视频上传绕开 Clash，避免分片卡死。

### ⚠️ Playwright `connect_over_cdp` 对夸克会卡死

实测：连夸克 9223 时 `connect_over_cdp("http://127.0.0.1:9223")` 直接挂起（ws 连上但 handshake 无返回，180s 超时）。**改用原生 CDP over websocket**（依赖 `websocket-client` 库，`pip install websocket-client`）：

```python
import json, urllib.request, websocket
ver = json.loads(urllib.request.urlopen("http://127.0.0.1:9223/json/version", timeout=5).read())
ws = websocket.create_connection(ver["webSocketDebuggerUrl"], timeout=15)  # 现在 allow-origins=* 可通过
# 建页→挂到目标→截图/取文本
r = send("Target.createTarget", {"url": url})
r = send("Target.attachToTarget", {"targetId": r["targetId"], "flatten": True}); sid = r["sessionId"]
send("Page.enable", {}, sid)
send("Page.navigate", {"url": url}, sid)
time.sleep(6)
shot = send("Page.captureScreenshot", {"format": "png"}, sid)["data"]   # base64
txt  = send("Runtime.evaluate", {"expression":"document.body.innerText","returnByValue":True}, sid)["result"]["value"]
```

- 本项目已落地脚本：`03_发布助手/_quark_cdp.py`（通用三平台探测）、`_quark_verify_login.py`（登录态+账号名核验）、`_quark_douyin.py`（抖音单列重查，SPA 渲染慢需等 12s）。
- 登录态核验范式：导航到创作后台后**抓账号昵称**（如 `DUODUO WEAR泳衣` / `DUODUOWEAR`），确认是品牌号而非 多多OS/世斐；URL 无 `login` ≠ 账号正确（见二·4.5）。

### 已知坑

- 抖音创作后台是 SPA，`document.body.innerText` 常常空/不全 → 等待 ≥12s 再抓，且用 `creator-micro/home` 落地页判登录。
- 夸克与 Chrome 启动参数坑同源：同 profile 已存在实例时新参数被忽略，需先确认进程归零。
- 别 blanket 强杀 quark.exe（丢 cookie）；要重启先 `Get-Process quark | Stop-Process -Force`（仅我启的自动化实例，非用户默认 Chrome）。

## 四、Chrome 持久登录统一（原 cdp-chrome-profile-unify）

### 触发场景

- 用户说"怎么又要登录/扫码/验证码"，或"想办法永久登录"。
- 用 CDP（端口 9222）做批量发布时，平台反复要求重新登录。
- 发现用户已经在自己浏览器登录，但机器人仍显示未登录。

### 根因

CDP 机器人通常启动在独立的 Chrome profile（如 `User Data AutoDebug`）。用户日常用的是默认 profile（`User Data/Default`）。两个 profile 的 cookie、localStorage、登录态完全隔离。用户在自己浏览器登录 ≠ 机器人在其 profile 中登录。

### 诊断步骤

1. 连上调试端口，列出 Chrome 进程命令行，确认当前机器人在用哪个 profile。
2. 检查用户日常 Chrome 的 profile 路径与 Cookies 数据库修改时间（`User Data/Default/Network/Cookies`）。
3. 对目标平台分别导航到登录门控页（创作后台 / home / compose），读取最终 URL 与页面文本：
   - URL 含 `login`、`signin`、`oauth`、`passport` 或 body 出现登录关键词 → 未登录。
   - 否则视为已登录。
4. 若用户日常 profile 里有登录态但机器人 profile 没有 → 需要统一 profile。

### 修复步骤（DPAPI-free，推荐）

1. 关闭全部 Chrome 进程（包括机器人和用户的 Chrome），确保默认 profile 的 `SingletonLock` 释放。
2. 用用户真实 Default profile 重启 Chrome，并开启调试端口：
   ```powershell
   Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" `
     -ArgumentList "--remote-debugging-port=9222", `
                   "--user-data-dir=C:/Users/<User>/AppData/Local/Google/Chrome/User Data", `
                   "--no-first-run", "--no-default-browser-check", "--restore-last-session"
   ```
3. 验证 `http://localhost:9222/json/version` 响应，并导航到各平台门控页再次确认登录态。
4. 机器人后续所有 CDP 脚本均连接 `localhost:9222`，直接复用用户真实会话。

### 注意事项

- 不要在命令行中混用 `~` 或空格导致 profile 路径被截断；用绝对路径并加引号。
- 如果用户有多个 profile，需用 `--profile-directory=Profile N` 指定；通常无此参数时启动的是 `Default`。
- 强制关闭 Chrome 后再启动 `--restore-last-session` 不一定能恢复标签页；提前告知用户。
- 微信公众号群发仍触发微信"风险操作保护"扫码，这是平台强制，统一 profile 后依然存在。
- 若安全环境禁止直接读取 `CryptProtectData` / DPAPI 解密 cookie DB，此"重启统一 profile"方案是唯一不依赖 DPAPI 的解法。

---

## 四-B、多账号登录地图（2026-08-07 新增 · 铁律级）

> **一个平台多个号，必须按账号分别记住登录态与切换方法。** 完整 canonical 矩阵见项目记忆 `<workspace>/.workbuddy/memory/账号登录地图.md`（每次发布前必查）。

- 🔴 **铁律**：绝不要求多多手动登录/扫码。视频号多多 2026-08-07 确认已登 = **DUODUOWEAR 品牌号（9222）**，可直接发。
- **本机架构**：`9222` = 默认 profile 品牌集群（小红书 duoduo wear / IG duoduo_wear / 视频号 DUODUOWEAR 均✅，可直控，绕过 cdp-proxy 用 `/json/new` + `t9222_*.py`）；`10308`(端口 56641) = 微信扫码类登录态但 DevTools 不可达、cdp-proxy `/new` 僵死 → 不可自动化，且**不可重启**（丢态）。
- **多账号切换 SOP**：① 从 `to_publish_*.md` 读出目标平台+账号 → ② 实测 9222 当前登录的号（`probe_min.py`）→ ③ 已是目标号直接发 → ④ 不是则：凭证平台用 vault 凭证自助切号、微信扫码平台请多多在 **9222** 扫对应微信 → ⑤ 发完核验+记录+改 published+移 `04 Published/`。
- **品牌护栏**：发 duoduo wear 内容前必须确认 9222 小红书 = duoduo wear 号，否则违反护栏。
- **微信系**（视频号/公众号/小宇宙）：同一微信下多号可下拉切换无需重扫；不同微信需重扫。
- **凭证**一律从 vault `03_ACTIVE PROJECTS/ai个人公司/公司档案/00_共享公司资料/00_凭证_passwords.md` 读取，绝不打印到回复。
- **已知技术坑**：① 小红书 `XHS-PUBLISH-BTN` 普通 JS click 无效，但 `el._onPublish()` 有效；② 视频号上传页用 **Wujie(无界) Shadow DOM**，CDP 文件注入受限，待试 Wujie 真实 `<iframe>` → `Target.attachToTarget(flatten)` 拿 iframe session 后 `DOM.setFileInputFiles`；③ 小宇宙上传须 `/activate` 保前台。

---

## 五、代理路由（cdp-proxy.mjs 需含这些；本机已加）

- `/new?body=URL` 开页 · `/navigate` 导航 · `/targets` 列页 · `/activate?target=` 调前台（**后台 tab 坐标点击会失效，必须先 activate**）
- `/eval?target=` 跑 JS · `/clickXY?target=&x=&y=` 坐标真实鼠标 · `/type?target=` CDP `Input.insertText`（受信任逐段输入）
- `/keys`(paste/ctrlEnter/逐字符) · `/grantclip`(clipboardReadWrite) · `/setFiles`(文件上传) · `/screenshot`

## ⚠️ 发布前必做：去重检查（多多 2026-07-30 铁律）

每次发布前**必须**先查目标账号近期已发内容，确认本次内容未重复，避免多发/重发。
- 方法：到目标账号个人主页/动态页，用 `/eval` 取 `document.body.innerText`（或 recent posts 文本），检查是否含本次内容的关键句（如 C5 的「青旅开业 / 半离职 / AI个人公司 / 多多的未完成实验」）。
- 含 → 跳过本次发布，报告「已存在，跳过」。
- 不含 → 继续发布；发完再回主页确认「真的出现」才算完成（验证铁律）。
- ⚠️ `/eval` 里的**中文正则会被传输编码弄坏**（匹配失效）。应对：① 用非中文过滤（如 `(x.innerText||"").trim().length>0` 找发送按钮）；② 或让 eval 返回原始文本，在 Bash/Python 侧用 `in` 判断中文关键词。

---

## 六、各平台发布情况 / 注意事项 / 流程（核心）

### 公众号（ProseMirror）
- **状态**：✅ 文本注入可用；❌ 封面图强制必填、UI 较脆。
- **方法**：聚焦 `.rich_media_content .ProseMirror`（正文）或 `.title-editor__input .ProseMirror`（标题）→ `document.createRange` 设光标到末尾 → 代理 `/type` 整段 `Input.insertText`。正文/标题都能实写。
- **验证**：发后去草稿箱/已发送确认。
- **注意**：微信系首次需手机扫码登录；title 同名「公众号」易误判登录态，要看"请重新登录"/明确登录墙信号。

#### 🧷 封面自动化（2026-08-05 实测打通｜多多确认手机已见草稿并发出 —— **照抄这套，别再另起炉灶**）

前提：正文里已插入过图片（封面从正文图中选）。用 **Playwright `launch_persistent_context`**（不是 CDP 代理），profile = `chrome_profile_copy`。

**成功链路（cv10 方案，5 步）**
1. `page.hover('.select-cover__btn.js_cover_btn_area')` —— **必须先 hover**，下拉才渲染出「从正文选择 / 从图片库选择 / 微信扫码上传 / AI 配图」。
2. 用 `rect()` 取 **`a.js_selectCoverFromContent` 的可见坐标**，再 `page.mouse.click(x, y)`。
3. 弹窗出现（标题「选择图片　请从正文插入的图片和视频封面中选择封面」）→ 枚举 `span.appmsg_content_img.cover`（115×115，靠 background-image 渲染）→ 取第一张坐标 `page.mouse.click()`。
4. 点「下一步」→ 进裁剪 → 点「确认」。
5. 核验：`getComputedStyle(coverBtn).backgroundImage` 应变为 `url("https://mmbiz.qpic.cn/mmbiz_jpg/.../0?wx_fmt=jpeg")`，最终封面 **900×382**（竖图原图被自动裁成横封面，属正常）。然后「保存为草稿」。

**为什么必须坐标点击（踩过的坑，别重犯）**
- ❌ `page.click('a.js_selectCoverFromContent')` → **strict mode violation**（该 selector 匹配 3 个元素）。
- ❌ `evaluate(() => el.click())` 点隐藏 LI → 弹窗根本不开（微信依赖真实鼠标事件链）。
- ❌ 按文字精确匹配「从正文选择」→ 菜单实际文案是「从正文选择可选视频封面」，找不到。
- ✅ 只有「hover 触发菜单 → `rect()` 可见坐标 → `mouse.click()`」这条路稳。

**发表环节**：点「发表」会触发**手机扫码安全验证**，AI 无法代操作（群发不可撤回）。自动化做到「封面已设 + 保存草稿」为止，剩下让多多手机确认发出。脚本末尾要 `time.sleep()` 挂住浏览器别关。

**Chrome 单例锁**：`launch_persistent_context` 报 `TargetClosedError / Target page closed` = 残留 chrome 占着 profile。修：PowerShell 按命令行含 `chrome_profile_copy` 过滤 → `Stop-Process -Force`，再 `rm -f <profile>/Singleton*`。

### X / Twitter（@faifaida1，Draft.js）
- **状态**：✅ 已验证可发（2026-07-30 C5 成功发出，主页第 4 条、C5 置顶）。
- **方法**：`/activate` → `/clickAt` 聚焦 `[aria-label="Post text"]` → `/keys` 逐字符注入（**不要用 `Input.insertText`，只进 1 字符、Post 持续 disabled**）→ `/clickAt` 点 `button[data-testid="tweetButtonInline"]`（真实鼠标）。
- **验证**：个人主页 `tweetText` 出现即成功；`statuses_count` +1。
- **注意**：Post 按钮在编辑器为空/未聚焦时 disabled；必须先聚焦再注入。

### 即刻（多多OS，contentEditable）
- **状态**：✅ 已验证可发（2026-07-30 C5 成功，主页顶部「刚刚」帖子）。
- **方法**：`/activate` → `/clickAt` 第一个 `[contenteditable=true]`（**确认 parent 是 `_form`/`content-editor`**，feed 内帖子也有 contentEditable 要避开）→ `/keys` 注入（可带 `{"text":...,"clear":true}` 先清空）→ 点「发送」按钮（`/clickAt` 或 `/clickXY`，坐标为视口坐标）。
- **验证**：发送后编辑器清空 = 成功信号；个人主页顶部出现「刚刚」帖子即证。
- **注意**：发送按钮中文匹配在 eval 里易编码损坏 → 用非中文过滤（如 `innerText.trim().length>0`）找按钮，用 Python 解析坐标。

### 小红书（多多OS 账号 95470336324）—— ✅ 已打通，但内容审核有坑
- **状态**：✅ 账号已进调试 Chrome（多多OS / 95470336324），已绑手机，发布链路跑通；⚠️ 2026-07-30 C5 发布后被平台判「未通过」（原因：正文引导用户去「公众号《多多的未完成实验》」，被认定为「推广第三方平台」）。
- **登录关键坑**：多多说"已在小红书智能助手登录 多多OS"，但登录发生在**另一只会话**（用户自己的 Chrome 或手机 App），自动化用的「带调试栏的 Chrome」看不到该登录态。`creator.xiaohongshu.com` 与 `www.xiaohongshu.com` 同浏览器共享 cookie。必须让 多多OS 会话落到**带调试栏的 Chrome**（手动登一次或给手机号+验证码驱动登），以后持久免扫码。
- **发布流程（图文笔记）**：
  1. `/navigate` 到 `https://creator.xiaohongshu.com/publish/publish`
  2. 点顶部「上传图文」标签（x≈433, y≈101；当前默认在「上传视频」）
  3. `/setFiles` 给 `input.upload-input` 传本地图片（accept: jpg/jpeg/png/webp）
  4. 编辑器加载后：标题框是 `input.d-text`（placeholder「填写标题会有更多赞哦」）；正文是 `.tiptap.ProseMirror` contentEditable
  5. 标题/正文都用代理 `/type`（`Input.insertText`）注入；**必须用 Python 直接 POST JSON，避免 shell/curl 中文编码损坏标题**
  6. 标签建议直接以 `#话题` 形式写在正文末尾，小红书会自动尝试关联
  7. **提交**：页面底部是自定义组件 `<xhs-publish-btn>`，常规 `/clickXY` 与 JS `.click()` 均无效；要直接调 `document.querySelector("xhs-publish-btn")._onPublish()`
  8. 发后去「笔记管理」确认状态：通过则出现在「已发布」；若进「未通过」则看「查看修改建议」里的具体原因
- **内容审核雷区（2026-07-30 实测）**：
  - 正文/图片/标题出现「公众号 / 微信 / 加微信 / 站外搜索 / 去某平台看完整版」等引导第三方平台的表述，极易被判定「推广第三方平台」→ 笔记「未通过」、流量受限。
  - 泳衣/泳装/身体暴露类图片也容易被判违规（C5 本次用图为海边泳装照，是潜在风险项）。
- **注意**：小红书对自动化检测严格，有封禁风险；除 `<xhs-publish-btn>` 必须 JS 调方法外，其余点击尽量走真实鼠标（`/clickAt` / `/clickXY`）。

### 小宇宙（播客 · 账号「多多的未完成实验」）—— ✅ 已打通 web 自动发布（EP04 实测 2026-08-11）
- **状态**：✅ 2026-08-11 用 `podcast_publish.py` 把 **EP04** 实测发布成功（公开页 `https://www.xiaoyuzhoufm.com/episode/6a7a486717676351c56fdd0f` 已含封面+shownotes，列表页出现标题，WebFetch 独立核验通过）。调试 Chrome 经「即刻 SSO」已登录。
- **🔑 登录关键认知（重要，曾误判）**：小宇宙主播后台 `podcaster.xiaoyuzhoufm.com` **没有独立密码登录**，它用**即刻（Jike）SSO**。调试 Chrome 里只要持有 `x-jike-access-token` / `x-jike-refresh-token`（即刻登录态），小宇宙就直接是登录态——**不要去 cookie 里找「xiaoyuzhou」字样的登录 cookie**（根本没有），应直接访问 `podcaster.xiaoyuzhoufm.com/podcast` 看是否出现节目名判断。若 Jike token 丢失/跳登录墙，无法脚本自动登录（需即刻 App 扫码），此时只能报人工。
- **入口链路**：`studio.xiaoyuzhoufm.com/` → 点「主播后台」→ `podcaster.xiaoyuzhoufm.com/podcast` → 节目 `6a5a306305d4bfbabc3ea16b` → 内容管理 →「创建单集」→ `podcaster.xiaoyuzhoufm.com/podcast/6a5a306305d4bfbabc3ea16b/episode/create`
- **🔴 技术栈铁律**：小宇宙音频/封面上传走**七牛分片**，对代理极敏感，调试 Chrome **必须 `--no-proxy-server` 直连 `:9222`**（见三·代理与大文件上传）。用 cdp-proxy(`localhost:3456`) 能力残缺且七牛会被拖死，**一律走直连 `127.0.0.1:9222` + `websocket-client`**（即 `podcast_publish.py` 路径），不要走 `/setFiles` 代理通道。
- **实战发布流程（EP04 实测通过，照抄 `podcast_publish.py`）**：
  1. 连 `:9222` → `Target.createTarget`(create 页) → `attachToTarget(flatten)` → 开 `Page/Runtime/DOM` enable → **`Page.setInterceptFileChooserDialog({enabled:true})`**（关键：音频/封面 input 是点击才弹原生文件框，需拦截）。
  2. 标题：`input[placeholder="输入单集标题"]`，用原生 value setter（`Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set`）赋值 + dispatch `input`，**勿用 `Input.insertText` 逐字符**（受控组件不认）。
  3. 简介：`.tiptap.ProseMirror` 直接 `innerHTML='<p>...</p>'` + dispatch `input`（ProseMirror 认 innerHTML，比逐段 `/type` 稳）。
  4. **音频（懒加载）**：真实鼠标（`Input.dispatchMouseEvent`）点「点击上传播客」区 → 等 `Page.fileChooserOpened` 事件 → `DOM.getDocument` → `DOM.querySelector('input[type=file][accept*="audio"]')` → `DOM.setFileInputFiles({files:[audio]})`。**直接 `DOM.setFileInputFiles` 无效，必须先点出 chooser 再喂**——这是上传成功的关键。
  5. **就绪判据**：轮询直到音频区出现时长 `mm:ss` 且 `sec>=30`（正则 `音频[\s\S]{0,8}?(\d{1,2}):(\d{2})`），且「创建」按钮 `disabled=false`。⚠️ 只查 `div,span,p,li`（**勿遍历 `*`**，会被 `<style>` 里的 CSS `%` 污染匹配），且**必须 `sec>=30`**（否则会误匹配播放器的 `00:00` 假就绪，导致提前点创建失败）。
  6. 封面（best-effort）：点「单集封面/封面/上传封面」区 → 拦截 chooser → `DOM.setFileInputFiles` 喂图。**上传后封面自动保存（预览 img 出现 `image.xyzcdn.net` 真实 URL 即已落盘）**，编辑页「更新」按钮全程 disabled 是**红鲱鱼，无需点击**。
  7. **🔴 勾「阅读并同意」checkbox（2026-08-11 血泪）**：发布前**必须**勾选协议 checkbox。它是 Mantine checkbox，**不是**页面上那个 Mantine Switch——要用 `ancestorText`（向上 6 层祖先拼文本）正则匹配「阅读并同意/同意《/服务协议/协议」再 `c.click()`。**不勾 → 点「创建」毫无反应，URL 停在 `/episode/create`，发布静默失败。**
  8. **点「创建」**：真实鼠标点「创建」按钮 → **直接导航到 `/episode/{id}/stats` 即发布成功，无二级确认 modal**。技能旧文写的「立即发布」按钮 / 二次确认弹窗**已过期**（2026-08-11 实测不存在）。
- **已落地发布器（推荐直接用，EP04 验证）**：`98_Windows_work/03_发布助手/podcast_publish.py`（通用，解析 `To publish_播客*` 包里的 `*_TO_PUBLISH_*.md`）。
  - `python podcast_publish.py --dry-run --package "<To publish_播客第X期>"`：只解析+填标题简介，不传音频不发布（自检）。
  - `python podcast_publish.py --package "<To publish_播客第X期>"`：完整上传音频+封面+简介 → 点创建 → 列表核验 → 写回 PUBLISHED + 发布记录 + 移 `04 Published/`。
  - `python podcast_publish.py --scan`：扫描 `03 drafts/To publish_播客*` 下所有未发布包自动发。
  - ⚠️ 旧 `xiaoyuzhou_upload.py`（cdp-proxy + 「立即发布」按钮写法）**已失效，勿再用**，仅留作参考。
- **验证（权威判据）**：
  - 发布后 URL 出现 `/episode/{id}/stats` = 已落库；
  - 再开 `.../episode` 列表页，`document.body.innerText.includes(标题)` = 真发布；
  - **公开单集页正确域名 = `https://www.xiaoyuzhoufm.com/episode/{id}`**（`podcaster.../episode/{id}` 是 404，别用错域名误判「页面不存在」）。
  - 可用 **WebFetch 抓公开页做独立核验**——CDP 在用户占用浏览器时会被 throttle（`evaluate` 全返回 `None`），此时**改信 WebFetch**，不要反复硬连 9222。
- **注意**：小宇宙是播客同步体系的**源头**——喜马拉雅 / Apple Podcasts / 网易云 等从小宇宙 RSS 自动同步，所以 EP 必须**先上小宇宙**，其余平台自动跟上，无需手动发。

### 视频号助手（channels.weixin.qq.com）
- **状态**：tab 存在，但视频发布本次未做（用户指令：视频还没好，先不发）。
- **注意**：视频上传/发布链路较长，建议视频就绪后用真实鼠标逐步操作，发前确认登录态。

### 公众号发布技术兜底：微信草稿 API（curl，仅当 CDP 不可用时）

主路径（本项目）：本技能 CDP 自动发布。render→PNG 后由 Windows 发布助手按 `03 drafts/to_publish_*.md` 执行，点击后主页核验 + 记链接 + 状态改 published + 移 `04 Published/`。

兜底路径（改自原 `duo-wechat` / `jvs-wechat-article-publisher`，仅 CDP 不可用时的技术兜底）：
```bash
# 1. 取 token（有效期2小时，每次重新取）
TOKEN=$(curl -s "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=SECRET" | python3 -c "import sys,json;print(json.load(sys.stdin).get('access_token',''))")
# 2. 传封面图
COVER=$(curl -s -X POST "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=$TOKEN&type=image" -F "media=@封面_900x383.png" | python3 -c "import sys,json;print(json.load(sys.stdin).get('media_id',''))")
# 3. 建草稿（必须 charset=utf-8，否则中文乱码）
curl -s -X POST "https://api.weixin.qq.com/cgi-bin/draft/add?access_token=$TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d "{\"articles\":[{\"title\":\"标题\",\"content\":\"<p>正文HTML</p>\",\"thumb_media_id\":\"$COVER\"}]}"
```
⚠️ **防乱码四必须**：① 每次重取 token；② `-H "Content-Type: application/json; charset=utf-8"`；③ 用 curl 不用 Python requests；④ 手机扫码预览核验。
⚠️ 本项目正文是**长图 PNG**（非富文本 HTML），故草稿 API 仅适合纯文字补充场景；长图一律走 CDP 图文草稿上传。

---

## 七、发布流程模板（通用）

1. `/activate` 目标 tab
2. **发布前去重检查**（铁律）
3. 确认登录态（探 DOM 登录墙 + URL 是否含 login/signin）
4. 聚焦编辑器 + `/type` 或 `/keys` 注入标题/正文
5. 处理封面/配图（必填项）
6. 点「发表/发送」（先 `/activate` 再 `/clickXY` 真实鼠标，别用 JS `.click()`）
7. 处理确认弹窗
8. 去个人主页/草稿箱验证**真的发出去了**（不凭"编辑器清空"判成功；小红书以编辑器清空为准，X/即刻以主页出现为准）

## 踩坑备忘（本机实测，2026-07-30）

- **后台 tab 必须先 `/activate` 再 `/eval`/`/clickXY`**：否则返回空（throttle），坐标点击失效。
- **代理返回 JSON 带转义引号**（`{\"x\":1085}`），用 `sed` 取坐标会失败；用 Python `json.loads(d['value'])` 解析后再取 x/y。
- **中文在 eval 代码里易编码损坏**：中文从页面取回显示正常，但写在 eval 代码里做匹配会失效。涉及中文判断一律放到 Bash/Python 侧。
- **小红书账号会话必须在「带调试栏的 Chrome」内**，用户在别的浏览器/手机登录不会同步过来（已栽过一次）。
- **微信系 title 也喊"公众号"**，易误判登录态；看"请重新登录"/明确登录墙信号。

---

## 八、发布排期（canonical 模板 · 每周复用）

排期是发布的总输入。

### 🔴 计划时点与窗口（多多 2026-08-07 纠正）
- **计划时点**：每周四拍「下周一–周日」排期（不是周五）。
- **窗口**：下周一 → 下周日，共 7 天（不是「本周五→下周五」8 天）。
- **页面架构（2026-08-07 终局定论 · 单文件）**：**唯一排期 html = `05_CONTENT/发布排期.html`**（单文件内含：主页概览 + 单列分周频次核对 + 历史周段 + 本周段 + 下周段；每周段 = 每日预览 + 段底「计划 vs SOP 一致性」表）。**不再另起主页/每周单独页、不再合并成多文件**——「主页 + 每周单独页面」的旧写法已废弃。历史排期若需保留，作为单文件里的「历史周段」存在，**绝不另开文件**。

### 🔴 强制前置核验步骤（用户 2026-08-07 铁律，排期前必做，否则禁止编造）
生成排期前，先完成两轮核对，无依据者一律不臆造：
1. **核对本周已发布情况**：对照实际已发（主页「本周已发布核对框」+ 平台主页核验），标记真「已发 / 待发 / 漏发」。
2. **核对 drafts 真实日期**：扫 `05_CONTENT/03 drafts/` 下 `to_publish_*.md` 与 `to publish_<主题>/` 文件夹，提取已标好的**公众号 / 播客 / 视频**真实发布日期+标题+第几期（这是唯一真值源）。
3. **无依据处理**：凡 drafts 无日期、无标题、或根本不存在的条目 → 先按「无排期 / 无标题」排入，**红色标 `⚠ 待确认`**，集中汇总交多多确认。**绝不凭空编 EP 编号、日期或标题**（曾发生把播客编成 EP05–08、视频编成 EP05–08 的事故）。

### 模板与源真值
**结构与格式以 `duo-content-weekly-workflow` 技能 §二/§三 的单文件规范为准**（单文件 `05_CONTENT/发布排期.html`，滚动窗口在文件内做；不再使用独立的 `schedule-template.html`——该模板概念已废弃，统一走工作流技能）。

源真值（需保持一致）：
  - 工作区副本（唯一圣经）：`05_CONTENT/发布排期.html`（单文件，桌面 `.url` 与 `.lnk` 双入口同指；内容运营 + 发布助手均可见）
  - 网站看板：`faifaida/duoduo-os` 仓库 `app/board/board.html.ts`（构建后渲染于 faifaida.com/board，TAKE SOMETHING 标签有「发布看板」入口）——同步时按单文件排期重刷，不要带编造数据
  - 频次依据（SOP 周频次）：见 `duo-content-weekly-workflow` 技能 §四「SOP 周频次参考表」（已嵌确认值）；或本单文件 tally 表的「SOP 周频次」列（即工作参考源）。原 `Human3_内容执行包/SOP_全平台执行手册_20260724 2.md` 路径已失效，不再引用。
- **草稿真值**：`E:\iCloudDrive\iCloud~md~obsidian\DuoDuo_AI_Workspace\05_CONTENT\03 drafts\`（公众号/播客/视频的真实日期+标题以此为准，禁止自行编造）

**9 条锁死规则（排期必须遵守，禁止漂移）：**
1. 认知日轮转：窗口内 C1/C2/C3/C4/C5 五天轮转 + 知识库号独立线 + 世斐额外线；C2 = DUODUO WEAR 泳衣日。
2. 世斐号：抖音/小红书/视频号 各 2 视频/周（旅行线，不绑 C1–C5）。
3. 短文组齐发：X / Threads / 微博 / 即刻 / 知识星球 = 一组，每个个人 C 日（非 C2）同天齐发、同内容；X + Threads 发英文、措辞微差（写两份不写一份）。
4. Medium / Substack：双周·奇数周 各 1 篇 C5 英文长文（同公众号 C5 改编）。
5. 多多OS 三视频平台：抖音/小红书/视频号 同一天发同一条视频，每周 2 条。
6. 一天同一平台账号只发 1 条（视频日占掉该号小红书槽位，当天不再另发图文）。
7. 公众号 C1/C3/C4/C5 都可发。
8. 多多OS 个人号不发泳衣；C2 只归 DUODUO WEAR 泳衣。
9. 世斐 = 额外旅行/冲浪内容，不绑 C1–C5。

排期结构（每天一区块 `.day`：`.top` 日期+认知+周末 boost 标；短文组日加 `.uni` 横幅；账号行 table 4 列=账号/格式/归属/文案状态；底部 `.tally` 频次核对 + `.next` 下一步）。单文件结构规范与频次语义分工见 `duo-content-weekly-workflow` 技能 §二/§三（不再单独维护 `schedule-template.html`）。

---

## 九、发布后文件更新

在原 to_publish 文件末尾**追加**（不覆盖）：

```
### 发布记录
| 平台 | 账号 | 状态 | 实际发布时间 | 链接 | 备注 |
```

状态枚举：`published / scheduled / draft_saved / failed / needs_confirmation / skipped`
全部成功 → 文件状态改 `published` 并移入 `04 Published/`；部分成功 → `partially_published`。失败/未验证绝不标成功。

## 最终汇报格式

原计划平台数 / 成功数 / 定时数 / 草稿数 / 失败跳过数 / 每平台链接 / 已执行核验 / 异常待办 / 原文件是否已更新。禁说"应该发好了"。

## 注意（iCloud 坑）

写进 vault 的发布记录/移动操作，必须同步本地安全副本 + ls 验证落盘（2026-07-29 曾发生 iCloud 回滚清空事故）。
Git Bash 环境**没有 `stat`**，落盘自检用 `ls -l <file> | awk '{print $5}'` 取字节数，别用 `stat -c%s`（会静默返回 0 造成"文件为空"误判）。

## 归因铁律：先证伪再下结论（2026-08-02 血泪）

失败归因写进发布记录前，**必须实测验证归因本身**。已发生三次连环误判：

| 误判 | 真相 | 教训 |
|---|---|---|
| 「素材缺失，`deliverables/assets_0731/` 不存在」 | 素材在 `C:\Users\Administrator\WorkBuddy\<会话时间戳>\deliverables\` | draft 里的**相对路径**在不同工作目录下解析结果不同。判"文件不存在"前必须 `find / -type d -name "<目录名>*"` 全盘搜一次 |
| 「全 vault 零张真实试穿照」（连判两天，硬阻塞挂两天） | `test_1~8.jpeg` 就是实拍试穿照，在上述目录 | 同上。素材类阻塞是最容易假阳性的一类 |
| 「登录态失效，显示请重新登录」 | 登录态有效，只是**新开标签没带 token** | 见下方公众号核验方法 |

**归因优先级**：账号不匹配 > 登录态 > 素材 > 网络。今晨那轮把"账号不匹配"错报成"素材缺失"，掩盖了真问题。
**每条 to_publish 执行前先核对 `平台+账号` 与浏览器当前登录账号是否一致**——不一致直接 blocked，不要走到素材步骤才发现。

## CDP 只读核验（直连 9222，不走 3456 代理）

3456 代理能力残缺（无 `/clickXY`、`/type`）。**直连 `127.0.0.1:9222` 能力完整**，核验一律走直连。

- 新开标签：`PUT /json/new?<urlencoded_url>` —— **必须 PUT**，GET 报 `Using unsafe HTTP verb`
- 读完 `GET /json/close/<tabId>` 关掉，别污染多多的标签页
- 通用只读脚本模板：`98_Windows_work/03_发布助手/_verify_0802.mjs`（新开标签 → Runtime.evaluate 取 innerText → 关闭）

### 公众号核验（多多OS）

token 从已有 mp.weixin 标签 URL 正则 `token=(\d+)` 提取，然后：

- 发表记录（查是否已发/是否重复）：`https://mp.weixin.qq.com/cgi-bin/appmsgpublish?sub=list&token=<T>&lang=zh_CN`
- 草稿箱：`https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit&action=list_card&type=77&token=<T>&lang=zh_CN`

⚠️ **不带 token 的新标签一律显示「请重新登录」，这不代表登录态失效**。必须带 token 复测才能判定。
⚠️ 公众号「发表」会触发**微信扫码安全验证**，agent 无法绕过 → 状态记 `needs_confirmation`，并**立刻查发表记录页确认到底发没发**（群发不可撤回，最高优先级核验）。

### 已知无解点

- 小红书 `<xhs-publish-btn>` 是 Vue Web Component，无 shadow DOM 无子元素；`dispatchEvent` / `Input.dispatchMouseEvent` / `synthesizeTapGesture` / `elementFromPoint().click()` 全部无效。需多多手点或专项授权。
- Windows 本机**无海外网络**：X / Threads / Instagram 一律 `ERR_CONNECTION_CLOSED`，直接转 `05_交接/` 给 Mac，别浪费轮次重试。

## 铁律

- **验证后才算完成**：发完必须去主页/后台确认内容存在，禁止凭 DOM 变化谎报成功。
- 登录态用 `/new`+`/eval` 探 DOM 登录墙 + URL 是否含 login/signin 判断；consumer 平台 cookie 偶尔会掉，发前必查，查不到登录态直接报告，不瞎发。
- 改完 cdp-proxy 必须重启代理才生效。
