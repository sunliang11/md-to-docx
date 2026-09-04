"""Web API tests."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

from web.app import MAX_BODY_BYTES, MAX_UPLOAD_BYTES, app

REPO = Path(__file__).resolve().parent.parent
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
    # Pydantic rejects oversize markdown with 422 when body is parsed as JSON.
    res = client.post(
        "/api/convert",
        json={"markdown": huge, "preset": "technical"},
    )
    assert res.status_code == 422


def test_example_md():
    res = client.get("/examples/technical-report.md")
    assert res.status_code == 200
    assert "#" in res.text or len(res.text) > 50


def test_convert_options_and_invalid_template():
    ok = client.post(
        "/api/convert",
        json={
            "markdown": "# Hello\n\nWorld.",
            "preset": "professional",
            "numbering": True,
            "title": "Playground",
            "author": "Tester",
            "date": "2026-09-03",
            "doc_version": "1.0",
            "toc_title": "目录",
            "figure_label": "图",
            "table_label": "表",
            "section_label": "节",
            "page_numbers": False,
            "normalize": True,
            "no_plugins": False,
            "strict_mermaid": False,
            "template": "technical-design",
        },
    )
    assert ok.status_code == 200
    assert len(ok.content) > 500

    bad = client.post(
        "/api/convert",
        json={"markdown": "# Hello\n\nWorld.", "preset": "technical", "template": "not-a-template"},
    )
    assert bad.status_code == 400
    assert bad.json()["detail"]["problem"] == "Invalid template"


def test_convert_multipart_with_template_file():
    tpl = REPO / "templates" / "technical-design" / "template.docx"
    if not tpl.is_file():
        return
    res = client.post(
        "/api/convert",
        data={
            "markdown": "# Hello\n\nWorld from multipart.",
            "preset": "technical",
            "toc": "true",
            "numbering": "true",
            "page_numbers": "true",
            "normalize": "true",
        },
        files={
            "template_file": (
                "template.docx",
                tpl.read_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert res.status_code == 200
    assert len(res.content) > 500


def test_preview_callout():
    res = client.post(
        "/api/preview",
        json={"markdown": ":::warning\nCareful.\n:::\n", "numbering": False},
    )
    assert res.status_code == 200
    data = res.json()
    assert "callout" in data["html"]
    assert "css" in data


def test_validate_issues():
    empty = client.post("/api/validate", json={"markdown": "   "})
    assert empty.status_code == 200
    codes = [i["code"] for i in empty.json()["issues"]]
    assert "empty_document" in codes

    skipped = client.post(
        "/api/validate",
        json={"markdown": "# Title\n\n#### Too deep\n"},
    )
    assert skipped.status_code == 200
    assert any(i["code"] == "heading_skip" for i in skipped.json()["issues"])


def test_validate_strict_and_text_format():
    md = "# Title\n\n#### Too deep\n"
    strict = client.post("/api/validate", json={"markdown": md, "strict": True})
    assert strict.status_code == 200
    assert any(i["severity"] == "error" for i in strict.json()["issues"])

    text = client.post(
        "/api/validate",
        json={"markdown": md, "strict": False, "format": "text"},
    )
    assert text.status_code == 200
    assert "heading_skip" in text.text


def test_templates_list():
    res = client.get("/api/templates")
    assert res.status_code == 200
    ids = [t["id"] for t in res.json()["templates"]]
    assert "technical-design" in ids


def test_reverse_docx():
    path = REPO / "examples" / "technical-report" / "example.docx"
    with path.open("rb") as fh:
        res = client.post(
            "/api/reverse",
            files={
                "file": (
                    "example.docx",
                    fh,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )
    assert res.status_code == 200
    assert len(res.text) > 20


def test_reverse_rejects_non_docx():
    res = client.post(
        "/api/reverse",
        files={"file": ("notes.txt", b"not a docx", "text/plain")},
    )
    assert res.status_code == 400


def test_reverse_too_large():
    payload = b"PK" + b"x" * (MAX_UPLOAD_BYTES + 8)
    res = client.post(
        "/api/reverse",
        files={
            "file": (
                "huge.docx",
                payload,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert res.status_code == 413


def test_diff_markdown():
    res = client.post(
        "/api/diff",
        json={
            "a": "# One\n\nHello.\n",
            "b": "# Two\n\nHello world.\n",
            "format": "md",
        },
    )
    assert res.status_code == 200
    assert "Document changes" in res.text or "heading" in res.text.lower()


def test_batch_dry_run_and_zip():
    files = [
        ("files", ("a.md", b"# A\n\nOne.\n", "text/markdown")),
        ("files", ("b.md", b"# B\n\nTwo.\n", "text/markdown")),
    ]
    dry = client.post(
        "/api/convert/batch",
        data={"preset": "professional", "dry_run": "true", "toc": "true"},
        files=files,
    )
    assert dry.status_code == 200
    data = dry.json()
    assert data["count"] == 2
    assert "a.md" in data["planned"]
    assert "b.md" in data["planned"]

    out = client.post(
        "/api/convert/batch",
        data={"preset": "professional", "dry_run": "false", "toc": "false"},
        files=[
            ("files", ("a.md", b"# A\n\nOne.\n", "text/markdown")),
            ("files", ("b.md", b"# B\n\nTwo.\n", "text/markdown")),
        ],
    )
    assert out.status_code == 200
    assert out.headers["content-type"].startswith("application/zip")
    with zipfile.ZipFile(io.BytesIO(out.content)) as zf:
        names = sorted(zf.namelist())
    assert names == ["a.docx", "b.docx"]


def test_batch_zip_archive_dry_run():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("docs/one.md", "# One\n\nHi.\n")
        zf.writestr("docs/two.md", "# Two\n\nHi.\n")
        zf.writestr("README.md", "# Skip me\n")
    res = client.post(
        "/api/convert/batch",
        data={"preset": "technical", "dry_run": "true"},
        files={
            "archive": ("bundle.zip", buf.getvalue(), "application/zip"),
        },
    )
    assert res.status_code == 200
    planned = res.json()["planned"]
    assert "docs/one.md" in planned
    assert "docs/two.md" in planned
    assert "README.md" not in planned


def test_batch_no_files():
    res = client.post(
        "/api/convert/batch",
        data={"preset": "technical", "dry_run": "true"},
    )
    assert res.status_code == 400
    assert res.json()["detail"]["problem"] == "No files"
