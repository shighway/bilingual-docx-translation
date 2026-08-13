#!/usr/bin/env python3
"""Compare target-equipment selection lists in a source and bilingual DOCX."""

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from zipfile import ZipFile, BadZipFile

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
JP_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")
SPACE_RE = re.compile(r"\s+")


def normalize(value: str) -> str:
    return SPACE_RE.sub(" ", value).strip()


def paragraph_text(paragraph) -> str:
    return normalize("".join(paragraph.xpath(".//w:t/text()", namespaces=NS)))


def target_list(path: Path):
    with ZipFile(path) as package:
        root = etree.fromstring(package.read("word/document.xml"))
    candidates = []
    for cell in root.xpath(".//w:tc", namespaces=NS):
        value = normalize("".join(cell.xpath(".//w:t/text()", namespaces=NS)))
        if "target equipment / system" in value.casefold() and "designation" in value.casefold():
            candidates.append(cell)
    if not candidates:
        return None
    # Merged cells may expose repeated logical text. The smallest matching cell is the local list cell.
    cell = min(candidates, key=lambda node: len(node.xpath(".//w:tc", namespaces=NS)))
    paragraphs = cell.xpath(".//w:p", namespaces=NS)
    instruction_index = next(
        (i for i, p in enumerate(paragraphs) if "designation" in paragraph_text(p).casefold()),
        None,
    )
    if instruction_index is None:
        return None
    instruction = paragraph_text(paragraphs[instruction_index])
    entries = [paragraph_text(p) for p in paragraphs[instruction_index + 1 :]]
    return {"instruction": instruction, "entries": [x for x in entries if x]}


def compare(source: Path, bilingual: Path) -> dict:
    report = {"source": str(source.resolve()), "bilingual": str(bilingual.resolve())}
    try:
        src = target_list(source)
        out = target_list(bilingual)
    except (BadZipFile, KeyError, etree.XMLSyntaxError) as exc:
        report.update(ok=False, error=str(exc))
        return report
    report["source_has_target_list"] = src is not None
    report["bilingual_has_target_list"] = out is not None
    if src is None:
        report.update(ok=True, status="not-applicable")
        return report
    if out is None:
        report.update(ok=False, status="missing-target-list")
        return report
    source_counts = Counter(src["entries"])
    output_counts = Counter(out["entries"])
    missing = list((source_counts - output_counts).elements())
    # Ignore added Japanese translations; flag extra non-Japanese entries as possible inherited equipment.
    unexpected = []
    for value, count in (output_counts - source_counts).items():
        if not JP_RE.search(value):
            unexpected.extend([value] * count)
    report.update(
        ok=not missing and not unexpected,
        status="match" if not missing and not unexpected else "mismatch",
        source_items=len(src["entries"]),
        bilingual_items=len(out["entries"]),
        missing=missing,
        unexpected_non_japanese=unexpected,
    )
    return report


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("bilingual", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = compare(args.source, args.bilingual)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"source: {report['source']}")
        print(f"bilingual: {report['bilingual']}")
        for key, value in report.items():
            if key not in {"source", "bilingual"}:
                print(f"{key}: {value}")
    raise SystemExit(0 if report.get("ok") else 1)


if __name__ == "__main__":
    main()
