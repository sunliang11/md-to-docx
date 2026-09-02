"""Web API tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from web.app import app, MAX_BODY_BYTES

client = TestClient(app)


def test_healthz():
    res = client.get("/healthz")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert "version" in data


def test_presets():
    res = client.get("/api/presets")
    assert res.status_code == 200
    data = res.json()
    names = [p["name"] for p in data["presets"]]
    assert "technical" in names
    assert "editorial" in names
    assert "wecom" not in names
    assert names[0] == "professional"
    assert names[1] == "editorial"
    first = data["presets"][1]
    assert first["name"] == "editorial"
    assert "preview" in first
    assert first["preview"]["latin"] == "Georgia"
    assert first["preview"]["body_pt"] == 13


def test_convert_returns_docx():
    res = client.post(
        "/api/convert",
        json={"markdown": "# Hello\n\nWorld.", "preset": "professional"},
    )
    assert res.status_code == 200
    assert res.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert len(res.content) > 500


def test_convert_empty_markdown():
    res = client.post("/api/convert", json={"markdown": "", "preset": "technical"})
    assert res.status_code == 400
    detail = res.json()["detail"]
    assert detail["problem"] == "Empty document"


def test_convert_huge_body():
    huge = "x" * (MAX_BODY_BYTES + 1)
    res = client.post(
        "/api/convert",
        content='{"markdown":"' + huge + '","preset":"technical"}',
        headers={"Content-Type": "application/json", "Content-Length": str(MAX_BODY_BYTES + 100)},
    )
    assert res.status_code in (413, 422)


def test_example_md():
    res = client.get("/examples/technical-report.md")
    assert res.status_code == 200
    assert "#" in res.text or len(res.text) > 50
