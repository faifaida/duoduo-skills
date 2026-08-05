# 读图 PROMPT 模板与字段定义

给本地 llava-llama3 用的**冒号键值** PROMPT。真实照片下 llava 稳定按此格式产出;
合成图会退化(整串复读示例),靠 `parse_llava` 的复读守卫兜底。

## PROMPT(直接复制)

```
请按以下字段分析这张图片,严格用「字段名: 值」格式每行一个,不要自由发挥:
场景地点: 图片最可能的真实地点类型(beach/ocean/canal/cafe/urban_street/hallway/church/museum/mountain/forest/water 等,越具体越好,不要用国家名)
主要物体: 逗号列举图中主要物体英文词(people,surfboard,dog,cup,wave...)
画面描述: 一句话中文描述画面
人物动作: 图中人物在做什么(逗号列举英文动作词:surf/swim/pose/drink/hold...),无人则写 none
内容类型: travel_portrait / scenery / food / city / people / object 之一
人物情绪: 图中人物情绪英文受控词(relaxed/warm/adventurous/curious/peaceful/excited/joyful/contemplative/nostalgic),多人不同则逗号列举
视觉感受: 叙事功能英文受控词(多选,下划线连接:hook_face/end_face/escalation/emotional_peak/realization/pause/world_build),图片不标 hook_face/end_face
推荐用途: 英文受控词(多选,逗号分隔:cover,thumbnail,post,story,broll,hero),不知道写 none
是否有人脸: 有/无
是否正对镜头: 是/否
内容风险: 低/中/高
```

## 受控词表(解析时归一化,统一小写英文)

### emotion(情绪基调,单选或逗号列举)
`relaxed` `warm` `adventurous` `curious` `peaceful` `excited` `joyful` `contemplative` `nostalgic`
中文映射: 放松→relaxed / 温暖→warm / 冒险→adventurous / 好奇→curious / 平静→peaceful / 兴奋→excited / 开心→joyful / 沉思→contemplative / 怀旧→nostalgic
规则: 禁止中英混杂、禁止自由句,统一英文小写受控词。

### vf(叙事功能/节奏节点,多选叠加,文件级标 1–3 个)
`hook_face`(开场钩子脸) `end_face`(收尾脸) `escalation`(情绪往上走) `emotional_peak`(高潮瞬间)
`realization`(顿悟微表情转折) `pause`(留白喘息/空镜) `world_build`(世界观/氛围铺陈,如空旷海滩全景/清晨小镇/帐篷外景)
规则: 图片只标功能类(realization/peak/pause/escalation/world_build),**不标 hook_face / end_face**(无时间位置概念)。细粒度(hook/end face 位置、realization 微表情)改由上云 GPT-5.6 判。

### recommended_use(推荐用途,多选,上限 4)
`cover`(封面) `thumbnail`(缩略图) `post`(图文帖) `story`(竖屏动态) `broll`(空镜素材) `hero`(主视觉头图)
中文映射: 封面→cover / 缩略图→thumbnail / 空镜→broll / 主视觉→hero / 图文帖→post / 竖屏→story
规则: llava 若整串复读示例词表("cover/thumbnail/post/story/broll/hero")视为未判断,清空。

## place 兜底(重要,避免城市图永远 0% 完成度)
- 有 GPS(mdls 取 lat/lon)→ 用 GPS 命名区(siargao/cebu/manila/bkk_airport…)
- 无 GPS → llava 把场景写进 `evidence`(城市街道/教堂/博物馆/hallway…)时,从 evidence/caption 提取场景词作 place,兜底标 `urban`
- 原则: place **非空、非国家名**,基于真读图信号
