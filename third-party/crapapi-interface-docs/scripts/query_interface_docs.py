#!/usr/bin/env python3
"""Query CrapAPI interface documentation by exact API URL."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Iterable


BASE_URL = "https://test.95598pay.top:29943/crapapi"
PROJECT_ID = "156939461626807001127"
PROJECT_NAME = "电e宝移动端接口服务（deb-api-rest）"


class QueryError(RuntimeError):
    """Base error for deterministic CLI reporting."""


class NotFoundError(QueryError):
    pass


class AmbiguousError(QueryError):
    pass


@dataclass(frozen=True)
class Candidate:
    interface_id: str
    title: str
    project_id: str


def normalize_api_url(value: str) -> str:
    raw = urllib.parse.unquote(value.strip())
    if not raw:
        raise ValueError("接口 URL 不能为空")

    parsed = urllib.parse.urlsplit(raw)
    path = parsed.path if parsed.scheme or parsed.netloc else raw.split("?", 1)[0].split("#", 1)[0]
    marker = "/debapi/"
    marker_index = path.find(marker)
    if marker_index >= 0:
        path = path[marker_index:]
    else:
        path = "/" + path.lstrip("/")
        if path == "/debapi":
            return path
        if not path.startswith("/debapi/"):
            path = "/debapi/" + path.lstrip("/")

    while "//" in path:
        path = path.replace("//", "/")
    if len(path) > 1:
        path = path.rstrip("/")
    return path


def request_json(url: str, *, form: dict[str, str] | None, timeout: float) -> dict[str, Any]:
    data = urllib.parse.urlencode(form).encode("utf-8") if form is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Accept": "application/json", "User-Agent": "crapapi-interface-docs/1.0"},
        method="POST" if form is not None else "GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise QueryError(f"请求接口文档平台失败：{exc}") from exc

    if payload.get("success") != 1:
        error = payload.get("error") or {}
        message = error.get("message") or payload.get("tipMessage") or "未知错误"
        raise QueryError(f"接口文档平台返回失败：{message}")
    return payload


def search_candidates(target: str, timeout: float) -> list[Candidate]:
    candidates: dict[str, Candidate] = {}
    current_page = 1
    total_pages = 1
    while current_page <= total_pages:
        payload = request_json(
            f"{BASE_URL}/visitorSearch.do",
            form={"keyword": target, "currentPage": str(current_page)},
            timeout=timeout,
        )
        page = payload.get("page") or {}
        total_pages = max(1, int(page.get("totalPage") or 1))
        results = ((payload.get("data") or {}).get("searchResults") or [])
        for item in results:
            if item.get("type") != "Interface" or str(item.get("projectId")) != PROJECT_ID:
                continue
            interface_id = str(item.get("id") or "")
            if interface_id:
                candidates[interface_id] = Candidate(
                    interface_id=interface_id,
                    title=str(item.get("title") or ""),
                    project_id=str(item.get("projectId") or ""),
                )
        current_page += 1
    return list(candidates.values())


def parse_embedded_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if not isinstance(value, str) or not value.strip():
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    return [item for item in parsed if isinstance(item, dict)] if isinstance(parsed, list) else []


def normalize_detail(data: dict[str, Any]) -> dict[str, Any]:
    headers = data.get("crShowHeaderList") or parse_embedded_list(data.get("header"))
    inputs = data.get("crShowParamList") or parse_embedded_list(data.get("paramRemark"))
    outputs = data.get("crShowResponseParamList") or parse_embedded_list(data.get("responseParam"))
    errors = parse_embedded_list(data.get("errors"))
    return {
        "id": str(data.get("id") or ""),
        "name": str(data.get("interfaceName") or ""),
        "projectId": str(data.get("projectId") or ""),
        "projectName": PROJECT_NAME,
        "moduleId": str(data.get("moduleId") or ""),
        "moduleName": str(data.get("moduleName") or ""),
        "fullUrl": str(data.get("fullUrl") or ""),
        "method": str(data.get("method") or ""),
        "version": str(data.get("version") or ""),
        "status": str(data.get("statusName") or ""),
        "contentType": str(data.get("contentType") or ""),
        "createdAt": str(data.get("createTimeStr") or ""),
        "updatedAt": str(data.get("updateTimeStr") or ""),
        "updatedBy": str(data.get("updateBy") or ""),
        "headers": headers,
        "inputs": inputs,
        "outputs": outputs,
        "requestExample": str(data.get("requestExam") or ""),
        "successExample": str(data.get("trueExam") or ""),
        "failureExample": str(data.get("falseExam") or ""),
        "errors": errors,
        "sourceUrl": f"{BASE_URL}/index.do#/interface/detail?projectId={PROJECT_ID}&id={data.get('id') or ''}",
    }


def fetch_detail(interface_id: str, timeout: float) -> dict[str, Any]:
    payload = request_json(
        f"{BASE_URL}/visitor/interface/detail.do?id={urllib.parse.quote(interface_id)}",
        form=None,
        timeout=timeout,
    )
    data = payload.get("data")
    if not isinstance(data, dict):
        raise QueryError(f"接口 {interface_id} 的详情结构无效")
    return normalize_detail(data)


def query_interface(value: str, timeout: float = 15.0) -> dict[str, Any]:
    target = normalize_api_url(value)
    candidates = search_candidates(target, timeout)
    if not candidates:
        raise NotFoundError(f"未找到接口：{target}")

    details = [fetch_detail(candidate.interface_id, timeout) for candidate in candidates]
    exact = [detail for detail in details if normalize_api_url(detail["fullUrl"]) == target]
    if not exact:
        choices = "、".join(f"{item['fullUrl']}（{item['id']}）" for item in details)
        raise NotFoundError(f"未找到精确匹配：{target}；候选：{choices or '无'}")
    if len(exact) > 1:
        choices = "、".join(f"{item['name']}（{item['id']}）" for item in exact)
        raise AmbiguousError(f"存在多个精确匹配：{target}；{choices}")
    return exact[0]


def escape_cell(value: Any) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", "<br>")


def required_text(item: dict[str, Any]) -> str:
    return "是" if str(item.get("necessary", "")).lower() == "true" else "否"


def display_field_name(item: dict[str, Any]) -> str:
    name = str(item.get("name") or item.get("realName") or "")
    deep = max(1, int(item.get("deep") or 1))
    leaf = name.split("->")[-1]
    return f"{'　' * (deep - 1)}{'└ ' if deep > 1 else ''}`{leaf}`"


def parameter_table(items: Iterable[dict[str, Any]], include_position: bool = False) -> list[str]:
    rows = list(items)
    if include_position:
        lines = ["| 参数名 | 类型 | 必填 | 参数位置 | 说明 |", "| --- | --- | --- | --- | --- |"]
    else:
        lines = ["| 参数名 | 类型 | 必填 | 说明 |", "| --- | --- | --- | --- |"]
    if not rows:
        column_count = 5 if include_position else 4
        lines.append("| 无 |" + "  |" * (column_count - 1))
        return lines
    for item in rows:
        base = [display_field_name(item), f"`{escape_cell(item.get('type', ''))}`", required_text(item)]
        if include_position:
            base.append(escape_cell(item.get("paramPosition", "")))
        base.append(escape_cell(item.get("remark", "")))
        lines.append("| " + " | ".join(base) + " |")
    return lines


def render_markdown(detail: dict[str, Any]) -> str:
    lines = [
        f"# {detail['name']}",
        "",
        "## 基本信息",
        "",
        "| 项目 | 内容 |",
        "| --- | --- |",
        f"| 接口 ID | `{escape_cell(detail['id'])}` |",
        f"| 所属项目 | {escape_cell(detail['projectName'])} |",
        f"| 所属模块 | {escape_cell(detail['moduleName'])} |",
        f"| 完整路径 | `{escape_cell(detail['fullUrl'])}` |",
        f"| 请求方法 | `{escape_cell(detail['method'])}` |",
        f"| Content-Type | `{escape_cell(detail['contentType'])}` |",
        f"| 版本 | `{escape_cell(detail['version'])}` |",
        f"| 状态 | {escape_cell(detail['status'])} |",
        f"| 更新时间 | `{escape_cell(detail['updatedAt'])}` |",
        f"| 更新人 | {escape_cell(detail['updatedBy'])} |",
        f"| 来源文档 | {escape_cell(detail['sourceUrl'])} |",
        "",
        "## 请求头",
        "",
        *parameter_table(detail["headers"]),
        "",
        "## 请求参数",
        "",
        *parameter_table(detail["inputs"], include_position=True),
        "",
        "## 响应参数",
        "",
        *parameter_table(detail["outputs"]),
    ]

    examples = [
        ("请求示例", detail["requestExample"]),
        ("正确返回示例", detail["successExample"]),
        ("错误返回示例", detail["failureExample"]),
    ]
    for title, content in examples:
        if content:
            lines.extend(["", f"## {title}", "", "```json", content, "```"])

    lines.extend(["", "## 错误码", "", "| 错误码 | 说明 |", "| --- | --- |"])
    if detail["errors"]:
        for item in detail["errors"]:
            lines.append(f"| `{escape_cell(item.get('errorCode', ''))}` | {escape_cell(item.get('errorMsg', ''))} |")
    else:
        lines.append("| 无 | 文档未配置 |")
    return "\n".join(lines).rstrip() + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="按接口 URL 查询 CrapAPI 文档")
    parser.add_argument("urls", nargs="+", help="完整 URL、/debapi/ 路径或相对接口路径")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--timeout", type=float, default=15.0)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    results: list[dict[str, Any]] = []
    try:
        for value in args.urls:
            results.append(query_interface(value, timeout=args.timeout))
    except NotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except AmbiguousError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    except (QueryError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.format == "json":
        payload: Any = results[0] if len(results) == 1 else results
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("\n\n---\n\n".join(render_markdown(item).rstrip() for item in results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
