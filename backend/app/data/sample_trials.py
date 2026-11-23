"""Synthetic (100% fictional, NDA-safe) clinical trial documents for demo & testing."""

from __future__ import annotations

from app.models.schemas import AuditBundleRequest, ClinicalDocument, DocumentType

SAMPLE_TRIAL_BUNDLE = AuditBundleRequest(
    study_id="AMX-402-P2",
    documents=[
        ClinicalDocument(
            doc_id="PROTO-2026-01",
            doc_type=DocumentType.PROTOCOL,
            title="Phase II Study Protocol — Compound AMX-402",
            version="2.0",
            content=(
                "Study Identifier: AMX-402-P2\n"
                "Compound: AMX-402\n"
                "Clinical Phase: Phase II\n"
                "Target Sample Size: N=240 randomized patients across 12 sites\n"
                "Primary Dosage: 50 mg oral once daily for 24 weeks\n"
                "Serious Adverse Events (SAE): 3 treatment-emergent SAEs recorded in interim cut\n"
                "Primary Endpoint: Change in systolic blood pressure from baseline at Week 24\n"
                "Regulatory Standard: Conducted in full compliance with ICH-E6(R2) GCP guidelines."
            ),
        ),
        ClinicalDocument(
            doc_id="IB-AMX402-v3",
            doc_type=DocumentType.INVESTIGATOR_BROCHURE,
            title="Investigator's Brochure — AMX-402 Edition 3",
            version="3.0",
            content=(
                "Compound: AMX-402\n"
                "Clinical Phase: Phase II\n"
                "Target Sample Size: N=240 subjects enrolled globally\n"
                "Primary Dosage: 75 mg oral once daily in maintenance cohort\n"
                "Serious Adverse Events (SAE): 2 treatment-emergent SAEs reported to date\n"
                "Regulatory Standard: Aligned with ICH-E6(R2) GCP safety reporting rules."
            ),
        ),
        ClinicalDocument(
            doc_id="CTD-M2.5-DRAFT",
            doc_type=DocumentType.CTD_OVERVIEW,
            title="CTD Module 2.5 Clinical Overview (Draft)",
            version="0.9-draft",
            content=(
                "Compound: AMX-402\n"
                "Clinical Phase: Phase II\n"
                "Target Sample Size: N=220 patients evaluated in pivotal cohort\n"
                "Primary Dosage: 50 mg oral once daily\n"
                "Serious Adverse Events (SAE): 3 treatment-emergent SAEs summarized in Table 4\n"
                "Primary Endpoint: Change in systolic blood pressure from baseline at Week 24"
            ),
        ),
    ],
)
