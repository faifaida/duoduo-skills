#!/usr/bin/env python3
"""
生成两个 .shortcut 文件，供多多在 iPhone 上「文件」App 点一下导入：

1. 语音日记存vault.shortcut
   获取最新录音(Voice Memos) -> 存到 iCloud 云盘 /DuoDuo_Inbox/voice
   （一键：Widget / 轻点背面 触发；录完退出语音备忘录后跑）

2. 备忘录日记存vault.shortcut
   查找「多多日记本」笔记本里的备忘录 -> 逐条存为 .md 到 iCloud 云盘 /DuoDuo_Inbox/notes
   （一键；若你不用「多多日记本」笔记本，导入后把过滤条件改成你自己的日记笔记本即可）

注：.shortcut 是二进制 plist。本脚本只生成结构正确的文件，无法在 Mac 验证手机端导入效果，
    导入若有一步不对（多半是文件夹需要重选），在快捷指令里点一下改掉即可。
"""
import plistlib
import uuid
from pathlib import Path

CLIENT_VERSION = "2373.0.2"
CLIENT_RELEASE = "17.5"
MIN_CLIENT = 900

CLOUD_DOCS = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs"


def uid() -> str:
    return str(uuid.uuid4()).upper()


def icon(start: int = 4, glyph: int = 59533) -> dict:
    return {
        "WFWorkflowIconStartColor": start,
        "WFWorkflowIconGlyphNumber": glyph,
    }


def action_output_ref(action_uuid: str, output_name: str) -> dict:
    """引用上一个动作的输出（magic variable），用 ActionOutput + UUID 最稳。"""
    return {
        "Value": {
            "Type": "ActionOutput",
            "OutputName": output_name,
            "OutputUUID": action_uuid,
        },
        "WFSerializationType": "WFTextTokenString",
    }


def save_file_action(input_ref: dict, folder_rel_path: str, ask_where: bool = False) -> dict:
    """Save File 动作：把 input_ref 存到 iCloud 云盘 folder_rel_path（相对 iCloud Drive 根）。"""
    fm_url = "file://" + str(CLOUD_DOCS) + folder_rel_path
    return {
        "WFWorkflowActionIdentifier": "is.workflow.actions.savefile",
        "WFWorkflowActionParameters": {
            "UUID": uid(),
            "WFSaveFileWorkflowAskWhere": ask_where,
            "WFFileContentItem": input_ref,
            "WFFilePath": {
                "Value": {
                    "Type": 2,  # 2 = iCloud Drive（相对 iCloud Drive 根）
                    "Value": {
                        "BasePath": "",
                        "PathString": folder_rel_path,
                        "FileManagerURL": fm_url,
                        "RelativeSubpath": "",
                    },
                },
                "WFSerializationType": "WFFilePath",
            },
        },
    }


def get_latest_recording() -> tuple[str, dict]:
    u = uid()
    return u, {
        "WFWorkflowActionIdentifier": "is.workflow.actions.getlatestrecording",
        "WFWorkflowActionParameters": {"UUID": u},
    }


def find_notes_in_folder(folder_name: str) -> tuple[str, dict]:
    u = uid()
    return u, {
        "WFWorkflowActionIdentifier": "is.workflow.actions.notes.find",
        "WFWorkflowActionParameters": {
            "UUID": u,
            "WFNotesFindFolder": {
                "Value": {"WFNoteFolder": {"Name": folder_name}},
            },
        },
    }


def build_shortcut(name: str, actions: list, icon_dict: dict, input_classes=None) -> dict:
    return {
        "WFWorkflowClientVersion": CLIENT_VERSION,
        "WFWorkflowClientRelease": CLIENT_RELEASE,
        "WFWorkflowMinimumClientVersion": MIN_CLIENT,
        "WFWorkflowIcon": icon_dict,
        "WFWorkflowTypes": ["ActionExtension", "NCWidget"],
        "WFWorkflowInputContentItemClasses": input_classes or [],
        "WFWorkflowActions": actions,
        "WFWorkflowName": name,
    }


def main():
    out_dir = CLOUD_DOCS / "Shortcuts"
    backup_dir = CLOUD_DOCS / "DuoDuo_Inbox" / "shortcuts"
    out_dir.mkdir(parents=True, exist_ok=True)
    backup_dir.mkdir(parents=True, exist_ok=True)

    # 1) 语音：获取最新录音 -> 存 voice
    ru, rec = get_latest_recording()
    voice_actions = [
        rec,
        save_file_action(action_output_ref(ru, "Recording"), "/DuoDuo_Inbox/voice"),
    ]
    voice_sc = build_shortcut("语音日记存vault", voice_actions, icon(4, 59533))

    # 2) 备忘录：查找「多多日记本」-> 存 notes
    nu, find = find_notes_in_folder("多多日记本")
    notes_actions = [
        find,
        save_file_action(action_output_ref(nu, "Notes"), "/DuoDuo_Inbox/notes"),
    ]
    notes_sc = build_shortcut("备忘录日记存vault", notes_actions, icon(5, 59464))

    files = {
        "语音日记存vault.shortcut": voice_sc,
        "备忘录日记存vault.shortcut": notes_sc,
    }
    written = []
    for fname, sc in files.items():
        data = plistlib.dumps(sc, fmt=plistlib.FMT_BINARY)
        p1 = out_dir / fname
        p2 = backup_dir / fname
        p1.write_bytes(data)
        p2.write_bytes(data)
        written.append((fname, len(data)))

    print("生成完成：")
    for fname, size in written:
        print(f"  {fname}  ({size} bytes)")
        print(f"    -> {out_dir/fname}")
        print(f"    -> {backup_dir/fname}")


if __name__ == "__main__":
    main()
