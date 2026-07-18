import json

def pretty_json(obj, indent: int = 2, _level: int = 0) -> str:
    """自定义 JSON 格式化：字典按键换行缩进，数组内部保持同一行紧凑显示。"""
    pad = " " * (indent * _level)
    pad_inner = " " * (indent * (_level + 1))

    if obj is None:
        return "null"
    if isinstance(obj, bool):
        return "true" if obj else "false"
    if isinstance(obj, (int, float)):
        return str(obj)
    if isinstance(obj, str):
        return json.dumps(obj, ensure_ascii=False)
    if isinstance(obj, list):
        if not obj:
            return "[]"
        # 数组元素内部递归，元素之间用 ", " 连接（同一行）
        parts = [pretty_json(item, indent, _level) for item in obj]
        inner = ", ".join(parts)
        return f"[{inner}]"
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        lines = []
        for k, v in obj.items():
            key_str = json.dumps(str(k), ensure_ascii=False)
            val_str = pretty_json(v, indent, _level + 1)
            lines.append(f"{pad_inner}{key_str}: {val_str}")
        joined = ",\n".join(lines)
        return f"{{\n{joined}\n{pad}}}"
    return json.dumps(obj, ensure_ascii=False, default=str)
