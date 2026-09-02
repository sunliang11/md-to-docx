---
title: Technical Design Document
author: Engineering Team
date: 2026-09-02
---

# System Overview

This sample demonstrates the **technical-design** template with ODM callouts and tables.

:::info
This template is optimized for architecture and API documentation.
:::

## Components

| Component | Role | Status |
|-----------|------|--------|
| Parser | Markdown → AST | Stable |
| Renderer | AST → DOCX | Stable |
| Plugins | Transform hooks | Beta |

## Code Example

```python
from md_to_docx.api import convert

convert("report.md", preset="technical")
```

:::warning
Always validate Markdown with `--check` before publishing.
:::
