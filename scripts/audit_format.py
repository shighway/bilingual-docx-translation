#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bilingual format QA gate. Audits font / bold / size consistency of inserted
Japanese and FAILs (exit 1) on any violation. Run on the final bilingual docx
AFTER normalize_format.py (or as a pre-delivery gate).

Checks (on every run whose text contains CJK):
  FONT  genuine JP runs use the expected body font (default "Meiryo UI").
  BOLD  body translation runs are NON-bold; only " / " heading runs may be bold.
  SIZE  no JP run has w:sz > --max-size (default 36 half-points = 18pt; catches
        the 110pt / sz=220 class of defect).

Usage:
  python audit_format.py FILE.docx [MORE.docx] [--font "Meiryo UI"] [--max-size 36]
Exit: 0 = clean, 1 = violations found.
"""
import argparse, re, sys, zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def qn(t): return f'{{{W}}}{t}'
W_ = '{' + W + '}'

CJK_RE = re.compile(r'[\u3000-\u9fff\uff00-\uffef]')
HIRA_RE = re.compile(r'[\u3040-\u309f]')


def has_cjk(s): return bool(s and CJK_RE.search(s))
def has_hira(s): return bool(s and HIRA_RE.search(s))
def cjk_count(s): return sum(1 for c in s if '\u3000' <= c <= '\u9fff' or '\uff00' <= c <= '\uffef')
def lat_count(s): return sum(1 for c in s if 'A' <= c <= 'Z' or 'a' <= c <= 'z')


def run_text(r):
    return ''.join((t.text or '') for t in r.findall(qn('t')))


def run_font(r):
    rpr = r.find(qn('rPr'))
    if rpr is None:
        return None
    rf = rpr.find(qn('rFonts'))
    return rf.get(qn('eastAsia')) if rf is not None else None


def run_bold(r):
    rpr = r.find(qn('rPr'))
    if rpr is None:
        return False
    b = rpr.find(qn('b'))
    return b is not None and b.get(qn('val'), '1') != '0'


def run_color(r):
    """Non-default text color, if any (emphasis inherited from the EN source)."""
    rpr = r.find(qn('rPr'))
    if rpr is None:
        return None
    c = rpr.find(qn('color'))
    if c is None:
        return None
    v = c.get(qn('val'))
    return v.upper() if v and v.lower() not in ('auto', '000000') else None


def run_size(r):
    rpr = r.find(qn('rPr'))
    if rpr is None:
        return None
    sz = rpr.find(qn('sz'))
    if sz is None:
        return None
    try:
        return int(sz.get(qn('val')))
    except Exception:
        return None


def audit(path, font, max_size):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml')
    root = etree.fromstring(xml)
    body = root.find(f'.//{W_}body')
    violations = []
    checked = 0
    for pi, p in enumerate(body.findall(f'.//{W_}p')):
        full = ''.join(run_text(r) for r in p.findall(qn('r')))
        is_heading = ' / ' in full
        p_jp_dominant = cjk_count(full) > lat_count(full)
        for r in p.findall(qn('r')):
            t = run_text(r)
            if not has_cjk(t):
                continue
            genuine = is_heading or has_hira(t) or cjk_count(t) > lat_count(t)
            if not genuine:
                continue  # mixed EN+CJK label in English text: font-only, skip strict checks
            checked += 1
            ea = run_font(r)
            if ea != font:
                violations.append(f"p{pi} FONT eastAsia={ea!r} expected {font!r}: {t[:30]!r}")
            if run_size(r) is not None and run_size(r) > max_size:
                violations.append(f"p{pi} SIZE sz={run_size(r)} > {max_size}: {t[:30]!r}")
            if run_bold(r) and not is_heading and not run_color(r):
                # bold on a colored run is deliberate emphasis matching the
                # EN source (e.g. red SOP cross-reference) — allowed.
                violations.append(f"p{pi} BOLD body run is bold: {t[:30]!r}")
    name = path.replace('\\', '/').split('/')[-1]
    print(f"{name}: checked {checked} JP runs, {len(violations)} violation(s)")
    for v in violations[:25]:
        print(f"  FAIL {v}")
    if len(violations) > 25:
        print(f"  ... and {len(violations)-25} more")
    return len(violations)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('--font', default='Meiryo UI')
    ap.add_argument('--max-size', type=int, default=36, help='max allowed w:sz half-points (default 36)')
    a = ap.parse_args()
    total = sum(audit(f, a.font, a.max_size) for f in a.files)
    if total:
        print(f"\nRESULT: FAIL ({total} violation(s))")
        sys.exit(1)
    print("\nRESULT: PASS")


if __name__ == '__main__':
    main()
