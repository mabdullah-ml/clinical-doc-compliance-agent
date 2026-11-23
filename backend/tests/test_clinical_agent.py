"""Unit & contract tests for clinical fact extraction, discrepancy detection, and CTD drafting."""

from __future__ import annotations

import unittest

from app.agents.consistency_checker import run_compliance_audit_and_draft
from app.api.main import audit_clinical_bundle, get_sample_bundle, health
from app.data.sample_trials import SAMPLE_TRIAL_BUNDLE
from app.models.schemas import (
    AuditBundleRequest,
    ClinicalDocument,
    DiscrepancySeverity,
    DocumentType,
)


class TestClinicalDocComplianceAgent(unittest.TestCase):
    def test_sample_bundle_detects_critical_dosage_sae_and_major_sample_size_mismatches(self) -> None:
        report = run_compliance_audit_and_draft(SAMPLE_TRIAL_BUNDLE)
        fields = {d.field_name: d for d in report.discrepancies}

        self.assertIn("primary_dosage_mg", fields)
        self.assertEqual(fields["primary_dosage_mg"].severity, DiscrepancySeverity.CRITICAL)
        self.assertIn("sae_count", fields)
        self.assertEqual(fields["sae_count"].severity, DiscrepancySeverity.CRITICAL)
        self.assertIn("target_sample_size", fields)
        self.assertEqual(fields["target_sample_size"].severity, DiscrepancySeverity.MAJOR)
        self.assertIn("ich_gcp_reference", fields)
        self.assertEqual(fields["ich_gcp_reference"].severity, DiscrepancySeverity.MINOR)

        self.assertIn("BLOCKED", report.submission_gate)
        self.assertIn("Reconciled CTD Module 2.5 Clinical Overview", report.reconciled_ctd_draft)
        self.assertIn("50 mg", report.reconciled_ctd_draft)

    def test_consistent_bundle_achieves_100_readiness_score(self) -> None:
        clean_content = SAMPLE_TRIAL_BUNDLE.documents[0].content
        clean_bundle = AuditBundleRequest(
            study_id="AMX-402-CLEAN",
            documents=[
                ClinicalDocument(
                    doc_id="PROTO-CLEAN",
                    doc_type=DocumentType.PROTOCOL,
                    title="Protocol",
                    content=clean_content,
                ),
                ClinicalDocument(
                    doc_id="CTD-CLEAN",
                    doc_type=DocumentType.CTD_OVERVIEW,
                    title="CTD Overview",
                    content=clean_content,
                ),
            ],
        )
        report = run_compliance_audit_and_draft(clean_bundle)
        self.assertEqual(report.readiness_score, 100)
        self.assertEqual(len(report.discrepancies), 0)
        self.assertEqual(report.submission_gate, "READY FOR REGULATORY SUBMISSION")

    def test_fastapi_endpoints(self) -> None:
        self.assertEqual(health()["status"], "ok")
        bundle = get_sample_bundle()
        self.assertEqual(len(bundle.documents), 3)
        res = audit_clinical_bundle(bundle)
        self.assertEqual(res.study_id, "AMX-402-P2")


if __name__ == "__main__":
    unittest.main()
