def normalize_invoice(raw):
    """
    Converts raw parsed invoice data into canonical invoice_ctx.
    This function MUST never crash.
    """

    if not isinstance(raw, dict):
        raise TypeError("normalize_invoice expects dict")

    fields = raw.get("fields")

    # HARDEN against broken parsers
    if not isinstance(fields, dict):
        fields = {}

    invoice = {
        "invoice_id": fields.get("invoice_number") or fields.get("invoice_id"),
        "invoice_date": fields.get("invoice_date"),
        "seller_gstin": fields.get("seller_gstin"),
        "buyer_gstin": fields.get("buyer_gstin"),
        "vendor_pan": fields.get("vendor_pan"),
        "invoice_value": float(fields.get("invoice_value", 0) or 0),
        "line_items": raw.get("line_items") or [],
        "metadata": {}
    }

    return invoice
