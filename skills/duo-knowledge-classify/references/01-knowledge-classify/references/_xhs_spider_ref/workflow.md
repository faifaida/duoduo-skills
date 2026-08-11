# 运营手册 / 排障 Playbook

## 一、为什么从「DOM 抓取」换成「Spider_XHS 签名引擎」
旧方案（osascript 驱动本机 Chrome 打开每篇详情页提取 DOM）：
- ✅ 能绕过 TLS/设备指纹（真实 Chrome）。
- ❌ 一次性连抓 8 本触发**行为层风控**：页面回 "Too many requests"，标题显示"安全限制"。
- ❌ 旧 `valid` 判断漏掉限流页，把 ~490 篇 junk 写进了 vault（已清理）。

Spider_XHS：
- ✅ 逆向 x-s/x-t 等签名，走 `/api/sns/web/v1/feed` 签名 API（非 DOM）。
- ✅ 支持 cookie 导入登录（复用本机 Chrome 登录态）。
- ❌ **没有 board 级接口**，只返回「我的全部收藏」混合流 → 必须保留 Chrome 按 board 枚举 noteId 的混合架构。
- ❌ 仍受账号级限流 + IP 类型制约（见下）。

## 二、关键事实（2026-07-22 实测）
- **限流持续 >19h 未解除**：从 2026-07-21 22:20 起，到 07-22 凌晨 05:12 自动补抓、再到 17:42 手动重试，全部首篇即限流 → 疑**账号级风控**（链接能采、详情页被限，非网络/登录问题）。
- **出口 IP 是机房 IP（非住宅）**：`89.31.126.148`，ASN AS212238，归属 Think Huge LTD / Datacamp Limited（东京）。这是小红书重点封锁类型，是限流的**重要诱因之一**，也是换工具无法单独解决的。

## 三、当前 vault 有效篇数（截至 2026-07-22，约 561 篇）
| 完整 ✅ | 待补 ⚠️（被限流打断） |
|--------|--------|
| 习惯和思考 / 关系恋爱 / 青旅 / 剪辑 / 文旅 | 养生大法 / 职业 / 审美 / （关系恋爱少量） |

## 四、恢复 Playbook（按顺序）
1. **先切住宅/移动代理**：Clash Verge 切到住宅节点（或设 `XHS_PROXY`），这是降低限流/封号概率的首要动作。
2. **等限流解除**：通常 >24h。可用 `extract_xhs_cookies.py` + 一次小探测（只抓 1 篇详情）验证是否仍限流，避免空跑整批。
3. **刷新 cookie**：`extract_xhs_cookies.py`（登录态可能过期）。
4. **跑同步**：`xhs_obsidian_sync.py`（已带降速 3–6s/篇 + 限流退避 120s）。
5. **清理 junk**：若仍偶发限流页，跑 `cleanup_junk.py`。
6. **核对篇数**：统计 `VAULT/<专辑>/*.md`（排除索引）确认补齐。

## 五、增量运行约定
- 每周一晚 20:00 自动增量（automation 指向本 skill 的 `xhs_obsidian_sync.py`）。
- `imported_ids.json` 是去重唯一数据源；只补新增，不重建已抓。
- 不要在限流期硬跑：探测到首篇即限流 → 直接中止，不要连跑多轮加重风控。

## 六、升级上游签名
小红书约每月轮换签名算法。若某天开始大面积 `success=False` 且非限流，去 `cv-cat/Spider_XHS` 拉最新 `xhs_utils` 替换 `scripts/Spider_XHS/xhs_utils/`。
