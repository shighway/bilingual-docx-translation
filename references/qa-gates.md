# QA gates (all projects)

Checklists and mandatory script gates. Project-specific values (`--font`, body size) live in `projects/<project>.md`. Incident backgrounds: `incident-log.md`.

## 1. Script commands

```bash
# Structural audit (compare source vs output)
python scripts/audit_docx.py SOURCE.docx OUTPUT_JP_EN.docx

# target-equipment selection verification (when such a step exists; exit 1 = mandatory FAIL)
python scripts/audit_equipment_lists.py SOURCE.docx OUTPUT_JP_EN.docx

# Format normalization (mandatory after all insertion, before delivery; idempotent)
python scripts/normalize_format.py OUTPUT_JP_EN.docx [--font "Meiryo UI" --body-size 18]

# Format QA gate (1 violation = exit 1 = undeliverable)
python scripts/audit_format.py OUTPUT_JP_EN.docx [--font "Meiryo UI" --max-size 36]

# Partial color-emphasis inheritance (when source EN has partial coloring; run after normalize)
python scripts/inherit_color_emphasis.py OUTPUT_JP_EN.docx

# Raster flowchart bilingualization (see flowchart-overlay.md)
python scripts/build_flowchart_bilingual.py --ocr SRC.png --dump labels.json
python scripts/build_flowchart_bilingual.py --src SRC.png --labels labels.json \
    --docx OUTPUT_JP_EN.docx --media image2.png
```

Dependencies: `python-docx`, `lxml`, `Pillow`, `numpy` (`easyocr` only for OCR assist).
`pip install python-docx lxml pillow numpy easyocr`

## 2. Format gate is not optional

`deepcopy`-based insertion unconditionally inherits the source run's font/bold/size, so without normalization you always get font mixing (宋体/メイリオ/Calibri), bold body text, and broken sizes (110pt = `sz=220`). Every run: `normalize_format.py` → `inherit_color_emphasis.py` (if partial coloring) → `audit_format.py` PASS. `--font` is project-specific (KSW = Meiryo UI; KIX1 separate).

### Partial-bold rule (SOP-903)

When source EN action steps bold **only the leading verb** (`Conduct`/`Confirm`/`Refer`...), the deepcopy-inserted JP inherits the bold `runs[0]` and the whole sentence becomes bold. Instead bold only the corresponding Japanese verb phrase (English leading verb = Japanese sentence-final verb phrase: `確認する。` `参照する。` `実施する。` etc.). Fix = "unbold whole paragraph → re-bold only the verb phrase (split runs, keep color/font)". `audit_format.py` flags fully-bold JP paragraphs **without** color emphasis as violations (partial bold and colored full bold are legitimate).

### Underline inheritance (SOP-501)

Deepcopying an underlined EN run (e.g. label `Fuel Type – Fuel Oil A (A重油)`) propagates `w:u` to the whole JP line. `normalize_format.py` removes `w:u` from body JP runs automatically; `audit_format.py` FAILs fully-underlined JP paragraphs (bilingual underline headings are the allowed exception).

### End-of-document empty-paragraph push-out (SOP-501)

Adding JP rows to the last table (backout/sign-off) can push the trailing empty paragraph onto a new page, blanking the final page. After adding rows to a final table, shrink the trailing empty paragraph to 1pt with fixed line height to keep the original page count (verify final page via Word COM and save).

## 3. Technical fidelity checklist

- Every step, condition, expected result, warning, responsible role, location, tag, state, timing value, unit exists in both languages.
- Equipment tags, alarm names, HMI paths, drawing references, document numbers match the source exactly.
- target-equipment selection cell matches this SOP's source exactly (XML/paragraph level). Any missing/changed/reordered item or substitution from another SOP = FAIL. Run `audit_equipment_lists.py`.
- No real client company names remain; deletions read naturally; `Client`/`クライアント` only where grammatically/semantically required; product/OEM/contractor/body names verbatim.
- Independently verify `OPEN/CLOSED`/`ON/OFF`/input-output/before-after/isolate-restore/main-standby direction, all comparison operators and limits (`<`/`≤`/`>`/`≥`/ranges/time/%/temperature/pressure/voltage) across EN and JP.
- Do not conflate remote commands, field actions, expected automatic responses, and verification steps.
- LOTO steps keep lock ownership, tag data, test points, voltage class, stored-energy discharge, commissioning requirements.
- Chemical-handling steps verified against the relevant SDS and project/QHSE requirements.

## 4. Language consistency checklist

- Control-style `〜する。／〜ことを確認する。` register (per project).
- Repeated English phrases → identical Japanese (unless context truly differs).
- Literal screen/panel labels kept, clearly distinguished from narrative translation.
- English abbreviations kept; Japanese expansion only when useful and consistent.

## 5. Document integrity checklist

- Table structure, merged cells, row numbering, checkboxes, sign-off fields, warnings, backout sections preserved.
- Japanese placed with its corresponding English — never in an adjacent wrong line/cell.
- No clipped/occluded/duplicated text, or text separated from its checkbox/field.
- Header/footer, revision data, page numbers, document title correct.
- Document Control/Annual Review sections verbatim (unless the project file says otherwise); administrative/pre-execution form sections English-maintained per project file.
- Location/Equipment column values verbatim.
- Field Comments etc. bilingual unless a documented exclusion exists; checkbox/list formatting kept.
- Native SmartArt: EN→JP as separate paragraphs. Raster flowcharts: original visual system with inline bilingual text; all meaningful labels bilingual (branch captions/route labels/annotations/legends/outside-box).
- Steps with figures: English block → Japanese block → related photos (all photos last).
- Each Japanese translation keeps its English's intentional color emphasis.
- Internal subheadings: exactly one bilingual underlined heading, with the EN/JP pair before the next subheading. Duplicated headings, Japanese collected at the bottom, or underline leaking into body = FAIL.
- Multi-branch steps repeat `bilingual branch heading → EN actions → JP actions` per branch.
- Photos/nested tables kept inside the source operation cell; tall visual rows can break across pages.
- Empty Expected Outcome cells: no inference; listed in review reminders (unless project file specifies auto-fill).
- All placeholders and reviewer questions resolved or visibly listed.
- Word-repaired files: generated from the repaired package; no unrestored XML parts brought back.

## 6. Numbering check

Inspect every `#` cell in `document.xml` and `numbering.xml`: numbered paragraphs must be either "auto numbering only (no typed identifier)" or "typed identifier only (no `w:numPr`)". Both present = FAIL. Cross-references like `#D11–#D13` have no trailing period.

## 7. Structural and visual QA

- Run `audit_docx.py` on source and bilingual output; investigate every unexpected diff. After insertion, only `table_paragraphs` and `japanese_paragraphs` should increase (tables/inline_shapes/media/auto-numbered cells/package_parts/client-name candidates identical to source).
- Dump all procedure-cell EN/JP pairs: verify every English action has a Japanese pair, protected data untouched, English-maintained sections intact, no English-only procedure cells.
- Word COM check (`Documents.Open` with `OpenAndRepair=False` + `SaveAs` PDF): no repair dialog or exception. Any repair report = discard that revision → rebuild from `03`.
- Render the bilingual DOCX page by page and inspect: line wrapping, page breaks, merged cells, borders, clipping, photo/table containment, flowcharts, header/footer, dense Japanese cells.
- If rendering is impossible, report that limitation and do not claim visual QA pass. Structural QA is not a substitute for rendering.
- Re-open the DOCX after final edits and re-run audits.
