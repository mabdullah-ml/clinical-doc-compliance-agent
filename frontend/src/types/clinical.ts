export type DocumentType = "protocol" | "investigator_brochure" | "ctd_overview" | "csr";
export type DiscrepancySeverity = "CRITICAL" | "MAJOR" | "MINOR";

export interface ClinicalDocument {
  doc_id: string;
  doc_type: DocumentType;
  title: string;
  version: string;
  content: string;
}

export interface ExtractedFact {
  doc_id: string;
  doc_type: DocumentType;
  field_name: string;
  value: string;
  line_number: number;
  citation_excerpt: string;
}

export interface CrossDocDiscrepancy {
  discrepancy_id: string;
  severity: DiscrepancySeverity;
  field_name: string;
  authoritative_doc_id: string;
  authoritative_value: string;
  conflicting_doc_id: string;
  conflicting_value: string;
  regulatory_impact: string;
  recommended_fix: string;
}

export interface AuditBundleRequest {
  study_id: string;
  documents: ClinicalDocument[];
}

export interface ComplianceAuditResponse {
  study_id: string;
  readiness_score: number;
  submission_gate: string;
  extracted_facts: ExtractedFact[];
  discrepancies: CrossDocDiscrepancy[];
  reconciled_ctd_draft: string;
}
