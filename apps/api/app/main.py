import logging
import time
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from pythonjsonlogger import jsonlogger

# Logger setup
logger = logging.getLogger("quality-api")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

app = FastAPI(title="Data Quality Framework API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Path: {request.url.path} Duration: {duration:.4f}s Status: {response.status_code}")
    return response

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/datasets")
def get_datasets():
    return [
        {"id": "ds-fin-001", "name": "finance.ledger_certified", "source": "Snowflake", "trust_score": 0.98, "status": "CERTIFIED"},
        {"id": "ds-sales-042", "name": "sales.daily_aggregates", "source": "Databricks", "trust_score": 0.85, "status": "WARNING"},
        {"id": "ds-hr-101", "name": "hr.employee_master", "source": "BigQuery", "trust_score": 0.94, "status": "STABLE"}
    ]

@app.get("/scores/summary")
def get_scores_summary():
    return {
        "global_trust_index": 0.92,
        "critical_violations": 4,
        "freshness_compliance": "98.5%",
        "active_rules": 1420
    }

@app.get("/rules")
def get_rules():
    return [
        {"id": "rule-null-email", "name": "Check Null Emails", "dimension": "Completeness", "severity": "P2"},
        {"id": "rule-range-age", "name": "Age Range Validation", "dimension": "Accuracy", "severity": "P3"},
        {"id": "rule-integrity-order", "name": "Order-Customer Integrity", "dimension": "Integrity", "severity": "P1"}
    ]

@app.get("/incidents")
def get_incidents():
    return [
        {"id": "inc-456", "dataset": "finance.ledger_certified", "rule": "Completeness", "severity": "P1", "mttr": "2.4h"},
        {"id": "inc-789", "dataset": "sales.daily_aggregates", "rule": "Freshness", "severity": "P2", "mttr": "4.1h"}
    ]

@app.get("/dashboard/summary")
def get_dashboard_summary():
    return {
        "total_datasets_monitored": 450,
        "certified_datasets": 320,
        "avg_trust_score": "A-",
        "incident_backlog": 12
    }

@app.post("/checks/run")
def run_check(dataset_id: str):
    logger.info(f"Triggering quality check for dataset: {dataset_id}")
    return {"status": "Quality Job Enqueued", "job_id": "job_dq_789"}
