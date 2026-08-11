---
name: duoduo-video-edit
description: >
  多多个人 IP 号视频制作全流程——素材审片（联系表+人脸识别+分级）、
  capcut-cli 剪映草稿自动化、ffmpeg 直出成片。覆盖：素材目录→联系表生成→AI 审片分级→
  人脸找多多→视觉板 HTML→剪映草稿/ffmpeg 成品。触发词：剪映草稿/自动剪辑/出片/capcut/
  素材审核/审片/找多多/联系表。
---

# 多多视频制作全流程 · 素材 → 成片

路线：素材审片 → 分级筛选 → 剪映草稿 / ffmpeg 直出。无需 GUI 自动化，跨平台。

## 脚本工具

| 脚本 | 用途 | 依赖 |
|---|---|---|
| `scripts/contact_sheets.py` | 素材目录 → 联系表（动态条/关键帧条/高清照片缩略图）+ manifest.csv | ffmpeg + Pillow |
| `scripts/face_id.py` | 人脸向量身份判定：build/check/batch/video 四模式 | insightface + onnxruntime + opencv |

### contact_sheets.py — 素材审片联系表

```bash
# 全量（Live Photo + 视频 + 照片）
python3 scripts/contact_sheets.py --src <素材目录> --out <输出目录>
# 只跑照片
python3 scripts/contact_sheets.py --src <素材目录> --out <输出目录> --mode photo
# 指定 ffmpeg、子目录当正片视频（如 Caz）
python3 scripts/contact_sheets.py --src <素材目录> --out <输出目录> --video-dirs Caz
```

产出：
- `sheets_live/*.jpg` — Live Photo 5 帧动态条联系表（3 列 × 7 行，每格=1 段的动态预览）
- `sheets_video/*.jpg` — 视频关键帧条联系表（2 列 × 7 行）
- `sheets_photo/*.jpg` — **高清**照片联系表（4 列 × 6 行，**44px 大字 ID**，可读！）
- `manifest.csv` — 全部素材索引（id, type, duration_sec, sheet）

⚠️ **照片联系表必须用大字 ID**：早期用 8 列小缩略图，审片员反馈「ID 读不清」→ 整批审核作废重做。格子太小 = 审核等于没做。已修正为 4×6 大格 + 大字标签，不可改回小格。

### face_id.py — 「这张图里是不是本人」

```bash
# ① 建档：放确认过的正脸照进 refs_raw/
python3 scripts/face_id.py build [--id-dir <工作目录>] [--exclude IMG_8577_face1,...]
# ② 单图判定
python3 scripts/face_id.py check <图片> [--id-dir <工作目录>]
# ③ 批量扫目录
python3 scripts/face_id.py batch <目录> [--recursive] [--id-dir <工作目录>]
# ④ 视频/Live Photo 抽帧判定（帧级投票）
python3 scripts/face_id.py video <视频文件> [--frames 8] [--ffmpeg <路径>]
```

铁律：
- **build 后必须逐张看 refs_cropped/**：合影常混进别人（路人/长辈），混进会把整个 ID 向量拉偏导致全盘误判。发现杂人用 `--exclude` 剔除重建。
- **距离用余弦距离**，不是欧氏距离。阈值需用负样本实测标定（本人 0.25–0.50 vs 非本人 0.92 → 阈值 0.75）。
- **人脸向量是生物特征数据，绝不推送到公开仓库**。`face_id.pkl` / `refs_*` 本地留存。

## Phase 0：素材审片（新项目第一步）

当用户给了一整批原始素材（几百到几千张），在动剪辑之前先做这件事：

1. **生成联系表**：`contact_sheets.py --src <素材> --out <审计目录>`
2. **AI 并行审片**：把 sheets_live / sheets_video / sheets_photo 分给多个 Agent 逐张看，每段评 A/B/C/D
3. **人脸找本人**：对含人物的素材跑 `face_id.py batch <目录>` 或 `face_id.py video <mov>`
4. **合并 SELECTS**：写一份分级文档（A=主镜头 B=连接 C=备用 D=弃）+ 授权清单（他人正脸）
5. **建视觉板 HTML**：用 html-anything skill 出单文件 HTML，A 级精选带真实图片预览
6. **写剪辑指南**：基于 SELECTS 给出骨架时间线 + BGM 方向 + 调色 + 转场 + 时长控制

评级标准参考（按项目调）：
- **A** = 主镜头级：画面美 + 动态/构图好 + 内容切题
- **B** = 可用连接/空镜：氛围或信息有用
- **C** = 备用
- **D** = 弃：糊/抖/无关/无动态

人物识别纪律：不确定就写「有人物·身份不确定」并描述外观，**绝对不要编造画面里不存在的人**（grill-me 红线）。

## 工具链路径（已部署于本机，勿重复安装）
- **ffmpeg / ffprobe**：软链在 `/Users/Zhuanz/.workbuddy/binaries/ffmpeg-bin/{ffmpeg,ffprobe}`（v7.1）。每次运行前：
  `export PATH="/Users/Zhuanz/.workbuddy/binaries/ffmpeg-bin:$PATH"`
- **capcut-cli**：`/Users/Zhuanz/.workbuddy/tools/capcut-cli/dist/index.js`（v0.15.0，已 build）。
  运行：`/Users/Zhuanz/.workbuddy/binaries/node/versions/22.22.2/bin/node /Users/Zhuanz/.workbuddy/tools/capcut-cli/dist/index.js <cmd>`
- **probe.py**（探分辨率/方向/时长/帧率）：`/Users/Zhuanz/.workbuddy/tools/probe.py`
- **lossless_cut.sh**（无损切/合并/转封装，替代 GUI 版 LosslessCut）：
  `bash /Users/Zhuanz/.workbuddy/tools/lossless_cut.sh {cut|merge|remux|probe} ...`

## 标准流程
1. **拿素材**：用户给 Photos 共享相册「公共网站」链接 → Playwright 批量下载到本地工作目录（**非 iCloud**，避免云端反复拉取）。工作目录建议：`~/.../Human3_内容执行包/IP视频制作/`。
2. **探方向**：`python3 /Users/Zhuanz/.workbuddy/tools/probe.py <clip>` → 看 `orientation`/`is_9x16`。竖屏直用；横屏需 `crop --ratio 9:16`。
3. **建草稿**（任选其一）：
   - 极简：`capcut quickstart <名> --video <clip.mp4> --drafts <工作目录>` （建+加视频+lint）
   - 声明式：`capcut compile <spec.json> --out <草稿目录>`（整条时间线一次生成）
   - 空白：`capcut init <名> --drafts <目录>`
4. **⚠️ 设竖屏画布**（最容易漏）：改 `draft_content.json` 的 `canvas_config`：
   ```js
   const d=JSON.parse(fs.readFileSync(p));
   d.canvas_config.width=1080; d.canvas_config.height=1920; d.canvas_config.ratio="9:16";
   if(d.width!==undefined){d.width=1080;} if(d.height!==undefined){d.height=1920;}
   fs.writeFileSync(p,JSON.stringify(d));
   ```
   **注意**：quickstart 默认横屏画布(1920x1080)。只改顶层 width/height 无效，必须改 `canvas_config`。否则 render 出来还是横的。
5. **加内容**：
   - 标题/口播字：`capcut add-text <草稿> <start秒> <时长秒> "文字" --font-size 40 --align 1 --y 0.3`
   - 自动字幕（需 whisper）：`capcut caption <草稿> --audio <clip> --language zh`（whisper 未装时先用 `import-srt` 导入手编 srt）
   - 横拍裁竖：`capcut crop <草稿> <segment-id> --ratio 9:16`（居中最大竖条）
   - 转场：`capcut transition <草稿> <id> dissolve --duration 0.5`
   - 封面：`capcut add-cover <草稿> <封面图.jpg>`
6. **代理预览（验证可看）**：`capcut render <草稿> --out proxy.mp4` → 出低分辨率竖屏预览，发给用户确认节奏/字幕。
7. **交付**：把草稿目录交给用户 → 剪映/JianYing 打开即见项目（已 register 进项目索引）→ 渲染导出。

## 关键坑（已踩过）
- **画布在 `canvas_config`，不在顶层**——见步骤 4。
- **iCloud 文件别用 ffprobe**：`~/Library/Mobile Documents/` 下大文件用 ffprobe 会触发 iCloud 云端整文件重下载→超时挂死。一律用 `probe.py`（ffmpeg -i 只读头部，秒回）。真实剪辑前把素材下到本地目录。
- **Caz 素材（懒懒岛/Caz/）8 段全是竖屏 9:16**（2160x3840 或 1080x1920），IMG_0395/8745/8747 是 4K 原片(3–5GB)，无需裁切。
- **capcut 版本/命名空间**：本机装了**两个**剪辑软件、草稿库各自独立——
  - CapCut（国际版）：`~/Movies/CapCut/User Data/Projects/com.lveditor.draft/`
  - **剪映 JianYingPro（国内版，多多实际用的）**：`~/Movies/JianyingPro/User Data/Projects/com.lveditor.draft/`
  - capcut-cli **默认写 CapCut 命名空间**，所以建完在剪映里看不到！**做剪映草稿必须给每个命令加 `--jianying`**（init/quickstart/add-video/add-text... 全加）。
  - ⚠️ **`--jianying` 只改枚举命名空间，不改输出目录**——实测 `init --jianying` 仍落 `~/Movies/CapCut/...`。必须**同时用 `--drafts` 指向剪映草稿根目录**：`--drafts "/Users/Zhuanz/Movies/JianyingPro/User Data/Projects/com.lveditor.draft"`（init/quickstart/add-video/add-text 全加），草稿才真正进剪映目录并注册。漏 `--drafts` 就会出现在 CapCut 库而非剪映。
  - **剪映会自动接管注册**：把草稿文件夹丢进 JianyingPro 的 `com.lveditor.draft/` 下（路径改对）让它自动扫到注册；手动改 `root_meta_info.json` 会被它的后台进程覆盖，别手动 register。
  - **剪映会自己扫文件夹、自动往 `root_meta_info.json` 写条目**——手动改注册表会被它的后台进程覆盖/丢弃。所以别手动 register，要么用 `--jianying` 让它自己写，要么把文件夹丢进 JianyingPro 的 `com.lveditor.draft/` 下（路径改对）让它自动接管（它会重写 draft_meta_info.json 的 draft_id/路径以匹配）。
  - 验证草稿到位：看 JianyingPro 的 `root_meta_info.json` 的 `all_draft_store` 里有没有该 draft_name，且 `draft_fold_path` 指向 JianyingPro 目录。
- **⚠️ add-video 在本机 ffprobe 探测失效 → 素材维度被错写成 1920x1080 横屏**：capcut-cli 自带的 ffprobe 在本沙箱探测失败（日志报 `Could not detect dimensions; defaulted to 1920x1080`），而真实素材多为竖屏（Caz 段是 2160x3840 或 1080x1920）。后果：剪映打开后竖屏片段被缩成中间一条横带。两种修法：
  ① **重建时显式传维度**（推荐）：`capcut add-video <草稿> <文件> <start> [dur] --width 1080 --height 1920`（4K 段用 `--width 2160 --height 3840`）。
  ② **patch 已生成草稿**：读 `draft_info.json`，按 `material_name` 把每段 `materials.videos[].width/height` 改成真实维度（段落 `transform.scale` 为空=自动，画布 9:16 时改对维度即满铺，不拉伸）。改完跑 `capcut lint <草稿>` 复核。
  **先用本机 ffprobe 探真实维度**：`/Users/Zhuanz/.workbuddy/binaries/ffmpeg-bin/ffprobe -v error -show_entries stream=width,height -of csv=p=0 <文件>`（Caz 段实测 IMG_0398/0400=2160x3840、8743/8744/8746=1080x1920，全竖屏）。

## 烟雾测试（已通过，可作模板）
- 竖屏：测试 clip 1080x1920 → quickstart → add-text → 画布 9:16 → render 出 540x960 ✓
- 横屏：1920x1080 → `crop --ratio 9:16` → 画布 9:16 → render 540x960 ✓

## 关联 skill
- `promo-creator-skills`：一条视频标准流程框架（简报→分镜→素材→剪辑→配乐→交付）。
- `remotion-video-toolkit`：程序化片头/片尾/卡点动画（React 代码生成）。
- `duoduo-voice-deai` / `qu-ai-wei`：口播稿去 AI 味（写文案用，保原声）。
- `duoduo-design-system`：封面/缩略图设计。
- `duo-wear-painting`：**AI 绘画插画**（小红书图文/口播讲解配图/公众号插画）的 sanctioned 例外——本 skill 的「禁 AI 生图」红线**只限视频封面与品牌实拍图**，知识分享/讲解/公众号插画走 `duo-wear-painting`（用户 2026-08-06 明确授权）。
- `3D模型与视频特效`：转场/特效片段（拥抱/变身/万物归尘模板）。

## 清新风直出 MP4 流水线（ffmpeg 替代剪映渲染 · 用户要"直接给成片"时用）

> ⚠️ 本节为**泛用清新风** ffmpeg 流水线，**非 DUODUO WEAR 品牌片现行规范**；品牌片视觉（字幕/调色）见上方「泳衣线视觉规范」。下面字幕/调色写法仅作泛用参考。
当用户要**最终成片**（不要自己开剪映渲染）且要清新/青春/通透调性（参考"小年糕"青春女大广告风）时，用此 ffmpeg 流水线直出：

- **素材红线**：用真实照片/视频，**禁止 AI 生图**（用户原话"ai生成图很假"）。照片源分辨率需 > 输出 1080（避免 zoompan 抖动；源够大则稳）。
- 竖屏 1080x1920：每段 `scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920`。
- 照片 Ken Burns：`zoompan=z='min(zoom+0.0015,1.2)':d={fps*dur}:s=1080x1920:fps=30:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'`（源图够大不抖）。
- **交叉淡入链式 xfade**：⚠️ **offset 公式 = cum_sum(durations[0..i]) - (i+1)*td**（td=转场时长）。只减一次 td 会导致越往后偏移越大、视频被截断成几秒——已踩坑崩过一次（出 8s 废片）。
- 通透调色：`eq=brightness=0.05:saturation=1.12:contrast=0.97,colorbalance=rs=0.03:bs=-0.03`（提亮+微暖+降对比，干净少女感）。
- 字幕干净化：用 `shadowcolor/shadowx/shadowy` 柔和阴影，**不要 borderw 粗黑描边**（丑）；居中下三分之一 `y=h-text_h-240`，`line_spacing=14`，fontsize~56，字体 Hiragino.ttc（已放 IP_video_drafts）。
- BGM 垫底：`[a]atrim=0:TOTAL,asetpts=PTS-STARTPTS,volume=0.5,afade=t=out:st=TOTAL-3:d=3`。
- 参考实现：`/Users/Zhuanz/IP_video_drafts/render_brand_v7.py`（DUODUO WEAR 泳衣第一篇 V7，11 镜头 xfade+zoompan+grade+clean type）。
- **真·卡点升级**（用户要"有节奏"时）：用 aubio/librosa 检测 BGM onset，把 xfade offset 对齐到鼓点，而非固定 4-5s 节奏。参考 GitHub `kburns-slideshow`(aubio onset)、`kdenlive_slideshow_editor`(madmom beat)。
- 字体：系统 `/System/Library/Fonts/Supplemental/` 无 PingFang 直出时，用 `IP_video_drafts/Hiragino.ttc`（ffmpeg drawtext 可用，渲染中文正常）。

## Film01 实战流水线（DUODUO WEAR 品牌片 · 已验证，2026-08）

背景：真实素材（斯里兰卡 Live Photo + 照片，禁 AI 生图）→ 中英双语烧录字幕成片 → 五平台版 → 封面。全程 ffmpeg + PIL，**无剪映渲染**。已发布成片 41.34s / 9:16 / 1080×1920 / 30fps。

### 1. 母版渲染（双语字幕 + BGM）

- **字幕防压字**：ASS 单条 `中文\N{\fnGeorgia\fs48}英文`，中英文共用一个 MarginV 定位框 → 杜绝「中文压住英文」。曾试过上下分开两条 → 相邻段互相覆盖，废弃。
- **BGM 低于人声**：`volume=0.10`（用户「音乐小一点」，较 0.15 再降 ≈ -3.5dB），VO `volume=1.4`。
- **BGM 仅 36s 起**：`afade=t=in:st=36:d=1.5`（36s 前静音→36–37.5s 淡入，39–41.34s 淡出）。
- **验证 36s 前无 BGM**：抽 `atrim=30:35,volumedetect`，与无-BGM 版 mean/max 应一致；**必须 `-v info` 才见 mean/max_volume**（默认静默）。
- 母版像素格式：`yuvj420p`（pc 全范围）。

### 2. 派生五平台版（不重剪，只转码）

- ⚠️ **range 转换坑**：母版 `yuvj420p(pc)` 必须转 `yuv420p(tv)`。**单独 `format=yuv420p` 不转 range**，必须靠 `scale=...:out_range=tv,format=yuv420p`。
- 命令模板：
  ```bash
  ffmpeg -y -i V06_MASTER_Film01.mp4 \
    -c:v libx264 -pix_fmt yuv420p -profile:v high -level 4.0 -crf 20 -preset medium \
    -color_range 1 -c:a copy -movflags +faststart Film01_XHS.mp4
  ```
- 五平台：XHS / Douyin / Shipinhao(视频号) / Instagram / YouTube 同一母版派生，封面按平台尺寸单出。

### 3. 封面流水线（PIL）

**★ 强制规则（2026-08-04 用户纠偏后确立）**：所有 DUODUO WEAR 视频封面**必须用 `scripts/make_cover.py` 生成**，禁止：① AI 生图当背景（必须用真实照片/真实帧）；② 白字标题（必须用米白 `#F1E9DA` + 暖墨 `#2A2620` 衬线）；③ 只放图形不放字标。定稿范例见 `references/covers_ep1/`（Film01_Cover_Final_4x5.jpg 等为规范参考，改 `make_cover.py` 顶部常量 PHOTO/TITLE/SUBTITLE 即可出下一条视频封面）。**Film02 曾踩雷：用 AI 金光图当背景 + 白字 → 被用户判"和 ep1 要求完全不一样"，已用模板重出。**

- 高清照片 + 底边缘米色渐变带 + **完整 logo lockup（含全大写 DUODUO WEAR，不要只放图形）** + 标题（如 `I wore it to disappear.` 放天空区域）。
- ⚠️ **「米色透明度拉低」= 更实**（alpha 调高，非调低）——用户口语反直觉，记牢。
- ⚠️ **字标（text mark）极宽**（~878×91）→ 必须锁版宽 ≤857px，否则整行超屏。
- ⚠️ **米色带与照片平滑过渡，禁止暗分隔线**：`make_cover.py` 顶部的 `edge` 块（band 顶 40px 叠 INK 渐隐）**已删除**；band 用 `CREAM_DEEP→CREAM` 渐变淡入，与照片无缝衔接。**不要再叠任何 INK 暗线**（Film02 用户明确要求去掉拼接黑线）。
- ⚠️ **中文副标必须与英文主标统一为米白（`CREAM_W` #F1E9DA）**，不得用暗暖墨 `INK`。两者共用同一阴影偏移（`INK+(190,)`）保证可读。（Film02 曾把中文设成暗墨，被用户判"和英文不统一"，已改。）
- ⚠️ **logo lockup 别贴米色带顶**：`row_cy` 留 ≥130px 米色余量（现 1200，band 999..1350），上方留呼吸空间。（Film02 用户要求"logo 往下一点"。）
- ⚠️ **平台非 9:16 封面（3:4 / 1:1 / 4:5）截上半部：用等比 scale 再 crop，绝不用 resize 直接拉（会变形！）**。例：4:5 = `scale` 到 1080×1920 再 `crop` 顶 570px。
- logo 抠背景：`dist=sqrt((arr-bg_ref)^2).sum(2)<45` 生成 alpha 蒙版，用 `Image.alpha_composite`（需保持 RGBA 链）。

### 4. 关键坑（已踩过，必记）

- range 转换必须 `scale out_range=tv`（见上）。
- ⚠️ **基础调色是精剪第 8 步强制项，不可跳过**：每期必须在所有片段过 `GRADE` 滤镜（`eq=contrast=1.06:saturation=1.05:brightness=0.005,colorbalance=rs=0.02:gs=-0.01:bs=-0.03:rm=-0.01:gm=0.0:bm=0.02` 统一混合源色调）。Film02 V07 曾漏做被用户抓（"按纪律你该检查+调色了"），V08 已补；以后每期必跑，不许再漏。
- **模型不读图**：视觉校验全靠 `ffprobe`(scdet 镜头数) / PIL 像素采样（品牌蓝检测 `(b>90)&(b>r+25)&(b>g+25)`）/ `whisper` 转写还原 VO，**禁止靠「看图片」做验证**（曾因此虚假验证 v5–v8）。
- 素材自带音频轨（iPhone .mov 的 pcm_s16le）会泄漏进最终音频覆盖 VO → 中间步骤全程 `-an`，mux 显式 `-map 0:v:0 -map 1:a:0` 锁定 VO。
- BGM 署名（CC BY）强制，四平台发布须保留（法律强制，非站外引流）。
- 品牌护栏：不写 Sri Lanka 地缘、不绑冲浪功能、不引导站外。

### 5. 发布交付工作流（精剪定稿后必走 · 封死）

成片 + 五平台版 + 封面 + 发布草稿 必须**一并交付**，不交付 = 未完工。

- **交付物**：母版 mp4 + 五平台版（XHS / Douyin / WechatChannel / Instagram / YouTube，由母版派生 remux+faststart，不重剪）+ 各平台尺寸封面（`make_cover.py` 出）+ 一个 `to_publish_*.md` 草稿。
- **草稿位置 + 命名**：放 `05_CONTENT/03 drafts/`，文件名以 **`to_publish_`** 开头（发布助手唯一扫描入口，见 `98_Windows_work/03_发布助手/🧷 发布助手_岗位规范_20260731.md`）。命名 `to_publish_<标识>.md`；**发布日期未定时省略日期段**（如 `to_publish_Film02_DUODUO-WEAR.md`），日期**留空不写**，待多多定档后回填。
- **状态闸门（铁律）**：发布助手**只在状态 = `approved` / "多多已确认" 时才发布**。交付时若未批准，状态写「发布准备包就绪 · 待多多确认」，**切勿标 approved**，否则会误发。
- **必含章节**：母版路径 + 五平台版路径 + 各平台封面路径（尺寸匹配）+ 逐平台 标题/正文/标签 + BGM CC BY 署名（法律强制）+ 品牌护栏（不写斯里兰卡/不绑冲浪/不站外）+ 发布前自检 + 发布记录表（发布后由发布助手追加，不覆盖原文）。
- ⚠️ **doc 与封面文件名严格一致**：`make_cover.py` 实际输出文件名（如 `Film02_Cover_IG.jpg`）即 doc 引用的名字；旧版改名残留（如 `Film02_Cover_Instagram.jpg`）**必须删除**，否则发布助手会拿错旧封面（Film02 已踩：doc 引旧名、文件夹留旧文件，已修）。
- ⚠️ **封面尺寸映射**：Final / IG = 4:5(1080×1350) / XHS = 3:4(1080×1440) / Douyin·9x16 = 9:16(1080×1920) / Shipinhao = 1:1(1080×1080)。
- **IG / YouTube 海外网络**：Windows 发布助手无海外网 → 这两平台在 doc 里标「暂停·待决策（Mac 发 / 配代理）」，不擅自发。
- **文案来源诚实标注**：若 VIDEO_BRIEF / 剪辑计划里无逐平台文案（常见），草稿里必须写明「文案为内容运营按原声语气起草的草稿，非 script 现成，待确认」，不得假装 script 自带。

## 交付前硬检 · 无静音头（2026-08-05 用户铁律）

「开视频直接开始说话」——成片 + 五平台版交付前，必须保证 VO 从容器 t=0 开始，**绝不能**有开头静音空白。

- **检测**：`ffmpeg -i <片> -af silencedetect=noise=-30dB:d=0.3 -f null -`（ffprobe 不可用，用 ffmpeg stderr 读 `silence_start`/`silence_end`）。若 `silence_start: 0` 且 `silence_end > 0.3s` → 有开头静音头。
- **裁剪（无损）**：`ffmpeg -y -ss <lead> -i <片> -c copy -movflags +faststart <片>`（input-seek + 流拷贝，不重编码；`<lead>` = silence_end 秒数）。裁后复检：应无 `silence_start: 0`。
- **只裁开头**：句子之间的自然停顿（silence_start 在几秒后）**不要动**，那是正常呼吸/断句。
- **根因**：多为 VO 文件自带静音头。渲染管线应在 mux 后统一裁掉（参考 `render_ep3.py` 的 `trim_lead_silence()`，放在五平台副本生成之前，副本自动继承）。
- **适用所有 Film**（Film01/02/03/…）：这是交付闸门，不是单期特例。

## VO 收紧 SOP（振幅验停顿 + EDL 复查 · 2026-08-06 吸收 xiaolan-auto-edit）

> 来源：xiaolan-auto-edit 的 `xiaolan-aroll` 方法（faster-whisper 词级 + 脚本 ground truth + **RMS 振幅验停顿** + select/aselect 音画同步 + 强制 CFR）。结合多多约束收敛后落成本 SOP。

**核心原则**：停顿检测用**振幅（RMS / silencedetect）**，不用 whisper 词间隙——whisper 会把词尾拉伸进静音、漏掉真停顿，导致该压的没压、不该压的误压。

- **双档标准（默认只裁头，可选压句中）**：
  - 开头静音头 → 直接裁（见上方「无静音头」闸门，无损 stream-copy）。
  - 句中停顿 `>0.15s` → 压到 `0.10s`（**可选**，仅干净录制旁白才用；蒙太奇句子间自然呼吸**保留**）。
  - 句末停顿 `>0.25s` → `0.20s`（可选）。
  - ⚠️ 多多 VO 多为策划式干净旁白，默认**只裁头 + 保留句间呼吸**，不激进压句中，避免机械感。
- **实现**（ffmpeg，防音画漂移）：用 `select`/`aselect` 在同一区间切，并**强制 CFR** `-r <fps>`（如 `-r 30`）；不要只切音频不锁帧率。
- **EDL 复查清单（必出）**：每次自动修剪都输出一份 `keep/cut` 日志（JSONL，含区间/时长/原因），放 `FilmXX_Production/` 下，方便扫查。自动删东西必须可复查，不偷偷删。
- **❌ 不适用（明确不搬）**：xiaolan 的「喊卡重说 / 去废 take / 重复 retake」流程——多多是策划式蒙太奇，无 raw 口播「喊卡」素材，此能力不实现。
- **踩坑记法**：见 `references/video_lessons.md`（带日期的错题本，违反即补一条）。

## 泳衣线视觉规范（DUODUO WEAR 现行品牌片规范 · 2026-08-07 确立，统一给所有 Film）

> EP3 实践后确立，取代早期 Film01「清新风」作为品牌片默认。Film01 已发布成片保留为历史特例，新片一律本规范。

- **字幕（烧录）**：ASS 单条 `中文\N{\fnGeorgia\fs48}英文`，中英文**同行同屏**（同一 MarginV 定位框，杜绝中文压英文）；中文 Songti（**不是 "Songti SC"**，EP2 黄金样式即 `"Songti"` + Bold=-1）52 + 英文 Georgia 48；蓝字 `#2E27A8`；米底 `#C4AE84` alpha `A0` 实底框（BorderStyle=4）；`MarginV=540`（下三分之一偏上）；句级一次一句（按 `. ,` 切原子句）中英同步；时间轴取自 faster-whisper 句级转写。
- ⚠️ **字幕对齐铁律（血泪教训，勿犯）**：字幕时间轴**只能取 faster-whisper 句级真实边界** `[(start,end,text)]`（每段自带正确起止时间，是天然句子/从句断点）。每段按**词内容重合(Jaccard)匹配脚本句、并强制单调不降**（你顺序说→每句拿到一段连续真实语音，绝不回跳）→ 同一脚本句的相邻段**合并为一屏**（时间=该句真实语音首尾）。数学上**不可能重叠/滞后/重复**。每一句一屏：`中文(脚本译文) + 英文(脚本定稿)` 同一行（`中文\N{\fnGeorgia\fs48}英文`），英文过长屏内折行(≤40/行)，中文每屏必有。
  - 🚫 **绝对禁止**：① 把字幕拆成「中文一条 + 英文一条」两条 Dialogue（相邻段会互相覆盖 → "上下两个不同字幕"）；② 用 Jaccard 匹配段后取 min/max 合并时段（一段语音可能匹配到**非连续**句子 → 时间跨度横跨 → 两句重叠 + 后句被推后）；③ 把词流按「脚本句长比例」切成 N 块（比例累积漂移 → **从第 2 句起就和旁白对不上**，实测翻车）。**正确做法 = 句级段 + 单调内容合并**（见上条）。
  - 验证必须**程序硬查 subs.ass**：重叠(下句起点<上句终点)=0、停滞空白窗(间隔>1s)=0、缺中文屏=0、零时长=0、开头延迟>1s=0。**禁止靠肉眼/看图片假验证**（曾虚假验证 v5–v8）。
- **调色（莫奈珠光 + 高对比抗糊）**：美图秀秀 VC3/VC5 莫奈珠光基底 + ffmpeg 高对比去主柔焦，杜绝纯磨皮柔焦糊片：
  `eq=contrast=1.20:saturation=1.22:brightness=0.010:gamma=0.98,colorbalance=rs=0.03:gs=-0.02:bs=-0.04:rm=-0.02:gm=0.01:bm=0.03,split=2[a][b];[b]gblur=sigma=18[blu];[a][blu]blend=all_mode=screen:all_opacity=0.10`
  （暖金高光 + 青蓝阴影 + 大模糊亮层 screen 弱珠光闪）。过曝安全 YAVG<200。
- ⚠️ **与 Film01 清新风的区别**：Film01 用 Hiragino + 柔和 shadow + 干净少女感调色（contrast 1.06），**已非现行规范**；早期「清新风直出流水线」小节同理标注为泛用非品牌默认。新片不要沿用。

## 旁白片字幕对齐流水线（render_narrated_ep.py · EP8/9/10 专用 · 2026-08-11 立，EP8 V13 定稿）

> 适用「用户录音 VO + 脚本中英 + 素材」的旁白型成片（EP8/9/10，区别于 Film01/02 的镜头蒙太奇）。核心目标：**字幕与旁白严格同步、一次只一行英文、中文绝不半句截断、零重复零延迟**。以下为本流水线踩出的全部标准与意难杂症，违反即查本文件 + `references/video_lessons.md`。

### 一、时间轴标准（字幕同步的根）
1. **转写只用 faster-whisper `small` 模型**（段级 `transcribe_segments` + 词级 `transcribe_words_cached`），并**按 VO 文件 mtime 缓存 JSON** 防非确定性漂移。
   - 🚫 **禁用 `medium`**：实测 medium 段起点系统性晚 ~1s 且把 2–3 句并成一段 → 字幕挂太久 + 缺句（用户感知=延迟+少字幕）；medium 词级时间戳还会前压（前几句压到 0–4s）→ 与真实朗读错位。
   - small 段级与词级时间戳均准确单调，是字幕时间轴唯一权威。
2. **每屏时间 = 词级真实时间戳**（`_time_group_clauses` 把单元内英文小句按词数连续映射到该单元词流的逐词真实起止）。**绝不用「词数比例」猜时间**（`dur=(ge-gs)*wts[k]/sw`），那会累积延迟 + 像重复（V08→V09 真凶）。
3. 结构：`build_subtitle_rows` 以**每条 whisper 段为一屏骨架**（段数=屏数=真实语音短语数）；段内英文 `_split_clauses`（≤40 字符单行）拆多屏；中文按内容**单调**匹配脚本对应句（不串句）。`zh_merge` 只用于中/英行数对齐，不影响时间轴。

### 二、ASS 烧录标准（物理同步的硬约束）
4. ⚠️ **ASS 时间码必须用两位百分秒 `H:MM:SS.cc`**（`hms()` 锁定 `f"{h:02d}:{m:02d}:{s:05.2f}"`，如 `00:00:00.11`）。
   - 🚫 **三位毫秒 `00:00:00.110` 是灾难**：libass 解析三位小数会把开始时间错移、且**不识别 End 时间** → 旧字幕赖着不走、越堆越多 = 用户看到的「延迟+重复」（V10→V11 真凶，独立烧录黑底实验已复现）。
5. 样式：ASS 单条 `中文\N{\fnGeorgia\fs48}英文`，中英文同行同屏（同一 MarginV 框，杜绝中文压英文）；中文 Songti + Bold=-1 52、英文 Georgia 48；蓝字 `#2E27A8`；米底 `#C4AE84` alpha `A0` 实底框（BorderStyle=4）；`MarginV=540`。

### 三、中文拆分标准（杜绝半句截断）
6. ⚠️ **中文绝不按字数硬切**。改为按**标点（，。：、；！？）+ 连接词**（而是/但是/但/就是/所以/并且/以及/加上/还有/尤其/特别是/换句话说/换句话/就）自然断（`_split_zh`）。英文屏数**迁就**中文片数（英文相邻合并、中文相邻合并），保证中文永远完整。硬切会导致"最担心的不是自。""是泳衣会不。"这类残缺句（V11→V12 真凶）。

### 四、交付验证标准（之前反复假验证翻车）
7. **三层验证缺一不可**：
   - ① 程序硬查 `subs.ass`：重叠（下句起点<上句终点）=0、停滞空白窗（间隔>1s）=0、缺中文屏=0、英文超宽屏=0、重复中文屏=0。
   - ② **端到端**：渲染后把**成片音轨重转写（small）**，与烧录字幕窗逐条比对起播偏差 <0.6s（缩写撇号 `isn't→isn/t`、品牌音译 `dodo→duoduo` 须归一化否则误报）。
   - ③ **抽真实帧读图**（模型不读图）：抽 10s/20s/50s/70s 等关键帧用 Read 工具看烧录进视频的字幕是否真的在那个时间点出现、是否一屏一行、中文是否完整。**禁止只看 ASS/缓存/重转写就宣称"同步 OK"**——V5–V10 全栽在这（代码层自洽 ≠ 成片层对）。

### 五、版本清理标准
8. ⚠️ 重渲时**删所有同集文件**（含无版本号的时间戳遗留 `Film8_20260811_021814.mp4` 这类），不能只删 `Film{ep}_Vdd`。否则用户会反复打开旧 bug 片误判"又出问题"（V09/V10 期真凶）。

### 六、尾卡 + DW 人声标准（视觉/听觉收尾）
9. **尾卡**：背景必须用品牌米底 `0xECCEB6`=(236,206,182)，不能用 `CREAM=[241,233,218]`（太浅发灰）；只保留 logo lockup，**禁额外画一行黑色 Georgia 字体 "DUODUO WEAR"**（与 lockup wordmark 重复，V12→V13 修）。
10. **DW 品牌人声**：源 = `Film01_Production/V06_MASTER_Film01.mp4` 中真实 "Doodoo wear." 在 **39.02–40.12s**，脚本截取 **39.0–40.2s**（去尾静音，40.2–40.5 是静音勿混）；**延迟 0s**（尾卡第一帧即出声）；boost 6.0。🚫 严禁截 39.0–40.5（含尾静音稀释人声）+ 延迟>0（人声滞后错过），这是"少人声"根因（V12→V13）。

> 完整踩坑时间线见 `references/video_lessons.md`（2026-08-11 系列）+ 项目 MEMORY.md 第⑮条。

### 七、覆盖机制（hook / back_replace / screen_replace · EP9/EP10 沉淀）

> 三类覆盖都在 `main()` 素材分配后、渲染前注入，互相独立可叠加。目的是**修特定屏而不动整体节奏**。

1. **`hook`（CONFIG 列表）**：把开头 `start < 10s` 窗口**整体替换**为指定片段。
   - EP9 用：原槟城开头含父母正脸 → 换成斯里兰卡泳衣+urban 视频（本地 llava 筛查单人、无他人正脸）。封面同步用 hook 首段帧。
2. **`back_replace = {start, clips}`**：把 `≥ start` 时间码之后的**所有屏整体替换**（按 clips 顺序循环填充）。
   - EP9 用：1:04（64s）之后旁白提 swimsuit 处原是无关槟城片 → 换成斯里兰卡单人比基尼海滩视频，满足「凡提 swimsuit 必有人穿泳衣」铁律。
3. **`screen_replace = {屏序号: 片段}`**：按屏序号**定点**替换单屏，不动相邻屏（最精准）。
   - EP10 用：第 [7] 屏旁白「一件泳衣怎样从早上穿到晚上」分配到非泳衣片 → 定点换成已确认泳衣的 `72234`；第 [8] 屏本就是泳衣片不动。
   - 🚫 提 swimsuit 的屏**绝不能**用非泳衣片段——这是 EP9 用户铁律，覆盖时优先用 `screen_replace` 精准修。

### 八、素材精选池 + 隐私筛查（EP10 沉淀 · 用户授权 iCloud `以前照片/`）

1. **`src` 指向 `_curated_src` 精选池**：从原始库（如 `斯里兰卡/`）复制来的**子集**，不是全库。全库含大量陌生人正脸，直接喂会踩隐私红线。
2. **本地 llava 单帧严格 JSON 筛查**（`llava-llama3:latest`，照片/视频不外传）：只收 **OTHER=False（无他人正脸）** 的片段；其余检出他人正脸的全部剔除。**绝不赌"应该没问题"**。
   - 问法刚性：输出必须 `SWIM:yes/no` + `OTHER:yes/no`，只采信干净解析；含糊/缺字段一律剔除。
   - 单帧可能漏掉后期出现的陌生人 → 仍由用户实机播终核，但精选池已把风险降到最低。
3. **跨集去重**：精选池排除上一集已用的片段（EP10 排除 EP9 用过的 8 段），防跨集重复。
4. **全视频零图片**：旁白片若精选池只有视频，`assign_media` 守卫空图片池 → 全屏用视频，更隐私安全（EP10 实测 25 屏全视频）。
5. **`assign_media` 循环复用修复**（EP10 踩坑）：池子片段数 < 屏数时**循环复用**（同集复用允许，跨集才禁）+ 守卫空图片池防越界崩溃。

### 九、交付给用户的纪律（2026-08-11 EP10 定稿后用户明确 · 写死）

1. ⚠️ **只交付成片视频 + 封面**。联系表（contact sheet）是**我内部的 QA 工具**（自检/抽真实帧读图用），**绝不再作为交付物 present 给用户**，除非用户主动要求。
2. 用户自己**实机播成片**即可确认画面（无陌生人正脸 / 泳衣屏有泳衣）。模型不读图，contact sheet 给我看也是假验证（见 L7），不该转嫁成用户负担。
3. 交付话术固定：① 哪集哪版；② 时长/规格（如 84.9s·25屏·3:4）；③ 自检过哪几项（单音轨/无黑帧/DW峰/dedup/字幕同步）；④ 用户必做（实机播确认）；⑤ 有未决点才列。不堆过程、不贴联系表。

## 品牌固定 Outro 铁律（所有 DUODUO WEAR 视频 · ★非 negotiable· 2026-08-09 用户再次明确「写死」）

> 🔴 **这是硬铁律，不是建议，不是可选项。** 每一个 DUODUO WEAR 视频（含 EP1–EP7 及以后所有期）结尾**必须**同时具备以下两项，缺一不可交付；不每期重议、不省略、不"本期换个做法"。
> 2026-08-09 用户原话：「加 duoduo wear 和背景音这个要求写死在记忆和 skill 里」+「duoduo wear 大一点。背景声音小一点。」

1. **结尾必叠品牌人声「DUODUO WEAR.」**
   - 取自 `Film01_Production/V06_MASTER_Film01.mp4` 中真实 "Doodoo wear." 的 **39.0–40.2s** 段（40.2–40.5s 为尾静音勿混，否则人声被稀释）。
   - **增益 boost ≥ 1.8×**（2026-08-09 起：用户要"大一点"，原 1.4× 已上调；如需更突出可到 2.0×）。
   - 压在 logo 尾卡起点（建议 0–0.3s；旁白片 EP8 用 0s 即从第一帧出声，避免人声滞后错过）。
   - 验证：专属 ~0.8s 窗口 `volumedetect` **峰值 > −12dB** 且**明显大于 BGM 峰值**（差 ≥ 4dB）。
2. **结尾必铺品牌固定 BGM（LolaMoore《Serene Acoustic Guitar Melodies》CC BY）**
   - **仅最后 5–15s 起放**（用 `adelay` 推后到 `TOTAL-15` 秒起，前面旁白/主体段落**纯净无 BGM，绝不全程铺底** —— 2026-08-09 用户纠正 EP3 全程 BGM 违规）。
   - **增益 ≤ 0.22**（2026-08-09 起：用户要"小一点"，原 0.40 已下调）。
   - 结尾淡入淡出（`afade=in:st=TOTAL-15:d=1.5, afade=out:st=TOTAL-1:d=1.0`）。
   - 发布必须在描述/评论保留 CC BY 署名（法律强制）：`Music: "Serene Acoustic Guitar Melodies" by LolaMoore (CC BY) — freesound.org/people/LolaMoore/sounds/762604`。
3. ⚠️ **音频签名例外**：此条是用户授权内的「音频品牌签名」复用于所有视频，**不违反「禁止跨期复用素材」红线**（红线只禁上期精剪**画面镜头**原样塞本期）。同曲 BGM + 同句人声 = 品牌一致性要求，例外放行。
4. 实现坑（adelay 毫秒换算 / atrim 取 10s 勿 12s / alimiter 只认 limit=）见 `reel-grid-pitfalls` skill 第 5 节。
5. ⚠️ **峰值验证姿势（2026-08-07 教训）**：验证结尾人声清晰可辨，**必须用专属 ~0.8s 窗口 `volumedetect` 验峰值 > −12dB**；绝不靠宽窗口 `mean_volume`（会被 VO 尾音稀释成看似"够响"实则人声被盖）。参考 `render_ep3.py`/`fix_ep5_outro.py` 的专属窗口做法。

### 交付前自检清单（每片出片前必逐项核验，缺一不可交付 · 2026-08-09 用户列项）

| # | 检查项 | 验证方法 | 通过标准 |
|---|---|---|---|
| 1 | **字幕** | 看 ASS 烧录结果 | 双语、中英文同行同屏、Songti米底蓝字、MarginV=540、按本期脚本、与 VO 句级同步 |
| 2 | **背景音** | `volumedetect` 分段 | BGM 仅最后 5–15s 有；前面主体段无 BGM 床；BGM 增益 ≤0.22 |
| 3 | **音画同步** | 抽帧 + 听 | 画面/字幕/口播随旁白节奏；body 由旁白真尾点(silencedetect)决定，无死画面 |
| 4 | **素材内容对照** | face_id QA + 人工 | 每镜 on-theme(泳衣/海边/多多)；无重复镜头(本期内 & 跨期)；无空镜/废帧 |
| 5 | **DUODUO WEAR 出现** | `volumedetect` 专属窗 | 结尾品牌人声峰值 >−12dB 且明显大于 BGM；尾卡 LOGO 米底 |
| 6 | **封面不重复** | `check_cover_collision` | 背景照不与 ep2(IMG_8208)/ep3(SL2603_WALK_70524)/ep5(SL2604) 撞图 |

## 导演纪律漏斗（每期必走 · 2026-08 由 Agent Package 合并入本 skill，唯一权威）

> 2026-08 用户指令：把 `duoduo-video-director` 合并进本 skill，**只留 edit**。原 vault 包 `Duoduo_Video_Agent_Package_20260730` 的纪律已全量固化于此，不再作为独立技能依赖。

每一期（Film01 / Film02 / …）是独立项目，必须从 VIDEO_BRIEF 走完整漏斗，**禁止跳步、禁止跨期复用素材**：

1. **VIDEO_BRIEF**：账号 / 平台 / 类型 / 目标时长 / 画幅 / 截止 / 为什么存在 / 真实事件 / 核心情绪 / 核心问题 / 认知落点 / 观众动作 / 与产品关系 / 必须保留 / 禁止出现 / 参考片 / 验收标准。
2. **素材审计**：有什么、缺什么、真现场 vs 补拍、授权风险、事实强 vs 只是漂亮、各镜头承担 Hook / 环境 / 证据 / 转折 / 停顿 / 结尾。
3. **SELECTS**：最真实瞬间 / 最强视觉 / 最强原声 / 最强一句 / 地点 / 关系 / 动作 / 情绪 / 过渡 / 环境声 / 不能用及原因。
4. **导演判断**（写脚本前）：素材真支持什么故事？原计划是否被素材否定？Hook / 情绪曲线 / 结尾？哪些缺口必须补拍、哪些该接受而非伪造？
5. **PAPER_EDIT**：时间码 / 可用原声 / 可删重复 / 不可删停顿 / 事后补充 / 调序(是否改原意) / 事实核验 / B-roll 功能 / 预计时长。
6. **开场校准样片**（15–30s，第一轮）：同核心内容测 人脸开场 / 物品动作开场 / 语音开场 / 现场声开场 / 快慢节奏；内部排除明显不适合再公开测试。
7. **粗剪 V01**：只解决 故事懂不懂 / 前几秒进入 / 情绪成立 / 信息够 / 结尾完整 / 时长。不沉迷动效转场调色字体音效包装。输出 `V01_ROUGH_CUT` + `V01_REVIEW_NOTES.md`。
8. **精剪**：结构确认后才做 节奏 / 停顿 / 反应镜头 / 环境声 / 人声清理 / 音乐 / 字幕 / 基础调色 / 图形 / 平台适配。**含固定品牌 Outro（见下方「品牌固定 Outro 约定」）：最后 5–10s 起放品牌 BGM + 结尾配 ep1「DUODUO WEAR.」人声 —— 所有视频统一且必须，不每期重议。**
9. **平台版本**：从 Master 派生（XHS / Douyin / WechatChannel / Instagram / YouTube），不重剪。
10. **复盘**：选题 / 形式 / 开头 / 时长 / 发布时间 / 播放 / 前几秒留存 / 完播 / 互动 / 制作耗时 / 是否愿再做 / 一次性反馈 / 账号规则 / 长期偏好。

⚠️ **跨期复用红线（用户铁律）**：每期独立审计 + SELECTS + PAPER_EDIT。原始库（如斯里兰卡库）可共用，但**选片文档不能复制上期**；更严禁把上期精剪镜头原样塞进本期。判别"同画面/同场景"：以上期 SELECTS 的 IMG 编号集合为排除集，本期只从补集挑；相邻 burst 同场景也避开。模型不读图，无法自证画面内容时，产出后必须交用户实机播确认，不谎报"已验证"。

## 每期纪律红线（2026-08 用户纠正，必读）

每一期（Film01 / Film02 / …）都是独立项目，必须从头走完完整纪律漏斗，禁止走捷径：

1. **禁止跨期复用素材**：绝不能直接把上一期的 SELECTS / 精剪镜头原样塞进本期。每期必须对自己的 brief 做**独立素材审计（MATERIAL_AUDIT）→ 独立 SELECTS → PAPER_EDIT**。共用原始库（如斯里兰卡库）可以，但必须按本期命题重新定向筛选并成文，不能复制上期选片文档。
2. **字幕是最低交付**：Level 1 起每片必须出双语烧录字幕（中英），且按本期脚本标重点（如 Film02 只标「使用身体 / 进入场景 / 生活动作」）。无字幕 = 未交付。
3. **本期要求必须同时用到**：脚本里的「推荐形式 / 必要补拍 / 剪辑规则 / 发布前检查」是验收标准，不能只做其中一项。
4. **漏斗顺序不可跳**：VIDEO_BRIEF → 素材审计 → SELECTS → 导演判断 → PAPER_EDIT → 开场校准样片(15–30s) → 粗剪 → 精剪 → 平台版 → 自检报告。跳过审计直接粗剪 = 违规（本次已踩）。
5. **模型不读图**：审计靠联系表 + CSV + 已知动作描述交叉验证；无法自证画面内容时，产出后必须交用户实机播确认，不谎报「已验证」。

## 剪辑流水线人脸 QA 与素材预处理硬坑（2026-08-07 吸收 EP3 三版迭代）

> EP3 海边段反复出现「源核验=多多、渲染同窗口=空镜」的废帧，定位根因后固化以下纪律。

1. **VFR 源 `-ss` seek 错位 → 人脸 QA 必须 render-time（或转 CFR）**：
   - 源素材是 VFR 时，源上抽帧核验与渲染同一窗口会命中**不同物理帧**（关键帧 snap），导致核验过的窗口渲染出空镜/非多多 → 废帧进片。SKILL 现有「关键坑」只写了 iCloud 别用 ffprobe（超时），**漏了这条**。
   - 根治：① 候选窗口先渲染样片（CFR 30fps，seek 精确）对样片自身极密核验（render-time QA）；或 ② 先把源转成 CFR 本地副本再核验/渲染。
2. **QA 阈值纪律（致命）**：样片核验用「含多多帧 ≥55% 通过、空镜(0%)必淘汰」，**绝不能要求全帧都识别到多多**——真实素材多多会眨眼/转头/被浪花挡，全帧要求必全淘汰 → 触发兜底退回未筛选坏窗口 → 废帧原样进片（EP3 V06 因此翻车）。全淘汰时**不退回未筛选坏窗口**，降级到源核验通过窗口或 drop。
3. **核验一致性**：流水线内动态抽帧核验必须与渲染用**同一 embedding pickle + 同一阈值(0.75)**，否则阈值不一致会误报/漏报。
4. **时间轴死画面根因**：body 长度由旁白**真正结束点**决定（silencedetect 找，不是 VO 文件时长）。`sea_total_target = vo_dur − 前部实际时长 − 停顿`；品牌人声/尾卡起点压到旁白真正结束点。拿 VO 文件时长硬撑 body 会多撑 2s 死画面（EP3 中期用户投诉「1:12 旁白停、1:15 品牌才出、中间死画面」根因）。
