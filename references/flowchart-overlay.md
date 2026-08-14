# Raster flowchart bilingualization — overlay method

Read this file only when the target SOP contains a raster (image) flowchart. Verified on SOP-310/501/903. Incident backgrounds: `incident-log.md`.

## Policy

- **Overlay (draw Japanese on top of the original image) is the default**, via `scripts/build_flowchart_bilingual.py` (easyocr + Pillow). Full redraw is last resort only: it breaks the original visual (colors/connectors/grouping) and can destroy `wp:extent` (SOP-310: image displayed at 14.6in). Overlay keeps pixel dimensions identical, so extent is unchanged.
- Even when a reference precedent left the flowchart English-only (SOP-306 etc.), do **not** treat that as a reason to keep English. Always bilingualize; never defer this to "review items".

## Procedure

1. **Locate the source image**: use `r:embed` occurrence order in `document.xml` plus `document.xml.rels` to determine which `word/media/imageN.*` sits in the `Flowchart:` cell (SOP-501/903: `image2.png`/`image2.jpeg`). Extract from `word/media/`.
2. **OCR + box detection**: `python scripts/build_flowchart_bilingual.py --ocr SRC.png --dump labels.json`. easyocr (`Reader(['en'], gpu=False)`) extracts English label bboxes; a non-white mask `~((r>230)&(g>230)&(b>230))` connected-components pass detects colored-box rectangles. Fill in `"jp"` for each label (translate). External vision APIs often reject local paths — easyocr is reliable.
3. **Overlay + swap**: `--src SRC.png --labels labels.json --docx OUT.docx --media image2.png`. `zipfile` replaces the target `word/media/imageN.*` and recompresses. Filename/path/relationships unchanged. If a full-redraw version with different pixel dimensions was swapped in before, restore the original display size with `--fix-extent CxCy_EMU --docx OUT.docx --media imageN.png` (SOP-310: `4144488x5035138` = 4.53in×5.51in).
4. **QA**: after swap run `audit_docx.py` (`inline_shapes`/`media_parts`/`tables` identical to source, `zip_integrity:True`); re-run `--ocr` to verify every label is EN+JP with no clipping (never rely on eyesight or inference); confirm no repair dialog on Word COM re-save.

## Overlay positioning principles (implemented in the script)

- **Dual coordinate system**: horizontal — center on the actual colored-box rectangle and clip the pill background to the box boundary (the OCR text bbox is narrower than the box; centering on it overflows). Vertical — OCR English text bottom edge Y+3px (the box bottom edge Y sits ~30px below the text, which separates EN and JP).
- **Color-detection pitfall**: an OR test like `(channel>200)` misses saturated colors where **all channels are <200** — purple (111,47,161), blue (47,85,151), green (84,130,53). Always use the non-white mask `~((r>230)&(g>230)&(b>230))`.
- Japanese rendering: `Meiryo` (`C:/Windows/Fonts/meiryo.ttc`) 10–11px, white text drawn **directly (no outline)** — a black 4-direction outline makes ~10px Meiryo look fully bold/stencil-like (SOP-310 v2) and is forbidden. Pill background samples the dominant non-white color inside the box.
- **No canvas extension**: if a pill would exceed the box bottom, extend the box fill color seamlessly full-width downward to fit (image dimensions and aspect ratio unchanged). White-background diamonds and similar: draw black text directly with no pill (`"dark": true` + `"cx"`/`"y"` in the labels JSON).
- **Font width**: if the text does not fit the box width, shrink one step only (11→10px); if it still does not fit, assert and fail (prevents silent 9px shrink to illegibility).

## Full-redraw fallback only (SOP-309 method)

Keep original aspect ratio and size. Use the original's **saturated colors as fills** (via `getcolors`) — no pastel conversion; saturated background + white text in the source means the same in the recreation; sample arrow colors from the original; match the original corner radius.
