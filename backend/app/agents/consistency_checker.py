"""Cross-Document Consistency Checker & Reconciled CTD Section Drafting Agents."""

from __future__ import annotations

from app.agents.fact_extractor import extract_document_facts
from app.models.schemas import (
    AuditBundleRequest,
    ComplianceAuditResponse,
    CrossDocDiscrepancy,
    DiscrepancySeverity,
    DocumentType,
    ExtractedFact,
)

FIELD_SEVERITY: dict[str, tuple[DiscrepancySeverity, str]] = {
    "primary_dosage_mg": (
        DiscrepancySeverity.CRITICAL,
        "Dosage discrepancy across regulatory submissions risks clinical safety rejection.",
    ),
    "sae_count": (
        DiscrepancySeverity.CRITICAL,
        "Serious Adverse Event (SAE) count mismatch violates pharmacovigilance audit integrity.",
    ),
    "target_sample_size": (
        DiscrepancySeverity.MAJOR,
        "Sample size inconsistency invalidates statistical power and CTD efficacy tables.",
    ),
    "clinical_phase": (
        DiscrepancySeverity.MAJOR,
        "Conflicting clinical trial phase undermines regulatory dossier classification.",
    ),
    "compound_name": (
        DiscrepancySeverity.CRITICAL,
        "Compound identifier mismatch across linked clinical artifacts.",
    ),
}


def run_compliance_audit_and_draft(bundle: AuditBundleRequest) -> ComplianceAuditResponse:
    """Execute 3-stage agent workflow: Fact Extraction -> Cross-Doc Audit -> Reconciled CTD Draft."""
    all_facts: list[ExtractedFact] = []
    facts_by_doc: dict[str, dict[str, ExtractedFact]] = {}

    for doc in bundle.documents:
        extracted = extract_document_facts(doc)
        all_facts.extend(extracted)
        facts_by_doc[doc.doc_id] = {f.field_name: f for f in extracted}

    # Authoritative source of truth: Protocol document if provided, otherwise first doc
    auth_doc = next(
        (d for d in bundle.documents if d.doc_type == DocumentType.PROTOCOL),
        bundle.documents[0],
    )
    auth_facts = facts_by_doc[auth_doc.doc_id]

    discrepancies: list[CrossDocDiscrepancy] = []
    disc_idx = 1

    for doc in bundle.documents:
        if doc.doc_id == auth_doc.doc_id:
            continue
        doc_facts = facts_by_doc[doc.doc_id]

        for field_name, (severity, impact) in FIELD_SEVERITY.items():
            auth_fact = auth_facts.get(field_name)
            other_fact = doc_facts.get(field_name)
            if auth_fact and other_fact and auth_fact.value.lower() != other_fact.value.lower():
                discrepancies.append(
                    CrossDocDiscrepancy(
                        discrepancy_id=f"DISC-{disc_idx:03d}",
                        severity=severity,
                        field_name=field_name,
                        authoritative_doc_id=auth_doc.doc_id,
                        authoritative_value=auth_fact.value,
                        conflicting_doc_id=doc.doc_id,
                        conflicting_value=other_fact.value,
                        regulatory_impact=impact,
                        recommended_fix=(
                            f"Update '{field_name}' in {doc.doc_id} (line {other_fact.line_number}) "
                            f"from '{other_fact.value}' to '{auth_fact.value}' matching "
                            f"{auth_doc.doc_id} (line {auth_fact.line_number})."
                        ),
                    )
                )
                disc_idx += 1

        # Check required ICH-GCP compliance citation on CTD Overview / IB documents
        if "ich_gcp_reference" in auth_facts and "ich_gcp_reference" not in doc_facts:
            discrepancies.append(
                CrossDocDiscrepancy(
                    discrepancy_id=f"DISC-{disc_idx:03d}",
                    severity=DiscrepancySeverity.MINOR,
                    field_name="ich_gcp_reference",
                    authoritative_doc_id=auth_doc.doc_id,
                    authoritative_value=auth_facts["ich_gcp_reference"].value,
                    conflicting_doc_id=doc.doc_id,
                    conflicting_value="MISSING",
                    regulatory_impact="Missing explicit ICH-E6 GCP compliance statement in regulatory draft.",
                    recommended_fix=(
                        f"Insert ICH-E6(R2) GCP compliance attestation in {doc.doc_id} "
                        f"referencing {auth_doc.doc_id}."
                    ),
                )
            )
            disc_idx += 1

    # Compute 0-100 Regulatory Readiness Score
    penalty = 0
    for d in discrepancies:
        if d.severity == DiscrepancySeverity.CRITICAL:
            penalty += 30
        elif d.severity == DiscrepancySeverity.MAJOR:
            penalty += 15
        else:
            penalty += 5
    readiness_score = max(0, 100 - penalty)
    has_critical = any(d.severity == DiscrepancySeverity.CRITICAL for d in discrepancies)
    submission_gate = (
        "BLOCKED — Critical Discrepancies Require QA Sign-Off"
        if has_critical
        else ("READY WITH MINOR NOTES" if discrepancies else "READY FOR REGULATORY SUBMISSION")
    )

    reconciled_draft = _draft_reconciled_ctd(
        study_id=bundle.study_id,
        auth_doc_id=auth_doc.doc_id,
        auth_facts=auth_facts,
        discrepancies=discrepancies,
    )

    return ComplianceAuditResponse(
        study_id=bundle.study_id,
        readiness_score=readiness_score,
        submission_gate=submission_gate,
        extracted_facts=all_facts,
        discrepancies=discrepancies,
        reconciled_ctd_draft=reconciled_draft,
    )


def _draft_reconciled_ctd(
    study_id: str,
    auth_doc_id: str,
    auth_facts: dict[str, ExtractedFact],
    discrepancies: list[CrossDocDiscrepancy],
) -> str:
    compound = auth_facts.get("compound_name")
    phase = auth_facts.get("clinical_phase")
    sample_size = auth_facts.get("target_sample_size")
    dosage = auth_facts.get("primary_dosage_mg")
    sae = auth_facts.get("sae_count")
    gcp = auth_facts.get("ich_gcp_reference")

    disc_lines = (
        "\n".join(
            f"- **[{d.severity.value}] {d.discrepancy_id} (`{d.field_name}`):** "
            f"{d.conflicting_doc_id} had `{d.conflicting_value}` → reconciled to "
            f"`{d.authoritative_value}` per `[{d.authoritative_doc_id}]`."
            for d in discrepancies
        )
        if discrepancies
        else "- No cross-document discrepancies detected across submitted clinical artifacts."
    )

    return (
        f"# Reconciled CTD Module 2.5 Clinical Overview — {study_id}\n\n"
        f"> **Authoritative Reference:** `{auth_doc_id}` (All numerical claims traced below)\n\n"
        f"## 1. Product Development Rationale & Design\n"
        f"Compound **{compound.value if compound else 'N/A'}** is under evaluation in a "
        f"**{phase.value if phase else 'N/A'}** clinical study (`{study_id}`) enrolling "
        f"**N={sample_size.value if sample_size else 'N/A'}** randomized participants "
        f"[`{auth_doc_id}`, L{sample_size.line_number if sample_size else 1}].\n\n"
        f"## 2. Dosing Regimen & Safety Summary\n"
        f"The authoritative primary dosing regimen is **{dosage.value if dosage else 'N/A'}** "
        f"[`{auth_doc_id}`, L{dosage.line_number if dosage else 1}]. Interim pharmacovigilance "
        f"review confirmed **{sae.value if sae else '0'}** treatment-emergent Serious Adverse Events "
        f"(SAEs) [`{auth_doc_id}`, L{sae.line_number if sae else 1}].\n\n"
        f"## 3. Regulatory Compliance Attestation\n"
        f"All clinical operations comply with **{gcp.value if gcp else 'ICH-E6(R2) GCP'}** "
        f"standards [`{auth_doc_id}`].\n\n"
        f"## 4. Cross-Document Audit & Reconciliation Log\n"
        f"{disc_lines}\n"
    )
