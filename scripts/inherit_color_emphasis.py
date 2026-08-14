#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Inherit partial color (and bold) emphasis from the EN source paragraph into
its JP translation paragraph, for literal segments that appear verbatim in both
(typical: HMI/app paths, SOP/document cross-references).

For each EN paragraph that carries a non-default color not yet present in the
immediately-following JP paragraph, the JP run is split so the matching literal
segment receives the same color (and bold, if the EN segment is bold). The rest
of the JP keeps its body face. Idempotent.
"""
import re, shutil, zipfile, sys
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def qn(t): return f'{{{W}}}{t}'
W_ = '{' + W + '}'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'
JP = re.compile(r'[\u3000-\u9fff\uff00-\uffef]')


def has_jp(s): return bool(s and JP.search(s))
def run_text(r): return ''.join((t.text or '') for t in r.findall(qn('t')))


def run_color(r):
    rpr = r.find(qn('rPr'))
    if rpr is None:
        return None
    c = rpr.find(qn('color'))
    if c is None:
        return None
    v = c.get(qn('val'))
    return v.upper() if v and v.lower() not in ('auto', '000000') else None


def run_bold(r):
    rpr = r.find(qn('rPr'))
    if rpr is None:
        return False
    b = rpr.find(qn('b'))
    return b is not None and b.get(qn('val'), '1') != '0'


def para_colors(p):
    return {run_color(r) for r in p.findall(qn('r')) if run_text(r).strip()}


def en_colored_spans(en_p):
    """Merged (literal, color, bold) spans for consecutive same-color EN runs."""
    out = []
    for r in en_p.findall(qn('r')):
        rt = run_text(r)
        if not rt:
            continue
        col = run_color(r)
        bold = run_bold(r)
        if col:
            if out and out[-1][1] == col:
                out[-1] = (out[-1][0] + rt, col, out[-1][2] and bold)
            else:
                out.append((rt, col, bold))
    return out


def find_literal(text, lit, pos):
    """Return (idx, matched_text) for lit in text from pos; fall back to
    stripping trailing punctuation. Else (-1, None)."""
    idx = text.find(lit, pos)
    if idx >= 0:
        return idx, lit
    stripped = lit.rstrip(' .,;:。、，；：')
    if stripped and stripped != lit:
        idx = text.find(stripped, pos)
        if idx >= 0:
            return idx, stripped
    return -1, None


def build_segments(full, spans):
    """Plan (text, color, bold) segments over `full`, coloring matching spans."""
    segs, pos, applied = [], 0, 0
    for lit, col, bold in spans:
        idx, matched = find_literal(full, lit, pos)
        if idx < 0:
            continue
        if idx > pos:
            segs.append((full[pos:idx], None, None))
        segs.append((full[idx:idx + len(matched)], col, bold))
        pos = idx + len(matched)
        applied += 1
    if not applied:
        return [], 0
    if pos < len(full):
        segs.append((full[pos:], None, None))
    return segs, applied


def apply_spans(jp_p, spans):
    """Split the JP paragraph's runs so matching literals get color+bold.
    spans: list of (literal, color, bold). Returns count applied."""
    runs = jp_p.findall(qn('r'))
    if not runs:
        return 0
    full = ''.join(run_text(r) for r in runs)
    base_rpr = runs[0].find(qn('rPr'))
    segs, applied = build_segments(full, spans)
    if not applied:
        return 0
    for r in runs:
        jp_p.remove(r)
    for text, col, bold in segs:
        if text == '':
            continue
        nr = etree.SubElement(jp_p, qn('r'))
        nrpr = etree.SubElement(nr, qn('rPr'))
        if base_rpr is not None:
            for child in base_rpr:
                nrpr.append(etree.fromstring(etree.tostring(child)))
        if col:
            c = nrpr.find(qn('color'))
            if c is None:
                c = etree.SubElement(nrpr, qn('color'))
            c.set(qn('val'), col)
        if bold is not None:
            for tag in ('b', 'bCs'):
                el = nrpr.find(qn(tag))
                if el is None:
                    el = etree.SubElement(nrpr, qn(tag))
                el.set(qn('val'), '1' if bold else '0')
        nt = etree.SubElement(nr, qn('t'))
        nt.set(XMLSPACE, 'preserve')
        nt.text = text
    return applied


def process(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml')
    root = etree.fromstring(xml)
    body = root.find(f'.//{W_}body')
    ps = body.findall(f'.//{W_}p')
    total = 0
    for i, p in enumerate(ps):
        en_text = ''.join(run_text(r) for r in p.findall(qn('r')))
        spans = en_colored_spans(p)
        if not spans or has_jp(en_text):
            continue
        if i + 1 >= len(ps):
            continue
        nxt = ps[i + 1]
        nxt_text = ''.join(run_text(r) for r in nxt.findall(qn('r')))
        if not has_jp(nxt_text):
            continue
        # only if JP lacks at least one EN color
        jp_cols = para_colors(nxt)
        missing = [s for s in spans if s[1] not in jp_cols]
        if not missing:
            continue
        n = apply_spans(nxt, missing)
        if n:
            total += n
            print(f"  p{i}->p{i+1}: applied {n} color span(s) | EN: {en_text[:55]!r}")
    out = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    tmp = path + '.tmp'
    with zipfile.ZipFile(path, 'r') as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            zout.writestr(item, out if item.filename == 'word/document.xml' else zin.read(item.filename))
    shutil.move(tmp, path)
    print(f"  total spans applied: {total}")


if __name__ == '__main__':
    for f in sys.argv[1:]:
        print(f"Color-inherit: {f.split('/')[-1]}")
        process(f)
