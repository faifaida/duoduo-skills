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
- `3D模型与视频特效`：转场/特效片段（拥抱/变身/万物归尘模板）。

## 清新风直出 MP4 流水线（ffmpeg 替代剪映渲染 · 用户要"直接给成片"时用）
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
