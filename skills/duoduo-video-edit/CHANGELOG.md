# duoduo-video-edit 演进记录

## 2026-08-11（v3 里程碑）
- SKILL.md 增补第 7–9 节
  - 第 7 节：三类覆盖机制 `hook` / `back_replace` / `screen_replace`（旁白片按时间窗/屏序定点替换素材）
  - 第 8 节：斯里兰卡素材隐私筛查标准（本地 `llava-llama3:latest` 单帧严格 JSON，OTHER=False 才收，排除跨集重复）
  - 第 9 节：交付纪律（成片只给视频+封面，contact sheet 仅内部 QA 绝不 present）
- 配套 `references/video_lessons.md` 错题本（含旁白片七宗罪、字幕对齐流水线）
- EP1–EP10 泳衣导演线实战打磨，世斐线复用同一套工作流

## 2026-08 初（v2）
- 引入 `render_narrated_ep.py`：用户录音 VO 型旁白片流水线
- `zh_merge` 中英文屏配对、`assign_media` 池不足循环复用 + 空池守卫
- `make_cover.py` 品牌封面规范（克隆 ep2 排版、暗角、米色渐变带、logo lockup）

## 2026-07（v1 初版）
- 素材审片联系表 + 人脸识别找多多（face_id 0.75 阈值）
- ffmpeg 直出成片；泳衣线视觉规范；字幕对齐流水线雏形
