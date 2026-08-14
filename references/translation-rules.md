# Translation rules (all projects)

Common translation and bilingual-presentation rules. Project-specific formats/terms live in `projects/<project>.md` and take precedence. XML-editing safety lives in `editing-rules.md`.

## 1. Terminology reference hierarchy (when references conflict)

1. Verified equipment labels, approved drawings, OEM terminology, statutory/safety requirements.
2. English source and SME-confirmed operational intent.
3. Terms consistently repeated across multiple approved documents.
4. These common rules (this file).
5. Project living-translation base (`projects/<project>.md`).
6. A single past translation — existing alone is not enough to overturn stronger evidence.

## 2. Client-name neutralization

Search for and remove company names that denote the client organization (Microsoft, Google, etc.).

- Delete the company name. Prefer simple deletion when the remaining sentence is complete and natural (e.g. `Microsoft Datacenter Work Rules and Regulations` → `Datacenter Work Rules and Regulations`; the Japanese translation also refers to `Datacenter Work Rules and Regulations` directly — do not add `クライアント`).
- Use `Client`/`クライアント` only when the sentence needs an organization/owner/approver/possessive/grammatical subject.
- Never replace one real client name with another real client name.
- Do not change company names denoting OEMs, contractors, software/product names, statutory bodies, or other non-client entities.
- If the role is ambiguous, do not guess — send to review.
- Search scope is not just body paragraphs: include table cells, headers/footers, text boxes, shapes, SmartArt, comments, relationships and related package parts (`Document.paragraphs` alone is insufficient).

## 3. Translation fidelity

- Preserve every action, condition, tag, state, limit, timing value, unit, warning, responsible role, acceptance criterion.
- Use project-specific natural control Japanese and established technical terms. Avoid English word order and dictionary-literal translation.
- Procedure register per project file (e.g. non-polite terminal form `〜する。`, `〜ことを確認する。`).
- Equipment tags, document IDs, system abbreviations, paths, HMI/panel labels, room names, equipment names are invariant.
- Never insert technical assumptions to make unclear English fluent. Keep it and report.
- Review-required: safety, switching authority, LOTO, chemical handling, statutory titles, unclear technical states.
- Repeated English phrases get the same Japanese translation (unless context truly differs).

## 4. Bilingual presentation rules

### Placement and language blocks

- Keep the existing document structure, line order, numbering, merged cells, checkboxes, sign-off fields, warnings, backout sections.
- Bilingual cells: English first, Japanese as the immediately following new paragraph/line.
- Define language blocks by logical group, not by first sentence: instruction followed by English path/option/tag/panel/equipment lines is one English block. The complete Japanese instruction and its corresponding path/tag lines come only after the complete English group. Never interleave Japanese before subsequent English path/tag lines.
- Activity Description: complete English block → complete Japanese block. Never let Japanese split the English block.
- Underlined internal subheadings: put `English / 日本語` in the same paragraph, matching source formatting. Do not add a duplicated heading paragraph. Underline must not leak into body/action paragraphs.
- Multi-branch steps: repeat `bilingual branch heading → English actions → Japanese actions` per branch, before the next branch. Do not repeat the condition as a Japanese action prefix unless needed to avoid true ambiguity or as a definite reference. Never collect all English branches first with Japanese summarized at the bottom.
- Steps segmented by source subheadings: replace the original underlined subheading in place with `English / 日本語`; then complete English → complete Japanese under each heading, then next.
- Steps with visuals: English block → Japanese block → table/photo. Photos and tables stay in the original cell, in the original relative order.
- Document-generation flags (`[Insert PME Screenshot ...]` etc.) stay English; no Japanese version added. Place the flag after the complete English instruction + Japanese translation. The actual operational instruction to take/record the screenshot **is** translated.
- No empty paragraph between an English action and its Japanese translation. At most one empty paragraph between distinct logical/content blocks. Delete consecutive visible empty paragraphs (keeping format and the English→Japanese→visual order).

### Protected / untranslated content

- target-equipment selection cells (`Circle`/`Mark``/`Tick the target equipment`): protected source data. Copy the complete cell structure from **this SOP's own source** (never a past SOP or translation reference, even if the template looks identical) and insert only the Japanese instruction. Preserve category headings, checkboxes, equipment names, asset tags, order, spelling, whitespace, nested-table structure.
- Location/Equipment column values are fixed data: room names, equipment names, panel names, tags, asset labels stay verbatim.
- Panel labels and alarm texts stay exactly as displayed. When a Japanese explanation is needed, keep the literal label in quotes and translate only the surrounding instruction.
- Keep checkbox marks and their associations. `ON`/`OFF`/`OPEN`/`CLOSED`/`Auto`/`Manual` untranslated when literal panel indications; add Japanese in parentheses only if the reference style requires.
- Touch-panel operations: keep button text fully and use `「[label]」ボタンを押す。`. Keep menu/status strings fully.
- Application paths fully preserved (case and delimiters): `PME > DIAGRAMS > OVERVIEW`. Repeat the complete relevant HMI/application path in each branch; never replace with vague wording like `同画面にて`.

### Translated side content

- Translate operational content in Field Comments, notes, expected outcomes, side lists, figure captions, and flowchart outside-box labels (unless a documented exclusion applies). Preserve checkboxes, list formatting, underline headings, colors, alignment, and the English-first/Japanese-second order. Never assume the Operation column is the only bilingual area.
- Empty Expected Outcome cells: do not fill by inference; list them in post-delivery review reminders (unless the project file specifies auto-completion, e.g. KIX1's 109 pattern).

### Formatting of inserted Japanese

- Preserve source alignment, indent, size, emphasis, and text color in the Japanese translation. Centered English → centered Japanese; vertical alignment preserved. Normal actions left-aligned unless explicitly centered. Cell vertical centering does not authorize horizontal centering.
- Text color: if English is red/green/other intentional color, apply the same RGB/theme color to the Japanese. Partial coloring (red warnings / green HMI paths) colors only the corresponding Japanese segment.
- Procedure step paragraphs: 1.0 line spacing, 0pt before/after (approved exceptions aside). Do not rely on inherited paragraph styles.
- Photos/nested tables stay physically inside the source operation cell. Photos are `wp:inline`, never floating anchors. With both, place after the related table. If a row is too tall, remove `cantSplit`/fixed/exact row-height constraints so Word can break the page — never resize/detach/move a photo to another line just to fit.
- Translatable operation section/Part headings use the inline `English heading / 日本語見出し` form (project files specify full/half-width slash rules); keep heading alignment/emphasis. Do not use inline form when changing literal equipment/HMI labels.
- Part headings are static visible text: if a `REF ... \h` field has a missing bookmark, flatten the cached heading to normal formatted text (so Part H and later do not jump to the document start).
- Flowcharts: translate every meaningful string (outside-box text, branch labels, route captions, connector annotations, legends). Japanese directly below the corresponding English; keep source positions and connector spacing.
- Native SmartArt: English→Japanese as separate paragraphs. Raster flowcharts: keep the original visual system and add inline bilingual text (see `flowchart-overlay.md`).
