#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Raster flowchart bilingual builder (easyocr + Pillow overlay). Verified on
KSW SOP-501/SOP-903.

Method: keep the original raster image and OVERLAY Japanese text directly
below each English label. Preserves every visual element (boxes, colors,
connectors, arrows, grouping) with zero drift. Full redraw is a last resort
only (color/layout drift risk).

Two-step workflow:

  1. OCR assist — dump detected colored boxes + English text bboxes as JSON:
       python build_flowchart_bilingual.py --ocr SRC.png --dump dump.json
     Then edit dump.json: for each label keep box/text_y2 and add "jp".

  2. Overlay + optional DOCX swap:
       python build_flowchart_bilingual.py --src SRC.png --labels dump.json \
            [--out OUT.png] [--docx BILINGUAL.docx --media image2.png]

Label JSON format (list):
  [{"box": [x1, y1, x2, y2], "text_y2": 69, "jp": "地震信号受信"}, ...]

  box       = FULL colored-box rectangle (horizontal centering / pill clipping)
  text_y2   = bottom Y of the English text (vertical anchor: JP top = y2+3px)
  jp        = Japanese translation
  dark      = optional true: plain black text at {cx, y}, no pill
              (for white-bg labels like decision diamonds)

Positioning rules (SOP-310/501/903 lessons):
  - Horizontal: center on the actual colored box, clip pill to box bounds.
    NEVER center on the OCR text bbox — it is narrower than the box and the
    pill overflows the box edges.
  - Vertical: anchor to the OCR English text bottom, NOT the box bottom.
    Box bottom is ~30px below the text and pushes JP far from EN.
  - Box/color detection: use a NON-WHITE mask
      ~((r>230) & (g>230) & (b>230))
    NOT (channel > 200). Saturated colors (purple 111,47,161 / blue 47,85,151
    / green 84,130,53) have ALL channels < 200 and are missed otherwise.
  - NO black 4-direction text outline. At 10-11px Meiryo the outline makes
    every glyph look bold/stenciled (SOP-310 v2 lesson). White text directly.
  - NO canvas extension. If the pill would pass the box bottom, extend the
    box fill color seamlessly down (full box width) to the pill bottom
    instead. Canvas extension changes the aspect ratio vs the source.
  - Dark labels: white-bg areas (decision diamonds) get plain BLACK text,
    no pill — add {"cx": x, "y": y, "jp": "...", "dark": true}.
  - Font fit: one-step shrink (11->10px) then ASSERT. Never shrink silently
    below that — an overflowing 9px label must fail loudly.
  - Extent: if a previous full redraw swapped in a different pixel size,
    document.xml wp:extent no longer matches the source display size
    (SOP-310: image shown at 14.6in instead of 4.53in x 5.51in). After
    media swap, verify/restore the extent (see --fix-extent).

Dependencies: pip install pillow numpy easyocr  (easyocr only for --ocr)
"""
import argparse
import json
import os
import re
import shutil
import sys
import zipfile

import numpy as np
from PIL import Image, ImageDraw, ImageFont

MEIRYO = r'C:\Windows\Fonts\meiryo.ttc'
MSGOTHIC = r'C:\Windows\Fonts\msgothic.ttc'


def get_font(size):
    for path in (MEIRYO, MSGOTHIC):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    raise RuntimeError('No JP font found (meiryo.ttc / msgothic.ttc)')


def nonwhite_mask(arr):
    """Correct box-detection mask. Channel>200 tests MISS saturated colors."""
    return ~((arr[:, :, 0] > 230) & (arr[:, :, 1] > 230) & (arr[:, :, 2] > 230))


def find_boxes(arr, min_area=400):
    """Connected components on the non-white mask -> colored box rectangles."""
    mask = nonwhite_mask(arr)
    h, w = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    boxes = []
    for y in range(h):
        for x in range(w):
            if not mask[y, x] or visited[y, x]:
                continue
            stack = [(y, x)]
            visited[y, x] = True
            x1 = y1 = 10 ** 9
            x2 = y2 = -1
            while stack:
                cy, cx = stack.pop()
                x1, x2 = min(x1, cx), max(x2, cx)
                y1, y2 = min(y1, cy), max(y2, cy)
                for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                    if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                        visited[ny, nx] = True
                        stack.append((ny, nx))
            if (x2 - x1) * (y2 - y1) >= min_area:
                boxes.append((x1, y1, x2, y2))
    return sorted(boxes, key=lambda b: (b[1], b[0]))


def get_box_color_at(arr, cx, cy, radius=8, default=(111, 47, 161)):
    """Dominant non-white/non-dark pixel near (cx, cy) -> pill bg color."""
    h, w = arr.shape[:2]
    region = arr[max(0, cy - radius):min(h, cy + radius + 1),
                 max(0, cx - radius):min(w, cx + radius + 1)]
    if region.size == 0:
        return default
    mask = nonwhite_mask(region) & ~(
        (region[:, :, 0] < 60) & (region[:, :, 1] < 60) & (region[:, :, 2] < 60))
    if mask.any():
        pixels = region[mask]
        unique, counts = np.unique(pixels.reshape(-1, 3), axis=0, return_counts=True)
        return tuple(int(v) for v in unique[np.argmax(counts)])
    return default


def ocr_dump(src_path, dump_path):
    """easyocr the English labels, pair them with detected boxes, write JSON."""
    import easyocr  # deferred: heavy import
    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext(src_path)
    arr = np.array(Image.open(src_path).convert('RGB'))
    boxes = find_boxes(arr)

    def containing_box(cx, cy):
        best = None
        for b in boxes:
            if b[0] <= cx <= b[2] and b[1] <= cy <= b[3]:
                if best is None or (b[2] - b[0]) * (b[3] - b[1]) < \
                        (best[2] - best[0]) * (best[3] - best[1]):
                    best = b
        return best

    labels = []
    for bbox, text, prob in results:
        xs = [p[0] for p in bbox]
        ys = [p[1] for p in bbox]
        text_y2 = int(max(ys))
        cx, cy = int(np.mean(xs)), int(np.mean(ys))
        box = containing_box(cx, cy)
        labels.append({
            'box': list(box) if box else [int(min(xs)), int(min(ys)),
                                           int(max(xs)), int(max(ys))],
            'text': text,
            'text_y2': text_y2,
            'jp': '',  # fill in
        })
    with open(dump_path, 'w', encoding='utf-8') as f:
        json.dump(labels, f, ensure_ascii=False, indent=2)
    print(f'{len(labels)} labels -> {dump_path} (fill "jp", drop non-label rows)')
    for lab in labels:
        print(f"  y2={lab['text_y2']:4d} box={lab['box']} {lab['text']!r}")


def overlay(src_path, labels, out_path, font_size=11):
    img = Image.open(src_path).convert('RGBA')
    w, h = img.size
    orig_rgb = np.array(img.convert('RGB'))
    draw = ImageDraw.Draw(img)

    for lab in labels:
        jp = lab.get('jp', '')
        if not jp:
            continue
        f = get_font(font_size)

        if lab.get('dark'):  # plain black text on white bg (no pill)
            cx, ty = lab['cx'], lab['y']
            tw = f.getbbox(jp)[2]
            draw.text((cx - tw // 2, ty), jp, fill=(0, 0, 0, 255), font=f)
            continue

        bx1, by1, bx2, by2 = lab['box']
        text_y2 = lab['text_y2']
        box_w = bx2 - bx1
        cx = (bx1 + bx2) // 2
        bg = get_box_color_at(orig_rgb, cx, by1 + 5)

        tw = f.getbbox(jp)[2]
        if tw > box_w - 10:  # ONE shrink step, then fail loudly
            f = get_font(font_size - 1)
            tw = f.getbbox(jp)[2]
        assert tw <= box_w - 10, f'JP too wide {tw}>{box_w - 10}: {jp}'

        tx = max(cx - tw // 2, bx1 + 5)
        if tx + tw > bx2 - 5:
            tx = bx2 - 5 - tw
        ty = text_y2 + 3

        py0, py1 = ty - 2, ty + font_size + 1
        if py1 > by2 - 1:  # seamless box extension, NOT canvas extension
            draw.rectangle([bx1, by2 - 1, bx2, py1 + 1], fill=bg + (255,))
        draw.rectangle([max(tx - 4, bx1 + 2), py0,
                        min(tx + tw + 4, bx2 - 2), py1], fill=bg + (255,))
        draw.text((tx, ty), jp, fill=(255, 255, 255, 255), font=f)

    img.convert('RGB').save(out_path, 'PNG', optimize=True)
    print(f'{out_path} ({os.path.getsize(out_path):,} bytes) {w}x{h} (no canvas change)')
    return out_path


def replace_image_in_docx(docx_path, image_path, media_name):
    """Swap word/media/<media_name> in place. Keeps filename/rels untouched."""
    target = f'word/media/{media_name}'
    tmp = docx_path + '.tmp'
    shutil.copy2(docx_path, tmp)
    with zipfile.ZipFile(tmp, 'r') as zin, \
            zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        hit = False
        for item in zin.namelist():
            if item == target or item.endswith('/' + media_name):
                data = open(image_path, 'rb').read()
                zout.writestr(item, data)
                hit = True
                print(f'  replaced {item} ({len(data):,} bytes)')
            else:
                zout.writestr(item, zin.read(item))
    os.remove(tmp)
    if not hit:
        print(f'  WARNING: {target} not found in {docx_path}', file=sys.stderr)


def restore_extent(docx_path, media_name, cx, cy):
    """Rewrite wp:extent of inline drawings embedding media_name (SOP-310
    lesson: a previous full-redraw swap left extent at raw-pixel 14.6in,
    blowing the layout up). Call with the SOURCE display size in EMU."""
    with zipfile.ZipFile(docx_path, 'r') as z:
        data = {n: z.read(n) for n in z.namelist()}
    rels = data['word/_rels/document.xml.rels'].decode('utf8')
    m = re.search(
        rf'Target="media/{re.escape(media_name)}"[^>]*Id="(rId\d+)"'
        rf'|Id="(rId\d+)"[^>]*Target="media/{re.escape(media_name)}"', rels)
    rid = m.group(1) or m.group(2)
    doc = data['word/document.xml'].decode('utf8')
    parts = re.split(r'(<w:drawing>.*?</w:drawing>)', doc, flags=re.S)
    n = 0
    for i, p in enumerate(parts):
        if p.startswith('<w:drawing>') and f'r:embed="{rid}"' in p:
            parts[i] = re.sub(r'(<wp:extent cx=")\d+(" cy=")\d+("/>)',
                              rf'\g<1>{cx}\g<2>{cy}\g<3>', p)
            n += 1
    assert n >= 1, f'no drawing embedding {media_name} found'
    data['word/document.xml'] = ''.join(parts).encode('utf8')
    tmp = docx_path + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, d in data.items():
            zout.writestr(name, d)
    os.replace(tmp, docx_path)
    print(f'  extent restored to {cx}x{cy} EMU in {n} drawing(s)')


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument('--ocr', metavar='SRC.png', help='dump boxes+EN labels JSON')
    ap.add_argument('--dump', default='flowchart_labels.json')
    ap.add_argument('--src', help='source raster image')
    ap.add_argument('--labels', help='labels JSON (box/text_y2/jp)')
    ap.add_argument('--out', help='output PNG (default: <src>_bilingual.png)')
    ap.add_argument('--docx', help='bilingual docx to swap image into')
    ap.add_argument('--media', help='word/media filename, e.g. image2.png')
    ap.add_argument('--font-size', type=int, default=11)
    ap.add_argument('--fix-extent', metavar='CXxCY_EMU',
                    help='restore wp:extent (EMU) of drawings embedding --media')
    args = ap.parse_args()

    if args.fix_extent:
        if not (args.docx and args.media):
            ap.error('--fix-extent requires --docx and --media')
        cx, cy = args.fix_extent.split('x')
        restore_extent(args.docx, args.media, cx, cy)
        return

    if args.ocr:
        ocr_dump(args.ocr, args.dump)
        return
    if not (args.src and args.labels):
        ap.error('--src and --labels required (or --ocr)')

    with open(args.labels, encoding='utf-8') as f:
        labels = json.load(f)
    out = args.out or os.path.splitext(args.src)[0] + '_bilingual.png'
    overlay(args.src, labels, out, args.font_size)
    if args.docx and args.media:
        replace_image_in_docx(args.docx, out, args.media)


if __name__ == '__main__':
    main()
