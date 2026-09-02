---
title: Documents API
author: md-to-docx
---

# Documents API Reference

**Version:** v1.0  
**Base URL:** `https://api.example.com/v1`

## Authentication

All requests require a Bearer token in the `Authorization` header:

```http
GET /v1/documents HTTP/1.1
Host: api.example.com
Authorization: Bearer sk_live_abc123
Content-Type: application/json
```

## Endpoints

### List Documents

```
GET /v1/documents
```

Returns a paginated list of documents.

**Query Parameters**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Max results (default 20, max 100) |
| `cursor` | string | No | Pagination cursor from previous response |
| `status` | string | No | Filter: `draft`, `published`, `archived` |

**Response**

```json
{
  "data": [
    {
      "id": "doc_7x9k2m",
      "title": "Q3 Report",
      "format": "docx",
      "status": "published",
      "created_at": "2026-09-01T10:30:00Z"
    }
  ],
  "has_more": true,
  "next_cursor": "eyJpZCI6ImRvY183eDlrMm0ifQ"
}
```

### Create Document

```
POST /v1/documents
```

Converts Markdown to DOCX and stores the result.

**Request Body**

```json
{
  "title": "Technical Report",
  "source": "# Hello\n\nThis is **markdown**.",
  "options": {
    "template": "default",
    "include_toc": false
  }
}
```

**Response** `201 Created`

```json
{
  "id": "doc_new123",
  "title": "Technical Report",
  "download_url": "https://api.example.com/v1/documents/doc_new123/download",
  "expires_at": "2026-09-02T10:30:00Z"
}
```

### Get Document

```
GET /v1/documents/{id}
```

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Document ID (e.g. `doc_7x9k2m`) |

**Response** `200 OK`

```json
{
  "id": "doc_7x9k2m",
  "title": "Q3 Report",
  "format": "docx",
  "size_bytes": 45678,
  "status": "published",
  "created_at": "2026-09-01T10:30:00Z",
  "updated_at": "2026-09-01T14:22:00Z"
}
```

### Download Document

```
GET /v1/documents/{id}/download
```

Returns the `.docx` file as `application/vnd.openxmlformats-officedocument.wordprocessingml.document`.

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `invalid_request` | 400 | Malformed JSON or missing required field |
| `unauthorized` | 401 | Missing or invalid API key |
| `not_found` | 404 | Document ID does not exist |
| `rate_limited` | 429 | Too many requests (see `Retry-After` header) |
| `internal_error` | 500 | Server error — retry with exponential backoff |

**Error Response Format**

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Field 'source' is required",
    "param": "source"
  }
}
```

## Rate Limits

| Plan | Requests/min | Concurrent conversions |
|------|-------------|------------------------|
| Free | 10 | 1 |
| Pro | 100 | 5 |
| Enterprise | 1000 | 50 |

## Webhooks

Subscribe to `document.created` and `document.failed` events. Payloads are signed with HMAC-SHA256.

```json
{
  "event": "document.created",
  "data": {
    "id": "doc_new123",
    "title": "Technical Report"
  }
}
```

## SDK Examples

### Python

```python
import requests

resp = requests.post(
    "https://api.example.com/v1/documents",
    headers={"Authorization": "Bearer sk_live_abc123"},
    json={"title": "Report", "source": "# Hello"},
)
doc = resp.json()
```

### cURL

```bash
curl -X POST https://api.example.com/v1/documents \
  -H "Authorization: Bearer sk_live_abc123" \
  -H "Content-Type: application/json" \
  -d '{"title":"Report","source":"# Hello"}'
```
