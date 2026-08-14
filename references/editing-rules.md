# Editing rules (all projects)

How to edit the DOCX package safely. Applies to every insertion/revision pass. Translation wording rules live in `translation-rules.md`.

## 1. Preservation principles

- Work on a copy of the source DOCX. Bilingualize by local insertion; never rebuild from scratch.
- Preserve the English source verbatim. Technical English fixes are a separate revision job.
- Insertion must be idempotent: detect existing Japanese; never inject twice on overwrite.
- When revising a user-edited bilingual file, base the conversion on **that file**, not the source. Keep reviewer-approved English fixes, paragraph reordering, terms, and formatting. Never regenerate from the source or an old builder (approved content would be lost).
- Keep exactly one current bilingual file. Overwrite it after incorporating review comments (add `REV#` only when needed to defeat preview cache / identify updates).
- Preserve tables, merged cells, numbering, checkboxes, styles, headers/footers, bookmarks, relationships, images, figures, embedded objects.
- Native SmartArt: add Japanese as a separate paragraph below the English inside the same shape.
- Raster flowcharts/figures: bilingual replacement keeping original dimensions, colors, shapes, connectors, order, grouping, equipment tags. English first, Japanese directly below. Procedure in `flowchart-overlay.md`.
- Connectors are managed items: after recreation, count and visually check each connector. Linear blocks share a center line with one straight line between adjacent blocks. No decorative elbows, duplicate segments, or lines entering/passing through the final block (unless present in the source).
- After conversion, compare media/figure/inline-shape/table/related-package-part counts between source and output. Test DOCX ZIP integrity.
- Floating table placement `w:tblpPr` and `w:tblOverlap` on long procedure tables: delete and inline them, so Word does not visually repeat/reopen a previous Part during pagination. Verify each Part appears once and all step IDs are unique.

## 2. Word repair-file handling

When Word reports "unreadable content" and repairs/re-saves:

- The repaired file becomes the authoritative package baseline.
- Build the next revision **from the repaired file**. Never reconstruct from the source, the broken bilingual, or a builder script.
- Keep the `document.xml`/`numbering.xml`/settings/headers/footers/custom XML/related parts as Word rewrote them. Apply local edits only.
- Do not restore `document.xml` etc. from the unrepaired file.
- Stop using the generation revision that Word could not read. If needed, ask the reviewer to keep/save a Word-repaired copy and continue only from that package.

## 3. document.xml direct-edit safety

- Never edit `document.xml` via regex string replacement (SOP-501: an edit mistake corrupted the XML). Use an XML parser (lxml etc.) as the rule; if string editing is unavoidable, **back up the docx first**.
- Always keep a backup of the user-edited state at work start (e.g. `.bak_user_edit.docx`) so user edits survive corruption.
