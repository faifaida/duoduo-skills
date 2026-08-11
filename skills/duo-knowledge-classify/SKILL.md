---
name: duo-knowledge-classify
description: 多多个人公司「碎片知识统一加工系统」总入口——把任何来源的碎片内容（小红书收藏、微信读书划线、微信聊天记录、云盘/本地归档、课程笔记、文档）按知识生命周期采集、分类、去重、提炼进 Obsidian Vault 的 00_SOURCES 与 02_TOPIC_MAPS。触发词：整理小红书、同步收藏专辑、微信读书划线、读书笔记、导出微信聊天、整理云盘、重分类归档、网盘整理、把内容归纳进 knowledge work、周度采集、碎片知识加工。覆盖四条通道：小红书(签名引擎增量同步) / 微信读书(原地追加合并) / 微信聊天(限定范围导出) / 云盘归档(rclone+文本抽取+重分类)。
agent_created: true
---

# 多多 · 碎片知识统一加工系统（duo-knowledge-classify）

一个 skill 管全部知识入库。**平台只是来源，按知识生命周期管理，不按平台建独立知识系统。**

> 执行包全本：`com~apple~CloudDocs/懒懒岛/ip/多多_碎片知识统一加工系统_资料员执行包_v2/`
> 资料员长期记忆：`~/.workbuddy/plugins/marketplaces/my-experts/plugins/duoduo-researcher/MEMORY.md`

---

## 一、总纲：一行判断法

```
别人说什么          → 04_KNOWLEDGE WORK/00_SOURCES/<平台>/
我怎么理解          → T02 学习笔记
多个来源共同说明什么 → 02_TOPIC_MAPS/T10_<主题>知识地图.md（≥3 个同主题来源才建）
我要现实验证什么     → 03_ACTIVE PROJECTS/（T11 现实实验）
我准备如何对外表达   → 05_CONTENT/01 ideas
未来长期要记住什么   → 06_AI_WORKBENCH/AI_OUTPUTS TO REVIEW/Context更新建议/
```

**真实路径注意**：执行包文档写 `04_KNOWLEDGE_WORK`（下划线），真实目录是 `04_KNOWLEDGE WORK`（空格）。一律用真实路径。

---

## 二、四条通道（选一条进 references）

| 通道 | 场景 | 细则 |
|---|---|---|
| **A · 小红书** | 收藏专辑增量同步、失败页重抓、增删专辑 | `references/01_小红书通道.md` |
| **B · 微信读书** | 划线 → 拆书文件 + 每周原地追加、读书笔记 | `references/02_微信读书通道.md` |
| **C · 微信聊天** | 限定范围导出聊天记录 → Markdown | `references/03_微信聊天通道.md` |
| **D · 云盘/本地归档** | Google Drive/网盘/课程笔记重分类 + 知识提炼 | `references/04_云盘归档通道.md` |

**Properties 字段 / 红线 / 验证规范（全通道共通，必读）**：`references/05_共通规则.md`

---

## 二-B · 大外部源整理：Topic Map ↔ Research 双层归位（2026-08 百度网盘实战提炼）

整理**体量大的外部源**（整盘百度网盘 / Google Drive 大库 / 本地归档大堆）时，产出分**两层**，别再像早期那样把 topic map 错塞进 Research、或套错模板：

### 两层定位
- **Topic Map 层 = 资产 / 分类索引** → `04_KNOWLEDGE WORK/02_TOPIC_MAPS/`
  - frontmatter：`type: topic-map` + `map_type` + `corresponds_to`（绑一个主 R）+ `related`（指向所有相关 R）+ `status: developing`。
  - 内容只承载：分类索引（总览表 + 各分类明细）+ 清理 / 去重结果 + 操作注意事项 + 待核对事项。**不承载消化后方法论。**
- **Research 层 = 消化后方法论 / 生活主题** → `04_KNOWLEDGE WORK/03 Research/`
  - frontmatter：`type: knowledge-note` + `source` + `status: to-review` + `ai_inferred` + `usage` + `related`（指回对应 T）。
  - 新写一律 `status: to-review`，**不改正式知识**，待多多核完升 `finalized`。

### 归位决策（先列清单跟多多对齐，再动手）
| 外部源里的内容 | 落到 |
|---|---|
| 资产 / 分类索引 / 清理结果 | **02_TOPIC_MAPS**（topic map） |
| 消化后方法论 / 生活主题，**已有对应 R** | **补进已有 R**（append 一篇补充笔记，link 回 T） |
| 消化后主题，**vault 里无对应 R** | **新建 R**（命名 `Rxx_主题`，如 `R12_拉斐猫健康` / `R13_人性`） |
| 纯消费 / 素材（影视、照片归档、软件工具教程等） | **只在 topic map 标位置，不进 Research** |

### 模板铁律（踩过坑）
- ❌ **绝不用 `T04_每周复盘` 模板**写 topic map 或 research（月相 / 周计划九节是错的，早期百度云整理踩过）。
- ✅ topic map 用 `type: topic-map` 那套；research 用 `type: knowledge-note` + `source / status / ai_inferred / usage / related` 那套（与 `R2_ESG`、`个人故事素材` 等现有 research 同款）。详见 `references/05_共通规则.md` §10。

### ⚠️ 红线 #9 的适用范围澄清
常态增量采集（A 小红书 / B 微信读书）**仍禁止碰 03 Research**（已有 R 的结构 / Properties 不乱动）。但**大外部源整理（D 通道）走本双层归位**——允许「补进已有 R / 新建 R」，前提：① 只 append 补充笔记、不扰动已有 R 既有内容与 Properties；② 新 R 全部 `status: to-review`；③ 纯消费 / 素材只在 topic map 索引。

### 提取时的事实 / 推断标记
从日记 / 原始素材提炼进 research 时，沿用资料员六原则：原文事实标 `[原始事实]`、对事实的解读标 `[你的理解]`、非原文直接出现的归纳标 `[AI推断]`，并回溯到具体来源日期 / 文件。

---

## 三、批量前必做（00_START_HERE，不可跳）

1. 查看实际 Vault 目录（别照搬文档里的路径）。
2. 读本 skill 对应通道 references + 资料员 MEMORY.md。
3. 统计平台 / 时间范围 / 预计数量。
4. **先处理 10 条代表样本**。
5. 汇报分类结果、误判风险、预计完成时间。
6. **获得多多确认后再批量执行。**

> 例外：纯增量周度采集（已跑通的自动化）不用再走样本确认，直接跑。

---

## 四、红线（绝对不做）

- 删除或覆盖原始资料。
- 直接修改 `02_CONTEXT`（多多个人背景库）。
- 把 AI 推断写进 `why_saved`（那是多多自己的字段，永远留空待她填；AI 推断进 `ai_inference`）。
- 把外部资料当多多原创；自动发布 / 售卖外部内容。
- 批量改名、移动或修改已有 Properties 结构。
- 整盘平铺进一个新建的「归档」文件夹（多多明确反感）。
- 碰 `04_产品经理/她局/`（产品经理的产品）与 `04_KNOWLEDGE WORK/03 Research/`（已整理过的主题夹）——**常态采集（A/B 通道）下禁止**；但**大外部源整理（D 通道「双层归位」）允许补进已有 R / 新建 R**，见上方「二-B」。新写 R 一律 `status: to-review`，只 append、不扰动既有内容与 Properties。

---

## 五、交差前自检（多多明确要求）

能实测的就实测，不许「以为成功」：

- 数量核对：源计数 vs 落盘计数，差额要能解释（同名折叠 / 服务端隐藏 / 失败页）。
- 抽查 3–5 篇产物：frontmatter 完整、正文非空、无 `[[ ]]` 混进 YAML。
- 去重状态文件是否更新。
- 回报写 `03_资料员/回报_YYYYMMDD.md`（**当天只写一份，追加，不按主题拆多份**）。

---

## 六、脚本位置

```
~/.workbuddy/skills/duo-knowledge-classify/scripts/
  xhs/                 主力小红书引擎（Spider_XHS 签名 + Chrome 枚举）
  xhs_legacy_dom/      旧 DOM 抓取方式（已被签名 API 取代，备查）
```
微信读书合并脚本在 Vault 内：`03_资料员/tools/weread_merge.py`

---

## 七、关联自动化

| 自动化 | 节奏 | 用到的通道 |
|---|---|---|
| `automation-1785345604974` 资料员·周度采集 | 每周二 9:00 | B + A |
| `automation-1785360673928` 小红书失败页重抓 | 一次性（PAUSED） | A |
| `automation-1784568836921` 小红书收藏每周导入 | 每周一 20:00（PAUSED，待决去向） | A |

> 依赖的外部工具 skill：`weread-skills`（微信读书 API 数据源，**保留勿删**）。

---

## 八、外部依赖（非本 skill 自带，误删会断采集）

| 依赖 | 是什么 | 为什么不能删 | 在本 skill 里的角色 |
|---|---|---|---|
| **`weread-skills`** | 微信读书 API 数据源 skill（拉取划线/笔记的底层接口，非整理型） | 删了 → **B 通道周二采集静默失败**，拉不到任何新划线 | **仅作数据来源**。它**不含任何分类/归纳逻辑**；duo-knowledge-classify 的 B 通道只调用它的 pull 能力，整理 / 原地合并 / 读书笔记全部在本 skill 内完成 |
| `xhs` 引擎 | 已打包进 `scripts/xhs/`（Spider_XHS 签名 + Chrome 枚举），自带、不依赖外部 | — | A 通道主力，已内置 |

> ⚠️ **`weread-skills` 与 `duoduo-wechat-publish` / `wechat-article-pro`（发布型）都只是数据源 / 发布渠道，不是「整理+分类归纳」型**，故不在本次合并范围、保留不动。
> 它的功能副本在 `~/.workbuddy/skills/weread-skills/`，可读镜像在 `99_Systems/00_Workflows/`（如存在）。如要升级 B 通道的数据拉取能力，改的是 `weread-skills`，不是本 skill。
