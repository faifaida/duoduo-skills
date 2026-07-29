---
title: "公众号长图发布全流程（多版本）"
summary: "把设计稿（HTML 长图）自动发布到微信公众号（mp.weixin.qq.com）。支持 4 套设计变体（A 长卷叙事 / B 刊物杂志 / C 暗夜海面 / 正式稿）任选，含素材处理、Cookie 提取、Playwright 自动登录、上传、存草稿。正文最低字号强制 ≥21px。"
read_when:
  - 多多说"帮我发公众号" / "发公众号长图"
  - 用户要求自动化公众号发布
  - 涉及 Playwright 操作 mp.weixin.qq.com
  - 需要在多个公众号长图设计稿之间选择
---

# 公众号长图发布工作流（多版本）

## 适用场景

多多个人公司「多多OS」公众号发布**长图型图文**（一张高图切成 2~3 段上传，阅读体验像一张长海报）。本 skill 已沉淀 4 套设计变体，发布前由用户**选一套**即可。覆盖：

- 长图 HTML → 渲染高清 PNG
- 切段（符合公众号限制：宽 ≤1080、单图面积 <600 万 px、<10MB）
- 图片素材处理（封面裁剪、二维码替换、GIF 背景 padding）
- Playwright 自动登录后台 → 新建图文 → 填标题/摘要 → 上传正文图 + 封面 → 保存草稿
- 用户手动点「发表」+ 扫码群发（自动群发被 cookie 权限拦截，见下）

**⚠️ 两条硬限制（已验证无法绕过）：**
1. **自动群发被拦（除非重扫码授权）**：发表按钮（`#js_send`）需要 cookie 带「允许切换登录我的其他公众号、服务号、小程序」权限，提取的 Chrome cookie 没有 → 弹权限框。所以默认流程止于「保存为完整草稿」，群发由用户手动扫码。**解锁法**：Chrome 退公众号登录 → 重新扫码时勾选该选项 → 重提 cookie → 跑 `publish_wx_v6.cjs` 即可全自动（封面 picker + 发表全通）。
2. **封面不能直传**：编辑器封面 file input 不在初始 DOM，点击封面区弹出的是「图片库 UI」而非文件选择器。封面必须**先传素材库 → 再从图片库选**。

## 版本选择（核心）

4 套设计变体已存于 `templates/`：

| 变体 | 文件 | 视觉调性 | 适合 |
|------|------|----------|------|
| 正式稿 | `templates/正式稿_半离职状态_1080.html` | 深青墨绿海浪底 + 亮青编号 + 米白卡片；最贴品牌 | 当前 v1 首篇；正式、品牌感强 |
| **A 长卷叙事** | `templates/A_长卷叙事_1080.html` | 米白纸底 + teal/sand 编号 + 手写体点缀；暖、编辑式、照片占位 | 想更亲和/叙事感强时用 |
| B 刊物杂志 | `templates/B_刊物杂志_1080.html` | 纸张底 + 刊头(masthead) + 首字下沉；杂志感 | 想做"刊物/专栏"调性 |
| C 暗夜海面 | `templates/C_暗夜海面_1080.html` | 暗色 hero + 海浪 + 深色高级感 | 想走暗黑高级/夜色氛围 |

- **用户选哪套，就发布哪套**。没指定时默认用「正式稿」（已合规 21px、已渲染）。
- 4 个模板当前都**内嵌 v1 文章《青旅开业后，我却进入了半离职状态》正文**。换文章时：复制模板 → 替换 `.hero` 标题/副标 + 各 `.sec` 文案 + `.cta`/`.foot` → 重渲染。
- A/B/C 含 `.photo` 占位 div（无真实图），发布前需用真实照片替换（见 Phase 0 / Phase 1）。

### 正文最低字号：手机可见 ≥21px（发布前必做）

**⚠️ 关键规则（2026-07-27 实测确认）：**
微信文章在手机上显示时，1080px 宽的长图会被缩放至约 **375px**（缩放比 ≈2.88×）。
- 设计稿里写 `font-size: 21px` → 手机上实际只有 **~7px**，用户明确反馈"太小"。
- **要达到手机上 ≥21px 可见，1080px 设计稿的正文 font-size 必须 ≥60px（≈3×）。**

操作方法（以正式稿为例，已合规）：
1. 全局 `font-size` ×3：`font-size: (\d+)px` → 替换为 `Math.round($1*3)px`。body 21→63、h1 36→108、h2 26→78 等。
2. 修正固定尺寸容器（否则放大后溢出）：
   - `.sec-num` 圆圈 52→140px，字体 22→63
   - `.hero-badge` 章形 82→224px，字体 21→62
   - `.tri-grid` 若含英文长词（如 "Experiment"），改为 `grid-template-columns: 1fr` 单列
   - body 加 `overflow-x: hidden` 防横向溢出
3. 验证：渲染后用 Read 工具目视检查段图文字大小。
4. **A/B/C 模板发布前同样处理**（它们原稿有 17-20px，×3 后 ≥51px → 手机 ≥18px；若要求严格 ≥21 则需额外 +10% 到 ≥61px）。

> **为什么不是改设计宽度为 375？** 改宽度需要重排所有 padding/margin/font（工作量 = 重设计整个 HTML）。保持 1080 布局只放大字体是最小改动路径。

## 前置条件

### 环境依赖（绝对路径，勿用裸命令）
- Node：`/Users/Zhuanz/.workbuddy/binaries/node/versions/22.22.2/bin/node`
- Playwright：workspace `…/06_AI_WORKBENCH/Workbuddy/2026-07-19-18-29-25/node_modules/playwright`
- Python venv：`/Users/Zhuanz/.workbuddy/binaries/python/envs/default/bin/python3`
- Chrome：用户已在 Chrome 登录 mp.weixin.qq.com（用于提取 cookie）

### Python 包
`pip install browser_cookie3 Pillow imageio-ffmpeg`

### Node 包（在 workspace node_modules）
`npm install playwright`

### 工作目录（脚本与素材实际运行处）
```
03_ACTIVE PROJECTS/ai个人公司/公司档案/02_内容运营/Human3_内容执行包/公众号长图方案/
```
本 skill 的 `templates/` 是**设计稿仓库**；真发布时把选中的模板复制到上面工作目录、注入素材后再跑脚本。

## 完整工作流

### Phase 0：素材准备

| 素材 | 来源 | 处理 | 输出 |
|------|------|------|------|
| 封面 | `02_CONTEXT/多多照片/` 拿冲浪板的照 | PIL 16:9 裁剪 → 900×500 | `assets/封面_冲浪.jpg` |
| 底部 QR | `公司档案/00_共享公司资料/多多os微信号二维码.jpg` | resize → 400×509 PNG | `assets/微信号二维码.png` |
| 冲浪 GIF | `assets/冲浪视频.mp4`(4K/117MB/10s) | ffmpeg palettegen→截 2.5s→480×270→PIL pad 1080×270 深青绿 `#0c3236` | `assets/冲浪.gif`（≤2MB） |
| 正文照 | `02_CONTEXT/多多照片/` / `assets/` | 按模板 `.photo` 占位替换 | 段1/段2 内嵌 |

素材处理参考脚本：`/tmp/process_assets.py`（封面/Q R/GIF 三合一）。

### Phase 1：选版本 + 设计 HTML

1. 问用户要哪套（或默认正式稿）。
2. 复制 `templates/<版本>.html` 到工作目录，改名如 `发布稿_<版本>_1080.html`。
3. 注入内容：标题/副标、各章节文案、CTA、`.foot` 二维码（把占位 `<div class="qr">二维码占位</div>` 换成 `<img class="qr" src="assets/微信号二维码.png">`）、真实照片替换 `.photo` 占位。
4. **强制 21px**（见上）。

### Phase 2：渲染 + 切段

**渲染**（`render_split.js`，Playwright 全页截图）：
- 检测 `.wave-banner`（GIF 区）边界 → 在 GIF 处断开
- `deviceScaleFactor: 2` → `rendered/全图_2160.png`
- 运行：`NODE_PATH=…workspace/node_modules …/node render_split.js`

**切段**（`split.py`，PIL）：
- 按 GIF 边界切 2 段；每段缩到 1080 宽 JPEG quality=88
- 校验：面积 ≤600 万 px、文件 ≤10MB
- 输出 `rendered/段1.jpg` `rendered/段2.jpg`

**发布插入顺序**：`段1.jpg` → `冲浪.gif`（单独插入会动）→ `段2.jpg`

> 若模板无 `.wave-banner`（A/B/C），改在正文照之间自然分段，或直接整图切 2~3 段。

### Phase 3：Cookie 提取

`extract_wx_cookies.py`：
- `browser_cookie3.chrome(domain_name="weixin.qq.com")` 读 Chrome keychain
- **必须 `dangerouslyDisableSandbox: true`**（访问钥匙串）
- 输出 `wx_cookies.json`（Playwright `addCookies` 格式）
- 关键登录态：`bizuin / data_ticket / slave_sid / slave_user`

### Phase 4：自动建文 + 发布（publish_wx.cjs）

步骤：
1. `chromium.launch()` → `ctx.addCookies(cookies)`
2. `goto mp.weixin.qq.com` → 验证登录（URL 含 `/cgi-bin/home` + token 即成功）
3. 点「文章」→ 进编辑器（`/cgi-bin/appmsg.*appmsg_edit`）
4. 填标题（contenteditable + `dispatchEvent('input')`）
5. 填摘要（contenteditable/textarea，`placeholder` 含「摘要」）
6. 上传 3 张正文图（`input[type="file"]`.setInputFiles，顺序：段1→gif→段2）
7. **封面上传**：先传素材库 → 回编辑器点封面区 → 「从图片库选择」→ 选 `封面_冲浪.jpg` → 确定
8. 关弹窗（多次 Escape）→ `#js_submit` 保存草稿
9. 提示用户手动「发表」+ 扫码

运行需：`NODE_PATH=…workspace/node_modules` + `dangerouslyDisableSandbox: true`

### Phase 5：手动完成（用户侧）

| 步骤 | 操作 |
|------|------|
| 1 | 打开 mp.weixin.qq.com → 内容管理 → 草稿箱 |
| 2 | 找最新草稿（标题+时间）→ 编辑 |
| 3 | （若封面没自动上）从 `assets/封面_冲浪.jpg` 拖到封面区 |
| 4 | 删旧草稿（避免堆积） |
| 5 | 点「发表」→ 弹窗选「无需声明」→ 扫码群发 |

## 关键技术点

### 按钮选择器（1280×900 视口）
| 按钮 | ID/选择器 | 坐标 |
|------|-----------|------|
| 保存为草稿 | `#js_submit` | (905, 867) |
| 预览 | `#js_preview` | (1015, 867) |
| **发表** | `#js_send` | **(1125, 867)** |
| 新建图文「文章」 | `text=文章` / `div.create-card` | — |

### 编辑器标题不是 <input>
是 contenteditable div。填法：
```javascript
const ce = document.querySelector('[contenteditable="true"]');
ce.focus(); ce.innerText = '标题'; ce.dispatchEvent(new Event('input',{bubbles:true}));
```

### Body 图片上传
编辑器只有一个 `<input type="file">`（在下拉菜单 DOM 里），`setInputFiles()` 即可触发，**无需先点图片按钮**。连续 3 次按序插入。⚠️ 顺序：段1 → gif → 段2，**千万别在 body 前先传封面**。

### 封面上传（经素材库，最稳路径）
1. `goto …/cgi-bin/filepage?type=2&…`（素材库图片页）
2. 点「上传图片」→ 对出现的 `input[type=file]` `setInputFiles(封面_冲浪.jpg)` → 等 5s 入库
3. 回编辑器 → 点 `.js_cover_preview_new`/`.select-cover__btn` → 弹 4 选项
4. 点「从图片库选择」（文本模糊匹配，允许嵌套）
5. **等 dialog Vue 渲染**：`waitForFunction` 直到 `.weui-desktop-dialog img.length>5`（最多 ~15s，可能需滚动/懒加载）
6. 选图优先级：① 文本含「封面_冲浪.jpg」的元素→点其最近 `li/a/[class*=item]`；② 第一个含 `<img>` 的 `li/a/[class*=item]`；③ dialog 内第一个 `<img>` 的父链
7. 点「确定」→ 校验 `.js_cover_preview_new img` 出现
8. 若 selector 失效，**dump dialog outerHTML 到 /tmp 诊断**（见 `publish_wx.cjs` 里的 `cover_dialog_dump.txt`）

### GIF padding 解决背景断裂
GIF（480×270）夹在两段 1080 宽长图间会被白色背景截断，需 pad 到 1080×270 深青绿 `#0c3236`：
```python
from PIL import Image
gif = Image.open('冲浪.gif')
canvas = Image.new('RGBA',(1080,270),(12,50,54,255))
canvas.paste(gif.resize((480,270),Image.LANCZOS),(300,0))
canvas.save('冲浪_padded.gif')
```

## 常见问题

- **提取 cookie 失败**：需 `dangerouslyDisableSandbox: true`；确认 Chrome 已登录 mp.weixin.qq.com 且未退出；首次可能弹钥匙串授权，允许一次。
- **发表按钮弹权限框（根因已定位，2026-07-27 实测）**：cookie 缺「允许切换登录我的其他公众号、服务号、小程序」scope。**该 scope 嵌在 `data_ticket` cookie 里、扫码时勾选才授予**（已验证：localStorage 仅含 `__WXLS__*` UI 状态，不存授权；用 Chrome profile 拷贝启动 Playwright 也失败——沙箱无法解密 profile 的 Cookies SQLite/钥匙串）。解决：**Chrome 退公众号登录 → 重新扫码时勾选该选项 → 重跑 `extract_wx_cookies.py` 刷新 `wx_cookies.json` → 跑 `publish_wx_v6.cjs` 全自动（封面 picker + 发表都通）**。否则只能手动群发。
- **封面选不到**：严格走「素材库→从图片库选择」流程；若 dialog 图片没加载，等久一点或 dump HTML 看结构。最差兜底：用户手动从 `assets/封面_冲浪.jpg` 拖拽。
- **3 张图顺序乱**：body file input 只有一个，连续 setInputFiles 按序插；顺序必须 段1→gif→段2。
- **字体发虚/太小**：正文最低 21px；渲染用 `deviceScaleFactor: 2` 保清晰。

## 脚本索引

| 脚本 | 位置 | 用途 |
|------|------|------|
| `templates/*.html` | skill 内 | 4 套设计变体（A/B/C/正式稿） |
| `正式稿_半离职状态_1080.html` | 工作目录 | 当前 v1 长图源（已 21px） |
| `assets/` | 工作目录 | 图片素材 |
| `render_split.js` | 工作目录 | Playwright 渲染 + 分段坐标 |
| `split.py` | 工作目录 | PIL 切段 + 校验 |
| `extract_wx_cookies.py` | 工作目录 | 提取 Chrome 公众号 cookie |
| `wx_cookies.json` | 工作目录 | cookie 输出（自动生成） |
| `publish_wx.cjs` | 工作目录 | v4 主发布脚本（含封面库选图 + 诊断 dump） |
| `publish_wx_v5.cjs` | 工作目录 | 试过用 Chrome profile 拷贝启动（沙箱解密失败，弃用） |
| `publish_wx_v6.cjs` | 工作目录 | **重扫码勾选 scope 后的全自动脚本**（封面 picker + 发表，跑前先重提 cookie） |
| `verify_login.cjs` | 工作目录 | 仅验证登录态（调试用） |
| `/tmp/process_assets.py` | /tmp | 封面/QR/GIF 素材处理器 |
