def infer_missing_fields(invoice, vendor_registry):
    """
    Safely infer missing invoice attributes using vendor registry.
    This function MUST NOT mutate invoice structure.
    """

    if not isinstance(invoice, dict):
        raise TypeError("infer_missing_fields expects invoice dict")

    if not isinstance(vendor_registry, dict):
        raise TypeError("vendor_registry must be dict")

    # ---------------------------------------------------------
    # Ensure fields dict exists
    # ---------------------------------------------------------
    fields = invoice.get("fields")
    if not isinstance(fields, dict):
        raise TypeError("invoice['fields'] must be dict during inference")

    # ---------------------------------------------------------
    # Infer seller GSTIN from vendor registry
    # ---------------------------------------------------------
    if not invoice.get("seller_gstin"):
        vendor_name = fields.get("vendor_name")

        if vendor_name:
            for vendor in vendor_registry.get("vendors", []):
                if vendor.get("name") == vendor_name:
                    invoice["seller_gstin"] = vendor.get("gstin")
                    break

    # ---------------------------------------------------------
    # Infer vendor PAN from GSTIN
    # ---------------------------------------------------------
    if invoice.get("seller_gstin") and not fields.get("vendor_pan"):
        gstin = invoice["seller_gstin"]
        if isinstance(gstin, str) and len(gstin) >= 12:
            fields["vendor_pan"] = gstin[2:12]

    # ---------------------------------------------------------
    # Infer invoice value from line items
    # ---------------------------------------------------------
    if not invoice.get("invoice_value"):
        total = 0.0
        for item in invoice.get("line_items", []):
            amount = item.get("amount")
            try:
                total += float(amount)
            except (TypeError, ValueError):
                pass

        invoice["invoice_value"] = round(total, 2)

    # ---------------------------------------------------------
    # DO NOT TOUCH STRUCTURE BELOW
    # ---------------------------------------------------------
    return invoice
