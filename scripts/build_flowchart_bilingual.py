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
  text_y2   = bottom Y of the English text (vertical anchor: JP top = y2+4px)
  jp        = Japanese translation ('\n' allowed)

Positioning rules (SOP-501/903 lessons):
  - Horizontal: center on the actual colored box, clip pill to box bounds.
    NEVER center on the OCR text bbox — it is narrower than the box and the
    pill overflows the box edges.
  - Vertical: anchor to the OCR English text bottom, NOT the box bottom.
    Box bottom is ~30px below the text and pushes JP far from EN.
  - Box/color detection: use a NON-WHITE mask
      ~((r>230) & (g>230) & (b>230))
    NOT (channel > 200). Saturated colors (purple 111,47,161 / blue 47,85,151
    / green 84,130,53) have ALL channels < 200 and are missed otherwise.

Dependencies: pip install pillow numpy easyocr  (easyocr only for --ocr)
"""
import argparse
import json
import os
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

    line_height = font_size + 2
    pad = 4
    max_y = h
    for lab in labels:
        n_lines = lab['jp'].count('\n') + 1
        max_y = max(max_y, lab['text_y2'] + pad + n_lines * line_height + pad)
    extra = max(max_y - h + 5, 0)
    new_img = Image.new('RGBA', (w, h + extra), (255, 255, 255, 255))
    new_img.paste(img, (0, 0))
    draw = ImageDraw.Draw(new_img)

    for lab in labels:
        bx1, by1, bx2, by2 = lab['box']
        text_y2, jp = lab['text_y2'], lab['jp']
        if not jp:
            continue
        box_w = bx2 - bx1
        cx = (bx1 + bx2) // 2
        bg = get_box_color_at(orig_rgb, cx, by1 + 5)

        font = get_font(font_size)
        tw = font.getbbox(jp)[2]
        for size in (font_size - 1, font_size - 2):  # auto-shrink to fit box
            if tw > box_w - 12:
                font = get_font(size)
                tw = font.getbbox(jp)[2]

        tx = max(cx - tw // 2, bx1 + 4)               # center on box, clip
        if tx + tw > bx2 - 4:
            tx = bx2 - 4 - tw
        ty = text_y2 + pad                             # anchor: EN text bottom

        px0 = max(tx - 3, bx1 + 2)
        px1 = min(tx + tw + 3, bx2 - 2)
        if px1 > px0:
            draw.rectangle([px0, ty - 2, px1, ty + font_size + 1],
                           fill=bg + (255,))
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):  # black outline
            draw.text((tx + dx, ty + dy), jp, fill=(0, 0, 0, 255), font=font)
        draw.text((tx, ty), jp, fill=(255, 255, 255, 255), font=font)

    new_img.convert('RGB').save(out_path, 'PNG', optimize=True)
    print(f'{out_path} ({os.path.getsize(out_path):,} bytes) {w}x{h + extra}')
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
    args = ap.parse_args()

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
