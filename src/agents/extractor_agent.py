import json
import time
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
    RESPONSIBILITIES:
    - Load invoice files ONLY from data/invoices/
    - Parse PDF / Image / CSV / JSON
    - Support MULTI-INVOICE JSON files
    - Normalize + enrich each invoice
    """

    def __init__(self, config):
        self.invoices_dir = Path(config["invoices_dir"])
        self.vendor_registry_path = Path(config["vendor_registry_path"])

        if not self.invoices_dir.exists():
            raise FileNotFoundError(
                f"Invoices directory not found: {self.invoices_dir}"
            )

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

    # ---------------------------------------------------------
    # Invoice discovery
    # ---------------------------------------------------------

    def load_invoices(self):
        """
        Returns ONLY invoice files.
        Never returns reference data.
        """
        return [
            p for p in self.invoices_dir.iterdir()
            if p.is_file() and p.suffix.lower() in self.parsers
        ]

    # ---------------------------------------------------------
    # Extraction
    # ---------------------------------------------------------

    def extract(self, invoice_path: Path):
        """
        Extracts one invoice file.

        RETURNS:
            List[invoice_ctx]
        """
        start_time = time.time()
        suffix = invoice_path.suffix.lower()

        if suffix not in self.parsers:
            raise ValueError(f"Unsupported invoice type: {suffix}")

        parser = self.parsers[suffix]
        raw = parser.parse(invoice_path)

        if not raw:
            raise ValueError("Empty extraction result")

        # -------------------------------------------------
        # Normalize raw parser output into list of invoices
        # -------------------------------------------------

        if suffix == ".json":
            # 🔴 FIX: unwrap parser envelope
            payload = raw.get("fields")
            invoices = self._handle_json(payload, invoice_path)
        else:
            invoices = [raw]

        extracted = []

        for idx, raw_invoice in enumerate(invoices):
            if not isinstance(raw_invoice, dict):
                raise TypeError(
                    f"Invoice #{idx} in {invoice_path.name} is not a dict"
                )

            # ---- OCR cleanup ----
            if "raw_text" in raw_invoice:
                raw_invoice["raw_text"] = clean_ocr_text(
                    raw_invoice.get("raw_text", "")
                )

            # ---- Normalize ----
            normalized = normalize_invoice(raw_invoice)

            if not isinstance(normalized, dict):
                raise TypeError("normalize_invoice must return dict")

            # ---- Enrich ----
            enriched = infer_missing_fields(
                normalized,
                vendor_registry=self.vendor_registry
            )

            enriched.setdefault("metadata", {})
            enriched["metadata"].update({
                "source_file": invoice_path.name,
                "invoice_index": idx,
                "file_type": suffix,
                "processing_time_sec": round(
                    time.time() - start_time, 3
                ),
            })

            extracted.append(enriched)

        return extracted

    # ---------------------------------------------------------
    # JSON handling (CRITICAL)
    # ---------------------------------------------------------

    def _handle_json(self, raw_json, invoice_path):
        """
        Supports:
        1️⃣ Single invoice JSON (dict)
        2️⃣ Multi-invoice JSON (list)
        3️⃣ Wrapper formats: {"invoices": [...]}
        """

        # Case 1: {"invoices": [...]}
        if isinstance(raw_json, dict) and "invoices" in raw_json:
            invoices = raw_json["invoices"]

        # Case 2: [ {...}, {...} ]
        elif isinstance(raw_json, list):
            invoices = raw_json

        # Case 3: single invoice dict
        elif isinstance(raw_json, dict):
            invoices = [raw_json]

        else:
            raise TypeError(
                f"Unsupported JSON structure in {invoice_path.name}"
            )

        if not invoices:
            raise ValueError(
                f"No invoices found in {invoice_path.name}"
            )

        return invoices
