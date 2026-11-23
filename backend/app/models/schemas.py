"""Pydantic v2 domain models for clinical document auditing and CTD drafting."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class DocumentType(StrEnum):
    PROTOCOL = "protocol"
    INVESTIGATOR_BROCHURE = "investigator_brochure"
    CTD_OVERVIEW = "ctd_overview"
    CSR = "csr"


class DiscrepancySeverity(StrEnum):
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"


class ClinicalDocument(BaseModel):
    doc_id: str = Field(..., min_length=2, max_length=64)
    doc_type: DocumentType
    title: str = Field(..., min_length=3, max_length=200)
    version: str = Field(default="1.0")
    content: str = Field(..., min_length=20, max_length=50000)


class ExtractedFact(BaseModel):
    doc_id: str
    doc_type: DocumentType
    field_name: str
    value: str
    line_number: int
    citation_excerpt: str


class CrossDocDiscrepancy(BaseModel):
    discrepancy_id: str
    severity: DiscrepancySeverity
    field_name: str
    authoritative_doc_id: str
    authoritative_value: str
    conflicting_doc_id: str
    conflicting_value: str
    regulatory_impact: str
    recommended_fix: str


class AuditBundleRequest(BaseModel):
    study_id: str = Field(default="AMX-402-P2")
    documents: list[ClinicalDocument] = Field(..., min_length=2)


class ComplianceAuditResponse(BaseModel):
    study_id: str
    readiness_score: int = Field(..., ge=0, le=100)
    submission_gate: str
    extracted_facts: list[ExtractedFact]
    discrepancies: list[CrossDocDiscrepancy]
    reconciled_ctd_draft: str
