#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Post-build bilingual format normalizer (project-agnostic, idempotent).

Prevents the recurring defect class where inserted JP runs inherit the source
English run's rPr via deepcopy, producing inconsistent fonts (宋体/メiryo/Calibri),
random bold, and catastrophic sizes (e.g. w:sz val=220 = 110pt). Run AFTER every
bilingual insertion pass, on the final docx. Re-running is safe.

Rules applied to every run whose text contains CJK:
  * Font     -> project body font (default "Meiryo UI").
  * Heading  -> a paragraph carrying the bilingual " / " separator. The mixed
                EN+JP run is split so the JP portion gets the body font while
                the EN portion keeps its original face. Heading bold/size kept.
  * Body     -> translation text (run has hiragana, or CJK dominates the run,
                or sits in a JP-dominant paragraph). Forced NON-bold; size set
                to body half-points (default 18 = 9pt) when missing or absurd
                (> 36 half-points).
  * Mixed EN+CJK run inside an English paragraph (e.g. 'Start「非常起動」button'):
                only the CJK (eastAsia/cs) face is normalized; Latin face, bold
                and size are left untouched so the surrounding English is not
                disturbed.

Usage:
  python normalize_format.py FILE.docx [MORE.docx] [--font "Meiryo UI"] [--body-size 18]
"""
import argparse, re, shutil, zipfile
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def qn(t): return f'{{{W}}}{t}'
W_ = '{' + W + '}'
XMLSPACE = '{http://www.w3.org/XML/1998/namespace}space'

CJK_RE = re.compile(r'[\u3000-\u9fff\uff00-\uffef]')
HIRA_RE = re.compile(r'[\u3040-\u309f]')


def has_cjk(s): return bool(s and CJK_RE.search(s))
def has_hira(s): return bool(s and HIRA_RE.search(s))
def cjk_count(s): return sum(1 for c in s if '\u3000' <= c <= '\u9fff' or '\uff00' <= c <= '\uffef')
def lat_count(s): return sum(1 for c in s if 'A' <= c <= 'Z' or 'a' <= c <= 'z')


def get_rpr(r):
    rpr = r.find(qn('rPr'))
    if rpr is None:
        rpr = etree.SubElement(r, qn('rPr'))
        r.insert(0, rpr)
    return rpr


def set_font(rpr, font, east_only=False):
    rf = rpr.find(qn('rFonts'))
    if rf is None:
        rf = etree.SubElement(rpr, qn('rFonts'))
    attrs = ('eastAsia', 'cs') if east_only else ('ascii', 'hAnsi', 'eastAsia', 'cs')
    for a in attrs:
        rf.set(qn(a), font)


def is_bold(r):
    rpr = r.find(qn('rPr'))
    if rpr is None:
        return False
    b = rpr.find(qn('b'))
    if b is None:
        return False
    return b.get(qn('val'), '1') != '0'


def set_bold(rpr, bold):
    for tag in ('b', 'bCs'):
        el = rpr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rpr, qn(tag))
        el.set(qn('val'), '1' if bold else '0')


def get_size(rpr):
    sz = rpr.find(qn('sz'))
    if sz is None:
        return None
    try:
        return int(sz.get(qn('val')))
    except Exception:
        return None


def set_size(rpr, val):
    for tag in ('sz', 'szCs'):
        el = rpr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rpr, qn(tag))
        el.set(qn('val'), str(val))


def run_text(r):
    return ''.join((t.text or '') for t in r.findall(qn('t')))


def split_mixed_heading(r, font):
    """Split a 'EN... / JP...' run into EN run (original face) + JP run (body font).
    Returns True if split happened."""
    ts = r.findall(qn('t'))
    if len(ts) != 1 or not has_cjk(ts[0].text or ''):
        return False
    text = ts[0].text or ''
    m = re.search(r'^(.*[A-Za-z0-9].*?)\s*/\s*(.*[\u3000-\u9fff].*)$', text)
    if not m:
        return False
    en_part, jp_part = m.group(1).rstrip() + ' / ', m.group(2)
    ts[0].text = en_part
    ts[0].set(XMLSPACE, 'preserve')
    jp = etree.Element(qn('r'))
    src_rpr = r.find(qn('rPr'))
    jp_rpr = etree.SubElement(jp, qn('rPr'))
    if src_rpr is not None:
        for child in src_rpr:
            jp_rpr.append(etree.fromstring(etree.tostring(child)))
    set_font(jp_rpr, font)
    jt = etree.SubElement(jp, qn('t'))
    jt.set(XMLSPACE, 'preserve')
    jt.text = jp_part
    r.addnext(jp)
    return True


def normalize(path, font, body_size):
    with zipfile.ZipFile(path) as z:
        xml = z.read('word/document.xml')
    root = etree.fromstring(xml)
    body = root.find(f'.//{W_}body')
    stats = dict(font=0, bold_off=0, size_fix=0, split=0)

    for p in body.findall(f'.//{W_}p'):
        full = ''.join(run_text(r) for r in p.findall(qn('r')))
        is_heading = ' / ' in full
        p_jp_dominant = cjk_count(full) > lat_count(full)
        if is_heading:
            for r in list(p.findall(qn('r'))):
                if split_mixed_heading(r, font):
                    stats['split'] += 1
        for r in p.findall(qn('r')):
            t = run_text(r)
            if not has_cjk(t):
                continue
            genuine = is_heading or has_hira(t) or cjk_count(t) > lat_count(t)
            rpr = get_rpr(r)
            set_font(rpr, font, east_only=(not genuine))
            if not genuine:
                continue
            stats['font'] += 1
            if is_heading:
                continue
            if has_hira(t) or p_jp_dominant:
                if is_bold(r):
                    set_bold(rpr, False)
                    stats['bold_off'] += 1
                if get_size(rpr) is None or (get_size(rpr) or 0) > 36:
                    set_size(rpr, body_size)
                    stats['size_fix'] += 1

    for pPr in body.findall(f'.//{W_}pPr'):
        rpr = pPr.find(qn('rPr'))
        if rpr is not None:
            rf = rpr.find(qn('rFonts'))
            if rf is not None and rf.get(qn('eastAsia')) and rf.get(qn('eastAsia')) != font:
                for a in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
                    if rf.get(qn(a)):
                        rf.set(qn(a), font)

    out = etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
    tmp = path + '.tmp'
    with zipfile.ZipFile(path, 'r') as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            zout.writestr(item, out if item.filename == 'word/document.xml' else zin.read(item.filename))
    shutil.move(tmp, path)
    print(f"  {path.split(chr(92))[-1] if chr(92) in path else path.split('/')[-1]}: "
          f"font={stats['font']} bold_off={stats['bold_off']} size_fix={stats['size_fix']} split={stats['split']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('files', nargs='+')
    ap.add_argument('--font', default='Meiryo UI', help='body CJK font (default "Meiryo UI"; KIX1 may differ)')
    ap.add_argument('--body-size', type=int, default=18, help='body size in half-points (default 18 = 9pt)')
    a = ap.parse_args()
    for f in a.files:
        normalize(f, a.font, a.body_size)


if __name__ == '__main__':
    main()
