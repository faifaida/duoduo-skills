---
name: os-video-edit
description: 多多OS·回家接班实验 视频剪辑标准流程（EP01/EP02 双路径已验证）。当多多要求"剪辑/剪视频/出成片/做封面/导出/圆角/字幕/交给发布助手"任一集时使用。覆盖两条执行路径：路径A=本地 OpenChatCut+ffmpeg（Codex EP02），路径B=云端 ChatCut MCP（Windows agent EP01）。含 转写→时间线/分镜重组→调色→字幕→圆角→混音→导出→封面→QC→交付发布助手 全链路。
agent_created: true
---

# os-video-edit — 多多OS 视频剪辑标准流程

> 把一集「生产包 + A-roll + B-roll + 文案」变成 **成片 mp4 + 封面 png + 三平台 to_publish 草稿**，交给发布助手。
> 创意/分镜的权威规范在 `SOP_导演工作流.md`（`98_Windows_work/10_win个人号导演/多多os最终生产包/`），本 skill **只管技术剪辑流程**，不重复分镜规则。

## 决策说明（为何是单份 skill + 双路径）

- Codex（Mac 剪辑）剪 EP02 用的是**本地 OpenChatCut 桌面**（127.0.0.1:5199）+ 本地 Whisper + ffmpeg 渲染脚本，产出在 `多多os最终生产包/EP2_工作文件/`。
- Windows agent（我）剪 EP01 用的是**云端 ChatCut MCP 插件** + 代理上传 + submit_export，封面用本机 Chrome 透明圆角。
- 两套工具链不同但工作流同构。为防流程分裂，**本 skill 作为唯一 canonical 源**，把两条执行路径都写进来；Codex 的 EP2 经验完整保留为「路径 A」，不被丢弃。
- 若多多要求改回"把我的 EP01 流程补进 Codex 的 EP2 工作文件"，按那条走即可，本 skill 可删。

---

## 何时触发

多多说以下任一即触发：剪辑 / 剪视频 / 出成片 / 做封面 / 导出 / 圆角 / 字幕 / 交给发布助手 / 发布 EP0X。

## 输入（每集必备）

1. 生产包 HTML/JSON（`多多OS_回家接班实验_v4_完整生产包.html` + `生产包_v4.json`）——脚本一字不动，分镜按新顺序重配。
2. A-roll 口播视频（竖屏 9:16）。
3. B-roll 素材（按分镜检索标签 retrieval）。
4. 物件 + 现场声（每集 ≥4s 纯现场声）。
5. 三平台发布包（封面文案/标题/话题）。

---

## 全链路标准步骤（两条路径共用）

1. **转写**：A-roll → 逐词时间戳 / 口播行时间轴。
2. **时间线/分镜重组**：按 `生产包_v4.json` 的镜头顺序，A-roll 对镜 + B-roll 短镜（1.5–2.5s）交替；物件首尾呼应。
3. **调色**：暖橙偏品红。DaVinci WB+100R/+50M；ffmpeg 近似见下。
4. **字幕**：逐字动态字幕，关键词花体放大，≤2 行，3–5 关键词/集。
5. **圆角**：所有画面图层真圆角（`borderRadius` 或 圆角遮罩），**禁黑色块遮罩**。
6. **混音**：多多本人原声 + B-roll 现场声 + 关键台词前后 0.3–1s 呼吸；可选打字机点击声。
7. **导出**：9:16、H.264+AAC、核心 2:00–2:15 + 结尾 ≈2:10–2:50。
8. **封面**：3:4（1080×1440）透明圆弧边角，出 A/B 两版备审。
9. **QC**：ffprobe 验编码/分辨率/时长；四角透明核验；逐镜肉眼核对。
10. **交付发布助手**：成片 + 封面落本地，写 `to_publish_*.md`（approved）到 `05_CONTENT/03 drafts/`。

---

## 路径 A：本地 OpenChatCut + ffmpeg（Codex EP02 验证）

> 适用：本机有 OpenChatCut 桌面（127.0.0.1:5199）+ `codex-video-tools` ffmpeg + faster_whisper。
> 参考实现：`98_Windows_work/10_win个人号导演/多多os最终生产包/EP2_工作文件/` 下 `transcribe_ep2_local.py` / `render_ep2_ffmpeg.py` / `build_ep02_cover.py`。

**1. 工程创建**（OpenChatCut 本地服务）
```json
{ "name":"多多OS_EP02_v4", "description":"...",
  "compositionWidth":1080, "compositionHeight":1920, "fps":24,
  "editorBaseUrl":"http://127.0.0.1:5199" }
```

**2. 转写**（本地 Whisper，比云端更可控）
- `faster_whisper` `WhisperModel("small", device="cpu", compute_type="int8")`
- 参数：`language="zh", beam_size=5, word_timestamps=True, initial_prompt=<口播校正稿>, condition_on_previous_text=True`
- 输出 `EP2_本地Whisper逐词时间戳.json`（segments + words）

**3. 圆角遮罩**（生成一次复用）
- 生成 `round_mask.png`：1040×1840 单通道，`rounded_rectangle((0,0,1039,1839), radius=46, fill=255)`
- ffmpeg 叠加：`[fg]scale=1040:1840:force_original_aspect_ratio=...,...[v];[mask]format=gray[mask];[fg][mask]alphamerge[rounded];color=c=#000000:s=1080x1920[canvas];[canvas][rounded]overlay=20:40`
- 画布 1080×1920，圆角边距 20/40。

**4. 调色**
- `eq=brightness=0.02:contrast=0.97:saturation=0.94,colorbalance=rs=.035:bs=-.025`（江酱暖度 R−B≈+47.6 的 ffmpeg 近似）

**5. 字幕（ASS）**
- 样式三套：`Caption`（正文 76pt Source Han Serif SC Heavy）、`Keyword`（关键词 164pt 花体放大）、`BlueLine`（下划线/蓝绿 #00FF7D1D）
- 关键词打字机：`\pos(540,880)` 逐字追加 `text[:index]`，每字约 4/24s
- 字体：`C:\Windows\Fonts\Source Han Serif SC Heavy (TrueType).ttf`

**6. 混音**
- A-roll + B-roll 现场声（`volume` 参数，如 .04–.75）+ 每字鼠标点击声（`OpenChatCut-src\...\assets\sound-effects\mouse-click.mp3`）
- ffmpeg `-filter_complex_script` 串接 `volume/adelay/amix/alimiter`

**7. 渲染**
- ffmpeg 路径：`C:\Users\Administrator\AppData\Local\Programs\codex-video-tools\bin\ffmpeg.exe`
- 分段渲染各 edit boundary → concat → 合成字幕/混音 → 输出 `多多OS_EP02_v4_纪录片版.mp4`

**8. 封面（PIL）**
- `build_ep02_cover.py`：`warm_grade`（R×1.045 / G×1.005 / B×0.91）+ 物件 QUAD 透视变换叠图 + 标题带 + 噪点；输出 3:4 PNG+JPG。
- 注意：Codex 版封面是**不透明底**（适合 EP2 物件叙事）；若要多多偏好的透明圆角，改走路径 B 的 Chrome 法。

**⚠️ 路径 A 关键坑**
- libass 不能可靠读长 Unicode 路径 → 渲染资产（ass/字体/分段）stage 到 ASCII 短路径再引用。
- OpenChatCut 实际渲染由 ffmpeg 脚本完成；OpenChatCut 桌面只管时间线编辑，别指望它的渲染器出最终片。

---

## 路径 B：云端 ChatCut MCP（Windows agent EP01 验证）

> 适用：本机无明显本地剪辑工具、但有 ChatCut MCP expert 插件 + 代理 127.0.0.1:7897。
> 参考实现：workspace `_upload_media_patched.mjs` + `__setproxy.mjs`；ChatCut MCP 工具集。

**0. 连接**
- 工具来自 `chatcut` MCP expert 插件（**非普通连接器**）。
- ⚠️ agent 侧**无重连权限**：MCP 断连时，新开一个对话即可自动恢复工具索引（勿用夸克 CDP 上传——React 上传框 `setFileInputFiles` 恒 0）。

**1. 拿上传令牌**
- `import_media` action=`create_session` → 返回 `sessionToken` + `endpoint`（上传 API base）。

**2. 上传素材（走代理）**
```bash
node --import file:///C:/.../__setproxy.mjs _upload_media_patched.mjs \
  --token <sessionToken> --endpoint <endpoint> --input Aroll.mp4 --input broll.mp4
```
- `__setproxy.mjs`：`undici` `ProxyAgent('http://127.0.0.1:7897')` 全局注入。
- S3 直连浏览器超时，**必须走代理**；多文件并行。

**3. 编辑时间线**
- `edit_item`（deletes + adds）：B-roll 横屏源用 `fit:"cover"` 铺满竖屏画布 + `borderRadius:90` 真圆角（**禁黑块遮罩**）。
- 验证：`read_project`（timeline / itemId 视图）。

**4. 导出 + 下载**
```bash
# submit_export
submit_export(projectId, timelineId, format:"video", codec:"h264", resolution:"1080p", fps:30)
# 轮询
track_export(action:"status", renderIds:"<renderId>")
# 下载（S3 直连被墙，走代理）
curl -sS -x http://127.0.0.1:7897 -L -o EP0X_成片.mp4 "<s3-url>"
```

**5. 转写**
- `doubao-asr` skill（豆包 Seed-ASR 2.0）做口播逐词时间戳。

**6. 封面（本机 Chrome 透明圆角）**
```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --no-sandbox \
  --disable-gpu --hide-scrollbars --default-background-color=00000000 \
  --force-device-scale-factor=1 --window-size=1080,1440 --screenshot=cover.png \
  --user-data-dir=<tmp> "file:///<cover.html>"
```
- 验证四角透明：`ffmpeg -vf "crop=1:1:X:Y" -pix_fmt rgba -f rawvideo -` 读角落字节第4字节=0（透明）、中心=255（不透明）。

**项目常量（备查）**
- EP01：projectId `e6be85a9-07a7-4f73-a6e9-e821ac068576` / timeline `0bdd735c`（1080×1920@30）
- EP02（OpenChatCut）：projectId `f52fd206-e089-4790-b640-e2ff09070e18`

**⚠️ 路径 B 关键坑**
- 勿用 CDP 代理 `/screenshot`（pipe 模式超时）；用本机 Chrome 命令直出。
- ChatCut 云端导出后下载必须走代理。
- 横屏 B-roll 入竖屏画布必须 `fit:"cover"`，否则拉伸变形。

---

## 共用视觉/音频标准（来自 SOP + duoduo-design-system）

| 维度 | 标准 |
|---|---|
| 画幅 | 9:16 竖屏 |
| 时长 | 核心 2:00–2:15 + 结尾 ≈2:10–2:50 |
| 色调 | 暖橙偏品红（DaVinci WB+100R/+50M；ffmpeg 近似见上） |
| 圆角 | borderRadius/遮罩真圆角；四角透出背景，禁黑块 |
| 字幕 | 逐字动态；关键词花体放大 ≤2 行；3–5 关键词/集 |
| 声音 | 多多本人原声；每集 ≥4s 纯现场声；关键台词前后呼吸 |
| 片尾 | 全季统一结语（逐字·花体）+ 小字"回家接班实验"+1s安静 |
| 物件 | 每集 1 核心物件，片头入画片尾回收 |
| 父亲 | 不剪反派、不露正脸、不替其断言动机 |
| 隐私 | 员工正脸模糊；合同/公章/公司名最小局部 |

## 封面规范

- 尺寸 3:4（1080×1440），圆弧边角（四角透明）。出 A/B 两版备审。
- 文案从三平台发布包取；品牌色 暖米 #f1e9da / 深海 #151a2e / 蓝绿 #00B6C5 仅高亮。
- 落款用 `DUODUO` 文字字标（技能包无 logo PNG）。
- 透明圆角验证：ffmpeg crop 1:1 四角 pix_fmt rgba → 角落 alpha=0、中心=255。

## 交付发布助手

- 成片 + 封面落本地（生产包目录）。
- 写 `to_publish_*.md`（状态 `approved`）到 `05_CONTENT/03 drafts/`：含 `platforms / 标题 / 正文(代码块带 #话题#) / 配图(封面+视频) / 标签 / 发布前自检 / 发布记录`。
- 发布助手 CDP 自动扫描 10:00/22:00 发布；先核验账号登录态（⚠️ 视频号=多多OS 非 DUODUOWEAR 品牌号风险）。
- 配图铁律：草稿 `## 配图` 段列图必须全挂，裸文本=发布失败。

## 禁止事项

- 不把父亲剪反派 / 露正脸 / 断言动机。
- 不用 AI 生成历史画面 / 网络泛化 B-roll。
- 不写"关注看下集" / "青旅已开业"。
- 不用黑色块做假圆角。
- 不交付 .md 给多多审阅（用 HTML / 预览件）。

## 三同步（封 skill 必做，Windows 侧职责）

1. 更新本 skill：`~/.workbuddy/skills/os-video-edit/SKILL.md`
2. 镜像 vault：`E:/iCloudDrive/iCloud~md~obsidian/DuoDuo_AI_Workspace/99_Systems/Workflows/os-video-edit_SKILL.md`
3. 上传 GitHub `faifaida/workbuddy-skills`：走 Git Database API 或 `git push`（openssl backend + 代理 `127.0.0.1:7897`）。被墙时告知多多手动。
