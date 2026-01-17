def infer_missing_fields(invoice, vendor_registry):
    """
    Attempts safe inference of missing invoice fields.
    Must NEVER mutate schema incorrectly.
    """

    if not isinstance(invoice, dict):
        raise TypeError("infer_missing_fields expects dict")

    invoice.setdefault("metadata", {})

    # Infer seller GSTIN by vendor name (best-effort)
    if not invoice.get("seller_gstin"):
        raw_text = invoice.get("metadata", {}).get("raw_text", "")
        for vendor in vendor_registry.get("vendors", []):
            if vendor.get("name") and vendor["name"] in raw_text:
                invoice["seller_gstin"] = vendor.get("gstin")
                break

    return invoice
