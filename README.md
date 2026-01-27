# Agentic AI Compliance Validator

## Overview
This project implements an Agentic AI–driven Compliance Validator for Accounts Payable invoices, designed to intelligently validate invoices against Indian GST and TDS regulations with human-like judgment.

The system combines:
- Deterministic compliance rules (58-point framework)
- Multi-agent architecture
- Stateful validation using SQLite
- External regulatory tools (GST mock API)
- LLM-assisted reasoning (GROQ)
- Human-in-the-loop escalation

---

## System Architecture

Invoices → Extractor Agent → Validator Agents → Resolver Agent → Reporter Agent → UI / Reports

---

## Agents

### Extractor Agent
- Parses PDF, Image (OCR), CSV, JSON invoices
- Normalizes fields
- Infers missing values
- Handles messy data

### Validator Agents
- ValidatorAgent: Category A & C checks
- GSTTDSValidatorAgent: Category B & D checks using GST Mock API

### Resolver Agent
- Handles regulatory conflicts and ambiguity
- Applies confidence thresholds
- Uses LLM (GROQ) only when required
- Detects deviation from historical decisions

### Reporter Agent
- Generates actionable compliance reports
- Includes confidence, failed checks, reasons, recommendations
- Exports CSV / JSON / PDF

---

## Tools

- GST Portal Mock API (5 endpoints)
- MCP (Model Context Protocol) for tool abstraction
- SQLite for stateful validation
- GROQ for local LLM reasoning

---

## Logs

- Agent execution timing
- Tool calls
- Decision confidence
- LLM reasoning

---

## UI

- Batch summary
- Actionable compliance table
- Escalation filtering
- LLM reasoning display
- CSV / PDF download

---

Folders/Codebase:
1.Data - It has all data sets needed
2.DOcs - It has Challenge document, architecture document and Walkthrough Document
3.src - It has below code files/folders
        -Config file
        -Storage folder(SQLite)
        -Agents folder
        -mcp folder
        -orchestration folder with code file which act as a pipeline
        -Models folder
        -Tools folder
        -Validation_checks folder
4.UI - App.py which is start of the agentic AI application
5.Utils -  All the utility tools are added
6.ReadMe file

----

##Pictorial presentation of codebase:

Compliance_Validator_Challenge/
│
├── data/
│   ├── invoices/
│   ├── vendor_registry.json
│   ├── gst_rates_schedule.csv
│   ├── hsn_sac_codes.json
│   ├── tds_sections.json
│   ├── company_policy.yaml
│   ├── historical_decisions.jsonl
│   └── state.db
│
├── src/
│   ├── agents/
│   │   ├── extractor_agent.py
│   │   ├── validator_agent.py
│   │   ├── gst_tds_validator_agent.py
│   │   ├── resolver_agent.py
│   │   ├── reporter_agent.py
│   │   └── llm_resolver_agent.py
│   │
│   ├── orchestration/
│   │   └── compliance_pipeline.py
│   │
│   ├── models/
│   │   ├── validation_result.py
│   │   └── base_validation.py
│   │
│   ├── validation_checks/
│   │   ├── category_a.py
│   │   ├── category_b.py
│   │   ├── category_c.py
│   │   ├── category_d.py
│   │   └── category_e.py
│   │
│   ├── storage/
│   │   ├── invoice_store.py
│   │   └── decision_store.py
│   │
│   ├── tools/
│   │   └── gst_portal_client.py
│   │
│   ├── mcp/
│   │   ├── server.py
│   │   └── tools/
│   │       └── gst_api_tool.py
|   |       └── groq_api_tool.py
│   │
│   └── config.py
│
├── utils/
│   ├── parsers/
│   │   ├── base_parser.py
│   │   ├── pdf_parser.py
│   │   ├── image_parser.py
│   │   ├── json_parser.py
│   │   └── csv_parser.py
│   │
│   ├── ocr_utils.py
│   ├── normalization_utils.py
│   └── inference_utils.py
│
├── ui/
│   └── app.py
│
├── mock_gst_server.py
├── README.md
└── requirements.txt


---

## 🔧 Prerequisites
### System Requirements
- Python 3.9+
- Git
- Windows / macOS / Linux

### Python Dependencies
```bash
pip install -r requirements.txt
```

### OCR Engine (Required for Image/PDF Invoices)
Install Tesseract OCR:

- Windows: https://github.com/tesseract-ocr/tesseract
- Ubuntu: sudo apt install tesseract-ocr
- macOS: brew install tesseract
---


## Quick Start
### 1. Open zipped folder in curson/VS code
### 2. Open new terminal(Ctrl + `)
### 3. Create virtual environment using uv
```bash
uv venv
```
### 4. Activate
```bash
.\.venv\Scripts\activate
```
### 5. Verify Python & pip
```bash
python --version
pip --version
python -m pip install --upgrade pip ##If pip is not installed
```

### 6. Install Dependancies
```bash
uv pip install -r requirements.txt 
#If get an error run this: python -m pip install pandas gradio requests flask pyyaml pillow pytesseract python-docx reportlab

```
### 7. Start GST Mock Server
```bash
uv pip install flask
python mock_gst_server.py
```
API validation:
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8080/api/gst/validate-gstin" `
  -Method POST `
  -Headers @{
    "X-API-Key" = "test-api-key-12345"
    "Content-Type" = "application/json"
  } `
  -Body '{"gstin":"27AABCT1234F1ZP"}'

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8080/api/gst/validate-irn" `
  -Method POST `
  -Headers @{
    "X-API-Key" = "test-api-key-12345"
    "Content-Type" = "application/json"
  } `
  -Body '{"irn":"a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8"}'

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8080/api/gst/hsn-rate?code=995411&date=2024-10-01" `
  -Method GET `
  -Headers @{
    "X-API-Key" = "test-api-key-12345"
  }

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8080/api/gst/e-invoice-required" `
  -Method POST `
  -Headers @{
    "X-API-Key" = "test-api-key-12345"
    "Content-Type" = "application/json"
  } `
  -Body '{
    "seller_gstin": "27AABCT1234F1ZP",
    "invoice_date": "2024-10-01",
    "invoice_value": 590000
  }'

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8080/api/gst/verify-206ab" `
  -Method POST `
  -Headers @{
    "X-API-Key" = "test-api-key-12345"
    "Content-Type" = "application/json"
  } `
  -Body '{"pan":"AXXPK5566Q"}'

### 7. Install Groq dependancies


### 8. Treat the current folder as the import root.

```bash
$env:PYTHONPATH="."
```
### 9. Treat the current folder as the import root.

```bash
$env:PYTHONPATH="."
```
### 10. PDF dependencies
```bash
uv pip install pdfplumber
```
### 11. (OpenCV) installer
```bash
uv pip install opencv-python
uv pip install pytesseract opencv-python
uv pip install reportlab
```


### 12. Install Dependencies for Groq
```bash
UV pip install groq python-dotenv
```

### 13. Run Application
```bash
python ui/app.py
```




