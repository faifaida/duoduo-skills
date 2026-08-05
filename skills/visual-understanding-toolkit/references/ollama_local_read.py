#!/usr/bin/env python3
"""
ollama_local_read.py — 本地 llava 真读图(照片不外传)
多多个人公司「视觉理解工具箱」参考实现。员工可复制到项目直接用。

用法:
  python ollama_local_read.py <图片路径> [图片路径2 ...]
  python ollama_local_read.py --dir <图片目录>   # 批量

输出: 每张图的结构化 dict(JSON 到 stdout),含受控词归一化 + 复读守卫。
依赖: requests  (python -m pip install requests)
前置: ~/.workbuddy/binaries/ollama/ollama serve 已在 127.0.0.1:11434
"""
import base64
import json
import os
import re
import sys
import subprocess

OLLAMA_BIN = os.path.expanduser("~/.workbuddy/binaries/ollama/ollama")
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "llava-llama3"

PROMPT = """请按以下字段分析这张图片,严格用「字段名: 值」格式每行一个,不要自由发挥:
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
内容风险: 低/中/高"""

EMOTION_CTRL = {"relaxed","warm","adventurous","curious","peaceful","excited","joyful","contemplative","nostalgic"}
EMO_MAP = {"放松":"relaxed","温暖":"warm","冒险":"adventurous","好奇":"curious","平静":"peaceful","兴奋":"excited","开心":"joyful","高兴":"joyful","沉思":"contemplative","怀旧":"nostalgic"}
VF_CTRL = {"hook_face","end_face","escalation","emotional_peak","realization","pause","world_build"}
RU_CTRL = {"cover","thumbnail","post","story","broll","hero"}
RU_MAP = {"封面":"cover","缩略图":"thumbnail","空镜":"broll","主视觉":"hero","图文帖":"post","竖屏":"story"}

def _ollama_running():
    try:
        out = subprocess.run([OLLAMA_BIN, "ps"], capture_output=True, text=True, timeout=10).stdout
        return MODEL in out
    except Exception:
        return False

def call_llava(img_path, timeout=90):
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    payload = {"model": MODEL, "prompt": PROMPT, "images": [b64], "stream": False}
    import requests
    r = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json().get("response", "")

def parse_llava(text):
    d = {k: "" for k in ["场景地点","主要物体","画面描述","人物动作","内容类型","人物情绪","视觉感受","推荐用途","是否有人脸","是否正对镜头","内容风险"]}
    for line in text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip(); v = v.strip()
            if k in d:
                d[k] = v
    # emotion
    emo = _norm_multi(d["人物情绪"], EMOTION_CTRL, EMO_MAP)
    # vf
    vf = _norm_multi(d["视觉感受"], VF_CTRL, {}, sep="_")
    # recommended_use
    ru_raw = d["推荐用途"].lower()
    # 复读守卫: 整串示例词表 → 清空
    if set(ru_raw.replace("/", ",").split(",")) >= RU_CTRL and "/" in ru_raw:
        ru = ""
    else:
        ru = _norm_multi(d["推荐用途"], RU_CTRL, RU_MAP)
    return {
        "scene": d["场景地点"], "objects": d["主要物体"], "caption": d["画面描述"],
        "action": d["人物动作"], "type": d["内容类型"], "emotion": emo, "vf": vf,
        "has_face": d["是否有人脸"], "facing": d["是否正对镜头"], "risk": d["内容风险"],
        "recommended_use": ru,
    }

def _norm_multi(raw, ctrl, amap, sep=","):
    raw = raw.strip().lower()
    if raw in ("none", "无", "n/a", "na", ""):
        return ""
    # 中文映射
    for zh, en in amap.items():
        raw = raw.replace(zh, en)
    toks = re.split(r"[,/\s]+", raw)
    out = []
    for t in toks:
        t = t.strip().strip("_")
        if not t:
            continue
        if t in ctrl:
            out.append(t)
    # 去重保序
    seen = set(); res = []
    for t in out:
        if t not in seen:
            seen.add(t); res.append(t)
    return sep.join(res[:4])

def read_one(img_path):
    if not _ollama_running():
        return {"file": img_path, "error": "ollama llava 未运行,请先启动服务"}
    try:
        resp = call_llava(img_path)
        parsed = parse_llava(resp)
        parsed["file"] = img_path
        parsed["raw_response"] = resp
        return parsed
    except Exception as e:
        return {"file": img_path, "error": str(e)}

if __name__ == "__main__":
    args = sys.argv[1:]
    files = []
    if "--dir" in args:
        d = args[args.index("--dir")+1]
        for ext in ("jpg","jpeg","png","webp","heic"):
            files += [os.path.join(d, f) for f in os.listdir(d) if f.lower().endswith("."+ext)]
    else:
        files = [a for a in args if not a.startswith("--")]
    for fp in files:
        print(json.dumps(read_one(fp), ensure_ascii=False))
