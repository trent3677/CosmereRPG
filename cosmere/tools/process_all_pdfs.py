#!/usr/bin/env python3
"""
Process all Cosmere RPG PDFs under cosmere/pdfs and generate structured
JSON outputs under cosmere/data/rules. Also builds a master_index.json for
fast lookups and a combined quick reference.

Usage:
  python cosmere/tools/process_all_pdfs.py
  python cosmere/tools/process_all_pdfs.py --pdf-dir cosmere/pdfs --output-dir cosmere/data/rules
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Ensure repo root is on sys.path so `cosmere` package resolves when executed directly
CURRENT_FILE = Path(__file__).resolve()
REPO_ROOT = CURRENT_FILE.parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Local imports
from cosmere.tools.pdf_processor import CosmereRPGPDFProcessor


logger = logging.getLogger("process_all_pdfs")


def find_pdf_files(pdf_dir: Path) -> List[Path]:
    """Return a list of PDF files in the given directory (non-recursive)."""
    if not pdf_dir.exists():
        return []
    pdfs: List[Path] = []
    for pattern in ("*.pdf", "*.PDF"):
        pdfs.extend(sorted(pdf_dir.glob(pattern)))
    return pdfs


def build_master_index(rules_output_dir: Path) -> Dict:
    """Aggregate quick references and glossaries into a master index."""
    master: Dict = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "sources": [],
        "glossary": {},
        "quick_reference": {
            "stats": {},
            "mechanics": {},
            "investiture": {},
            "tables": [],
        },
    }

    # Aggregate quick refs
    for quick_ref_file in rules_output_dir.glob("*_quick_ref.json"):
        try:
            with open(quick_ref_file, "r", encoding="utf-8") as f:
                qref = json.load(f)
            master["sources"].append(quick_ref_file.stem.replace("_quick_ref", ""))
            # Merge stats
            for stat_name, entries in qref.get("stats", {}).items():
                master["quick_reference"]["stats"].setdefault(stat_name, []).extend(entries)
            # Merge mechanics
            for mech_name, entries in qref.get("mechanics", {}).items():
                master["quick_reference"]["mechanics"].setdefault(mech_name, []).extend(entries)
            # Merge investiture
            for inv_type, entries in qref.get("investiture", {}).items():
                master["quick_reference"]["investiture"].setdefault(inv_type, []).extend(entries)
            # Append tables
            master["quick_reference"]["tables"].extend(qref.get("tables", []))
        except Exception as e:
            logger.warning("Failed reading quick ref %s: %s", quick_ref_file, e)

    # Aggregate glossaries by scanning content files
    for content_file in rules_output_dir.glob("*_content.json"):
        try:
            with open(content_file, "r", encoding="utf-8") as f:
                content = json.load(f)
            glossary = content.get("content", {}).get("glossary", {})
            for term, definition in glossary.items():
                # Keep first definition if duplicates; could be improved to merge
                master["glossary"].setdefault(term, definition)
        except Exception as e:
            logger.warning("Failed reading content %s: %s", content_file, e)

    return master


def main() -> int:
    parser = argparse.ArgumentParser(description="Process all Cosmere RPG PDFs")
    parser.add_argument("--pdf-dir", default="cosmere/pdfs", help="Directory containing PDF files")
    parser.add_argument("--output-dir", default="cosmere/data/rules", help="Output directory for JSON files")
    parser.add_argument("--extract-images", action="store_true", help="Extract embedded images (slower)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    pdf_dir = Path(args.pdf_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_files = find_pdf_files(pdf_dir)
    if not pdf_files:
        logger.info("No PDFs found in %s", pdf_dir)
        return 1

    logger.info("Found %d PDF(s) to process", len(pdf_files))
    processor = CosmereRPGPDFProcessor(output_dir=str(output_dir))

    processed = 0
    for pdf_path in pdf_files:
        try:
            logger.info("Processing: %s", pdf_path.name)
            processor.process_pdf(str(pdf_path), extract_images=args.extract_images)
            processed += 1
        except Exception as e:
            logger.error("Error processing %s: %s", pdf_path, e)

    if processed == 0:
        logger.error("No PDFs processed successfully")
        return 2

    # Build master index
    master_index = build_master_index(output_dir)
    master_path = output_dir / "master_index.json"
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(master_index, f, indent=2, ensure_ascii=False)
    logger.info("Wrote master index: %s", master_path)

    logger.info("Completed processing %d/%d PDFs", processed, len(pdf_files))
    return 0


if __name__ == "__main__":
    sys.exit(main())


