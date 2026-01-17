import os
import time
import json
from pathlib import Path

from utils.parsers.pdf_parser import PDFParser
from utils.parsers.image_parser import ImageParser
from utils.parsers.json_parser import JSONParser
from utils.parsers.csv_parser import CSVParser
from utils.ocr_utils import clean_ocr_text
from utils.normalization_utils import normalize_invoice
from utils.inference_utils import infer_missing_fields


class ExtractorAgent:
    """
    Extractor Agent
    ----------------
    - Parses invoices from PDF, image, JSON, CSV
    - Cleans OCR noise
    - Normalizes schema
    - Infers missing fields
    - ALWAYS returns a minimum viable invoice context
    """

    def __init__(self, config):
        self.invoices_dir = Path(config["invoices_dir"])
        self.vendor_registry_path = config["vendor_registry_path"]

        with open(self.vendor_registry_path, "r", encoding="utf-8") as f:
            self.vendor_registry = json.load(f)

        self.parsers = {
            ".pdf": PDFParser(),
            ".png": ImageParser(),
            ".jpg": ImageParser(),
            ".jpeg": ImageParser(),
            ".json": JSONParser(),
            ".csv": CSVParser(),
        }

    def load_invoices(self):
        return [
            p for p in self.invoices_dir.iterdir()
            if p.is_file() and p.suffix.lower() in self.parsers
        ]

    def extract(self, invoice_path):
        start_time = time.time()
        ext = invoice_path.suffix.lower()

        if ext not in self.parsers:
            raise ValueError(f"Unsupported invoice format: {ext}")

        # ---------- Parse ----------
        raw_data = self.parsers[ext].parse(invoice_path)

        if not isinstance(raw_data, dict):
            raise ValueError("Parser must return a dictionary")

        # ---------- OCR Cleanup ----------
        if "raw_text" in raw_data and isinstance(raw_data["raw_text"], str):
            raw_data["raw_text"] = clean_ocr_text(raw_data["raw_text"])

        # ---------- Normalize ----------
        normalized = normalize_invoice(raw_data)

        if not isinstance(normalized, dict):
            raise ValueError("normalize_invoice must return a dict")

        # ---------- Enrich / Infer ----------
        enriched = infer_missing_fields(
            normalized,
            vendor_registry=self.vendor_registry
        )

        # ---------- HARD SAFETY DEFAULTS ----------
        enriched.setdefault("invoice_id", invoice_path.stem)
        enriched.setdefault("invoice_date", "1970-01-01")
        enriched.setdefault("total_amount", 0)
        enriched.setdefault("seller_gstin", "")
        enriched.setdefault("buyer_gstin", "")
        enriched.setdefault("vendor_pan", "")
        enriched.setdefault("line_items", [])

        if not isinstance(enriched["line_items"], list):
            enriched["line_items"] = []

        # ---------- Metadata ----------
        enriched.setdefault("metadata", {})
        enriched["metadata"].update({
            "source_file": invoice_path.name,
            "file_type": ext,
            "processing_time_sec": round(time.time() - start_time, 3)
        })

        return enriched
