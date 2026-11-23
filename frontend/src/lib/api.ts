import type { AuditBundleRequest, ComplianceAuditResponse } from "../types/clinical";

export function apiBaseUrl(override?: string): string {
  const raw = override ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  return raw.replace(/\/+$/, "");
}

export function readinessTone(score: number): "ready" | "warn" | "blocked" {
  if (score >= 90) return "ready";
  if (score >= 60) return "warn";
  return "blocked";
}

export async function fetchSampleBundle(): Promise<AuditBundleRequest> {
  const res = await fetch(`${apiBaseUrl()}/api/v1/sample-bundle`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch sample bundle (${res.status})`);
  return (await res.json()) as AuditBundleRequest;
}

export async function runClinicalAudit(bundle: AuditBundleRequest): Promise<ComplianceAuditResponse> {
  const res = await fetch(`${apiBaseUrl()}/api/v1/audit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(bundle),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Audit failed (${res.status})`);
  return (await res.json()) as ComplianceAuditResponse;
}
