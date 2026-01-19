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
        for attempt in range(self.max_retries):
            response = requests.get(
                url, params=params, headers=self._headers(), timeout=5
            )

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                time.sleep(retry_after)
                continue

            return response

        raise RuntimeError(f"Rate limit exceeded for {endpoint}")

    # ---------- API METHODS ----------

    def _safe_json_response(self, response):
        """Safely parse JSON response, handling errors gracefully."""
        try:
            return response.json()
        except ValueError:
            # If response is not JSON, return error dict
            return {"error": "Invalid JSON response", "valid": False}

    def validate_gstin(self, gstin):
        try:
            resp = self._post("validate-gstin", {"gstin": gstin})
            return resp.status_code, self._safe_json_response(resp)
        except requests.exceptions.RequestException as e:
            return 500, {"error": str(e), "valid": False}

    def validate_irn(self, irn):
        try:
            resp = self._post("validate-irn", {"irn": irn})
            return resp.status_code, self._safe_json_response(resp)
        except requests.exceptions.RequestException as e:
            return 500, {"error": str(e), "valid": False}

    def get_hsn_rate(self, hsn_code, invoice_date):
        try:
            resp = self._get(
                "hsn-rate", {"code": hsn_code, "date": invoice_date}
            )
            return resp.status_code, self._safe_json_response(resp)
        except requests.exceptions.RequestException as e:
            return 500, {"error": str(e), "rate": {}}

    def check_einvoice_required(self, seller_gstin, invoice_date, invoice_value):
        try:
            resp = self._post(
                "e-invoice-required",
                {
                    "seller_gstin": seller_gstin,
                    "invoice_date": invoice_date,
                    "invoice_value": invoice_value,
                },
            )
            return resp.status_code, self._safe_json_response(resp)
        except requests.exceptions.RequestException as e:
            return 500, {"error": str(e), "required": False}

    def verify_206ab(self, pan):
        try:
            resp = self._post("verify-206ab", {"pan": pan})
            return resp.status_code, self._safe_json_response(resp)
        except requests.exceptions.RequestException as e:
            return 500, {"error": str(e), "section_206ab_applicable": False}
