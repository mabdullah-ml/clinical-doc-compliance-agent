"""Structured clinical parameter extraction with exact source document and line citations."""

from __future__ import annotations

import re

from app.models.schemas import ClinicalDocument, ExtractedFact

PATTERNS: dict[str, re.Pattern[str]] = {
    "compound_name": re.compile(r"Compound:\s*([A-Z0-9\-]+)", re.IGNORECASE),
    "clinical_phase": re.compile(r"Clinical Phase:\s*(Phase\s+[I|V|X|1-4]+[a-b]?)", re.IGNORECASE),
    "target_sample_size": re.compile(r"\bN\s*=\s*(\d+)\b", re.IGNORECASE),
    "primary_dosage_mg": re.compile(r"Primary Dosage:\s*(\d+\s*mg)", re.IGNORECASE),
    "sae_count": re.compile(r"Serious Adverse Events.*?:\s*(\d+)\b", re.IGNORECASE),
    "ich_gcp_reference": re.compile(r"\b(ICH-E6(?:\(R\d\))?\s*GCP)\b", re.IGNORECASE),
}


def extract_document_facts(doc: ClinicalDocument) -> list[ExtractedFact]:
    """Extract normalized regulatory parameters with line-level audit citations."""
    facts: list[ExtractedFact] = []
    lines = doc.content.splitlines()

    for field_name, pattern in PATTERNS.items():
        for line_no, line in enumerate(lines, start=1):
            match = pattern.search(line)
            if match:
                normalized = re.sub(r"\s+", " ", match.group(1).strip())
                facts.append(
                    ExtractedFact(
                        doc_id=doc.doc_id,
                        doc_type=doc.doc_type,
                        field_name=field_name,
                        value=normalized,
                        line_number=line_no,
                        citation_excerpt=line.strip(),
                    )
                )
                break
    return facts
