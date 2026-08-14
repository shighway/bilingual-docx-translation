# Incident log (reference only)

Backgrounds of past failures that produced current rules. Each rule now lives in the rule files; this file is cited from them. Read when unsure why a rule exists or when touching related code.

| Incident | What happened | Rule it produced | Where |
|---|---|---|---|
| SOP-306 | Flowchart image (`Flowchart:` cell) left English-only | Never follow English-only precedents; always bilingualize via overlay | flowchart-overlay.md |
| SOP-308/309/310 | deepcopy insertion inherited fonts/bold/sizes → 宋体/メイリオ/Calibri mixing, bold body, `sz=220` (110pt) breakage | Format gate mandatory: normalize → inherit_color → audit_format | qa-gates.md §2 |
| SOP-309 | EN partial coloring (red SOP refs, green HMI paths) lost in JP (only `runs[0]` color inherited) | `inherit_color_emphasis.py` after normalize | qa-gates.md §2 |
| SOP-903 | EN steps bold only the leading verb → JP whole sentence bold | Partial-bold rule: bold only the JP sentence-final verb phrase | qa-gates.md §2 |
| SOP-310 | Full-redraw swap changed pixel dimensions → `wp:extent` destroyed → 14.6in display | Overlay default; `--fix-extent` to restore EMU | flowchart-overlay.md |
| SOP-310 v2 | Black 4-direction outline on 10px Meiryo → everything looks bold/stencil | White text drawn directly, no outline | flowchart-overlay.md |
| SOP-501 | Regex string edit on `document.xml` corrupted XML | Parser-based editing; mandatory pre-edit backup (`.bak_user_edit.docx`) | editing-rules.md §3 |
| SOP-501 | Underlined EN runs propagated `w:u` to whole JP lines | normalize removes body underline; audit FAILs full underline | qa-gates.md §2 |
| SOP-501 | JP rows in the final table pushed the trailing empty paragraph to a blank new page | Shrink trailing empty paragraph to 1pt fixed | qa-gates.md §2 |
| SOP-102 | Backout procedure mistranslated as root-cause investigation (changed mandatory response) | Never use as precedent | projects/ksw.md defects |
| SOP-202 | BMS vendor escalation note had visually truncated/corrupt Japanese | Never reuse as translation memory | projects/ksw.md defects |
| SOP-208 C33 | English-only touch-panel instruction slipped through | Completeness check for English-only procedure cells | qa-gates.md §7 |
| SOP-209 | `≤3°C` vs `<3℃` mismatch | Operators/thresholds are technical data to reconcile | projects/ksw.md defects |
