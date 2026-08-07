#!/usr/bin/env python3
"""Generate the local Tampermonkey login helper without committing credentials."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_ENV = SKILL_DIR / ".env"
DEFAULT_TEMPLATE = SKILL_DIR / "assets" / "crapapi-auto-login.user.js.tpl"
DEFAULT_OUTPUT = SKILL_DIR / "crapapi-auto-login.generated.user.js"


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        values[key.strip()] = value
    return values


def import_existing_userscript(source: Path, env_path: Path) -> None:
    content = source.read_text(encoding="utf-8")
    username = re.search(r"const\s+USERNAME\s*=\s*(['\"])(.*?)\1\s*;", content)
    password = re.search(r"const\s+PASSWORD\s*=\s*(['\"])(.*?)\1\s*;", content)
    if not username or not password:
        raise SystemExit("未能从旧脚本识别 USERNAME/PASSWORD")
    env_path.parent.mkdir(parents=True, exist_ok=True)
    env_path.write_text(
        f"CRAPAPI_USERNAME={username.group(2)}\nCRAPAPI_PASSWORD={password.group(2)}\n",
        encoding="utf-8",
    )
    os.chmod(env_path, 0o600)


def generate(env_path: Path, template_path: Path, output_path: Path) -> None:
    values = read_env(env_path)
    username = values.get("CRAPAPI_USERNAME")
    password = values.get("CRAPAPI_PASSWORD")
    if not username or not password:
        raise SystemExit(f"缺少 CRAPAPI_USERNAME/CRAPAPI_PASSWORD：{env_path}")

    template = template_path.read_text(encoding="utf-8")
    replacements = {
        "__CRAPAPI_USERNAME_JSON__": json.dumps(username, ensure_ascii=False),
        "__CRAPAPI_PASSWORD_JSON__": json.dumps(password, ensure_ascii=False),
    }
    for placeholder, replacement in replacements.items():
        if placeholder not in template:
            raise SystemExit(f"模板缺少占位符：{placeholder}")
        template = template.replace(placeholder, replacement)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template, encoding="utf-8")
    os.chmod(output_path, 0o600)
    print(f"已生成：{output_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 CrapAPI 自动登录篡改猴脚本")
    parser.add_argument("--env", type=Path, default=DEFAULT_ENV)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--import-userscript", type=Path, help="从现有成品脚本迁移 USERNAME/PASSWORD 到 .env")
    args = parser.parse_args()
    if args.import_userscript:
        import_existing_userscript(args.import_userscript, args.env)
    generate(args.env, args.template, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
