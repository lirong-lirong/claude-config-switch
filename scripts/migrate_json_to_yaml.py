#!/usr/bin/env python3
"""将旧的 config.json 配置文件迁移为 config.yaml 格式。"""
import json
import shutil
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("错误: 请先安装 pyyaml: pip install pyyaml")
    sys.exit(1)


def main():
    config_dir = Path.home() / ".config" / "claude-code-switch"
    json_path = config_dir / "config.json"
    yaml_path = config_dir / "config.yaml"

    if not json_path.exists():
        print(f"未找到旧配置文件: {json_path}")
        sys.exit(1)

    if yaml_path.exists():
        print(f"目标文件已存在: {yaml_path}")
        print("如需重新迁移，请先手动删除或备份该文件。")
        sys.exit(1)

    # 读取 JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 写入 YAML
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    # 备份旧文件
    backup_path = json_path.with_suffix(".json.bak")
    shutil.move(str(json_path), str(backup_path))

    print(f"迁移完成!")
    print(f"  新配置: {yaml_path}")
    print(f"  旧配置已备份为: {backup_path}")


if __name__ == "__main__":
    main()
