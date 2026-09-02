---
title: Sprint Planning Meeting
date: 2026-09-02
---

# Sprint Planning — September 2, 2026

**Attendees:** Alice (PM), Bob (Eng Lead), Carol (Design), Dave (QA)  
**Duration:** 60 minutes  
**Location:** Conference Room B / Zoom

## Agenda

1. Review last sprint outcomes
2. Prioritize backlog items
3. Assign owners and deadlines
4. Identify blockers

## Last Sprint Recap

- Shipped batch conversion CLI flags (`--dry-run`, `--output-dir`)
- Fixed table normalization bug in CJK headings
- Deferred template marketplace to Q4

> Sprint velocity: 34 points completed (planned 38). Two stories carried over.

## Decisions

1. **P0 productization** is the top priority for this sprint
2. Examples gallery ships before GitHub templates
3. No new engine work until Document AST design is approved
4. WeCom import docs remain but are not the primary positioning

## Action Items

- [ ] Alice — finalize README copy by Wednesday
- [ ] Bob — create 7 example documents and verify conversion
- [ ] Carol — design logo and demo assets
- [ ] Dave — add CI step for examples conversion
- [ ] Bob — write `SECURITY.md` and issue templates
- [ ] Alice — update CHANGELOG for P0 release

## Backlog Priorities

| Priority | Item | Owner | Target |
|----------|------|-------|--------|
| P0 | README repositioning | Alice | Sep 5 |
| P0 | Examples gallery | Bob | Sep 6 |
| P0 | GitHub templates | Bob | Sep 6 |
| P1 | Document AST design | Bob | Sep 15 |
| P1 | Template presets | Carol | Oct 1 |
| P2 | PyPI publish decision | Alice | TBD |

## Discussion Notes

### Examples Gallery

Bob proposed 7 curated examples covering technical, business, academic, API, meeting, AI, and Chinese content. Each example should convert with pandoc only (no mmdc dependency for CI).

### Branding

Carol will deliver minimalist SVG logo (`MD → DOCX`) in near-black (#111827). No mascot, no gradients.

### CI

Dave confirmed the examples conversion step can run on the existing Ubuntu matrix without mermaid-cli.

## Blockers

- None currently

## Next Meeting

**Date:** September 9, 2026  
**Focus:** P0 acceptance review and P1A kickoff

## Parking Lot

- Web playground (deferred to P2)
- VS Code extension (deferred to P3)
- MCP server (deferred to P4)
