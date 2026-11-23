"""FastAPI service for clinical trial cross-document compliance auditing & CTD drafting."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.consistency_checker import run_compliance_audit_and_draft
from app.data.sample_trials import SAMPLE_TRIAL_BUNDLE
from app.models.schemas import AuditBundleRequest, ComplianceAuditResponse

app = FastAPI(
    title="Clinical Document Compliance & CTD Drafting Agent",
    version="1.0.0",
    description=(
        "Automated regulatory document fact extraction, cross-document consistency verification "
        "(Protocol vs IB vs CTD), and citation-backed CTD drafting."
    ),
)

raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "clinical-doc-compliance-agent"}


@app.get("/api/v1/sample-bundle", response_model=AuditBundleRequest)
def get_sample_bundle() -> AuditBundleRequest:
    return SAMPLE_TRIAL_BUNDLE


@app.post("/api/v1/audit", response_model=ComplianceAuditResponse)
def audit_clinical_bundle(request: AuditBundleRequest) -> ComplianceAuditResponse:
    return run_compliance_audit_and_draft(request)
