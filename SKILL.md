---
name: bilingual-docx-translation
description: データセンターEOP/SOPのWord文書を、プロジェクト別フォーマットと翻訳ルールに従ってバイリンガル（EN→EN+JP）化。KIX1/KSW/STACK等のプロジェクト固有ルールは別ファイル管理、共通する運用・QAプラクティスを汎用基盤として提供。docx XMLを直接編集し、書式・図・SmartArt・ヘッダ/フッタを保持。「翻訳」「bilingual」「JP_EN」「日本語併記」の指示、またはデータセンターEOP/SOPの.docxをバイリンガル化するときに使用。
---

# Bilingual DOCX Translation (Project-aware)

Convert data-center EOP/SOP Word documents to bilingual (EN → EN+JP) by editing docx XML in place. Formatting, figures, SmartArt, headers/footers preserved. **Formats and translation rules differ per project** — project-specific rules live in separate files; this skill defines only the common base.

## Project identification

Judge from filename/content; ask the user only if undeterminable.

| Project | Signal | Rules file | Notes |
|---|---|---|---|
| KIX1 | `KIX1 *.docx`, VDC template (BLDG-EOP/FIRE-EOP/MVAC-EOP/VDC-KIX1-EOP) | `projects/kix1.md` | `eop-translation` skill has tooling/track record |
| KSW | `KSW-*.docx`, SOP template | `projects/ksw.md` | |
| STACK | STACK documents | `projects/stack.md` | awaiting source |

## Reference loading (conditional — load per phase, not all upfront)

| File | Load when |
|---|---|
| `projects/<project>.md` | Always, before translating |
| `references/translation-rules.md` | Translation phase (preservation, bilingual layout, client-name neutralization) |
| `references/editing-rules.md` | Before XML insertion; whenever Word reports unreadable content |
| `references/qa-gates.md` | QA phase (checklists + script gates) |
| `references/flowchart-overlay.md` | Only when the SOP has a raster flowchart image |
| `references/incident-log.md` | Reference only (cited from other files) |

Also follow the docx skill's render-and-verify workflow where available.

## Workflow

1. **Source & output** — work on a copy; never modify the source. For revisions, patch the latest user-edited bilingual file (see `references/editing-rules.md`). If Word repaired a file, the repaired file is the new baseline. Keep one current bilingual file. Never silently fix dubious English — keep and report.
2. **Pre-translation inventory** — record section order, tables, merged cells, row/column structure, inline/floating shapes, media, figures, headers/footers, bookmarks, embedded objects. Identify: English-maintained sections (per project file); SOP names, Activity Descriptions, operation steps, Part headings, flowcharts, backout procedures, sign-off headings, photos, nested tables, colored text, underlined internal headings; fixed Location/Equipment values and untranslatable literal labels; target-equipment selection steps (`Circle`/`Mark`/`Tick the target equipment` — inventory headings/checkboxes/equipment/tags **from this SOP's own source**, never from past SOPs or translations); Field Comments, notes, expected outcomes, side lists, figure captions, flowchart outside-box labels.
3. **Translate** — per `references/translation-rules.md` + project file. Keep all tags, paths, labels, values, states, units, warnings, responsible roles, acceptance criteria. Natural control Japanese per project style. Review-required: safety, switching authority, LOTO, chemical handling, statutory titles, unclear technical states.
4. **Insert JP locally (no rebuild)** — per `references/editing-rules.md` + project-file exclusions. English blocks first, Japanese immediately after. Idempotent.
5. **Language/technical QA** — per `references/qa-gates.md` checklists.
6. **Structural/visual QA** — run the script gates below; render pages and inspect; re-run audits after final edits.
7. **Clean delivery** — deliver the current bilingual DOCX; keep the source. Delete disabled copies only with user approval. Summarize changes; list reviewer reminders and open technical questions separately. Never call it "approved" until the user/approved reviewer approves.

## Script gates (details and QA procedure in `references/qa-gates.md`)

- `scripts/audit_docx.py SOURCE.docx [MORE.docx] [--json]` — read-only structural audit.
- `scripts/audit_equipment_lists.py SOURCE.docx BILINGUAL.docx [--json]` — required when a target-equipment step exists; exit 1 = FAIL.
- `scripts/normalize_format.py OUTPUT.docx [--font ...]` — mandatory right after build (idempotent).
- `scripts/inherit_color_emphasis.py OUTPUT.docx` — when source EN has partial coloring.
- `scripts/audit_format.py OUTPUT.docx [--font ...]` — 0 violations = PASS, exit 1 = FAIL.
- `scripts/build_flowchart_bilingual.py` — raster flowchart bilingualization (see `references/flowchart-overlay.md`).

## Minimum acceptance criteria

- English source preserved verbatim; Japanese natural for local Japanese engineers; English-maintained sections untouched.
- Proper nouns, tags, paths, labels, values, states exact. target-equipment lists match this SOP's source exactly (no inheritance from reference SOPs).
- EN/JP alignment and intentional text colors match. Photos/tables placed after both language blocks, kept in original cells.
- Flowcharts keep the original visual system; all labels (boxes, branches, captions, annotations, outside-box) bilingual.
- DOCX package integrity pass with explained structural diffs; page-by-page visual QA pass, or explicitly reported impossible.

## Adding a new project

Create `projects/<project>.md` when a source arrives: record template structure, punctuation, glossary, English-maintained sections, numbering scheme, cautions. Check `projects/README.md` for cross-project conflict rules (comma width, chief-electrical-engineer translation, etc.) — mixing them up is strictly forbidden.

## User operation settings

- **No plan mode.** On an instruction like "〇〇のbilingual作成", skip confirmation/questions/plan mode and run the one-pass pipeline immediately: project identification → 03 Second Draft → 04 Bilingual Procedure.
- If the target draft is unclear, auto-select the latest draft (highest-numbered folder).
- If an approved reference bilingual exists, patch it as the base.
