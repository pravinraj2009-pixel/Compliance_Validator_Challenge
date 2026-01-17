# src/tools/gst_portal_client.py
import time
import requests


class GSTPortalClient:
    """
    Client for interacting with mock GST portal API.
    Handles retries, rate limiting, and error normalization.
    """

    def __init__(self, base_url, api_key, max_retries=3):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.max_retries = max_retries

    def _headers(self):
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _post(self, endpoint, payload):
        url = f"{self.base_url}/{endpoint}"
        for attempt in range(self.max_retries):
            response = requests.post(
                url, json=payload, headers=self._headers(), timeout=5
            )

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                time.sleep(retry_after)
                continue

            return response

        raise RuntimeError(f"Rate limit exceeded for {endpoint}")

    def _get(self, endpoint, params):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(
            url, params=params, headers=self._headers(), timeout=5
        )
        return response

    # ---------- API METHODS ----------

    def validate_gstin(self, gstin):
        resp = self._post("validate-gstin", {"gstin": gstin})
        return resp.status_code, resp.json()

    def validate_irn(self, irn):
        resp = self._post("validate-irn", {"irn": irn})
        return resp.status_code, resp.json()

    def get_hsn_rate(self, hsn_code, invoice_date):
        resp = self._get(
            "hsn-rate", {"code": hsn_code, "date": invoice_date}
        )
        return resp.status_code, resp.json()

    def check_einvoice_required(self, seller_gstin, invoice_date, invoice_value):
        resp = self._post(
            "e-invoice-required",
            {
                "seller_gstin": seller_gstin,
                "invoice_date": invoice_date,
                "invoice_value": invoice_value,
            },
        )
        return resp.status_code, resp.json()

    def verify_206ab(self, pan):
        resp = self._post("verify-206ab", {"pan": pan})
        return resp.status_code, resp.json()
