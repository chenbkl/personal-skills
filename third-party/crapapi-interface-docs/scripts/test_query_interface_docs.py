#!/usr/bin/env python3

import importlib.util
import pathlib
import sys
import unittest
from unittest import mock


MODULE_PATH = pathlib.Path(__file__).with_name("query_interface_docs.py")
SPEC = importlib.util.spec_from_file_location("query_interface_docs", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class QueryInterfaceDocsTests(unittest.TestCase):
    def test_normalizes_full_and_relative_urls(self):
        expected = "/debapi/withhold/individual/zfbSign"
        self.assertEqual(MODULE.normalize_api_url(expected), expected)
        self.assertEqual(MODULE.normalize_api_url("withhold/individual/zfbSign"), expected)
        self.assertEqual(
            MODULE.normalize_api_url("https://example.test/debapi/withhold/individual/zfbSign?x=1"),
            expected,
        )

    def test_exact_match_does_not_accept_prefix(self):
        target = MODULE.normalize_api_url("/debapi/withhold/individual/zfbSign")
        self.assertNotEqual(
            MODULE.normalize_api_url("/debapi/withhold/individual/zfbSignQuery"),
            target,
        )

    def test_search_filters_project_and_result_type(self):
        payload = {
            "success": 1,
            "page": {"totalPage": 1},
            "data": {
                "searchResults": [
                    {"id": "keep", "title": "目标", "type": "Interface", "projectId": MODULE.PROJECT_ID},
                    {"id": "wrong-project", "title": "同名", "type": "Interface", "projectId": "other"},
                    {"id": "wrong-type", "title": "页面", "type": "Article", "projectId": MODULE.PROJECT_ID},
                ]
            },
        }
        with mock.patch.object(MODULE, "request_json", return_value=payload):
            candidates = MODULE.search_candidates("/debapi/test", timeout=1)
        self.assertEqual([item.interface_id for item in candidates], ["keep"])

    def test_query_uses_exact_detail_url(self):
        candidates = [
            MODULE.Candidate("sign", "签约", MODULE.PROJECT_ID),
            MODULE.Candidate("query", "签约查询", MODULE.PROJECT_ID),
        ]
        details = {
            "sign": {"id": "sign", "name": "签约", "fullUrl": "/debapi/withhold/individual/zfbSign"},
            "query": {"id": "query", "name": "签约查询", "fullUrl": "/debapi/withhold/individual/zfbSignQuery"},
        }
        with mock.patch.object(MODULE, "search_candidates", return_value=candidates), mock.patch.object(
            MODULE, "fetch_detail", side_effect=lambda interface_id, timeout: details[interface_id]
        ):
            result = MODULE.query_interface("/debapi/withhold/individual/zfbSign", timeout=1)
        self.assertEqual(result["id"], "sign")

    def test_markdown_preserves_hierarchy(self):
        detail = {
            "id": "1",
            "name": "测试接口",
            "projectName": MODULE.PROJECT_NAME,
            "moduleName": "测试模块",
            "fullUrl": "/debapi/test",
            "method": "POST",
            "contentType": "application/json",
            "version": "1.0",
            "status": "开发中",
            "updatedAt": "2026-08-03 12:00",
            "updatedBy": "tester",
            "sourceUrl": "https://example.test/detail",
            "headers": [],
            "inputs": [],
            "outputs": [
                {"name": "LIST", "type": "string", "necessary": "true", "remark": "列表", "deep": 1},
                {"name": "LIST->ID", "type": "string", "necessary": "true", "remark": "编号", "deep": 2},
            ],
            "requestExample": "",
            "successExample": "",
            "failureExample": "",
            "errors": [],
        }
        markdown = MODULE.render_markdown(detail)
        self.assertIn("`LIST`", markdown)
        self.assertIn("└ `ID`", markdown)
        self.assertIn("编号", markdown)
        self.assertIn("## 响应参数", markdown)


if __name__ == "__main__":
    unittest.main()
