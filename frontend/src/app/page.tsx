"use client";

import { useEffect, useState } from "react";
import { fetchSampleBundle, readinessTone, runClinicalAudit } from "@/lib/api";
import type { AuditBundleRequest, ComplianceAuditResponse } from "@/types/clinical";

export default function ClinicalAuditConsole() {
  const [bundle, setBundle] = useState<AuditBundleRequest | null>(null);
  const [report, setReport] = useState<ComplianceAuditResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSampleBundle()
      .then((data) => setBundle(data))
      .catch((err) => setError(err instanceof Error ? err.message : "Backend unreachable."));
  }, []);

  async function handleRunAudit() {
    if (!bundle) return;
    setLoading(true);
    setError(null);
    try {
      const result = await runClinicalAudit(bundle);
      setReport(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Audit execution failed.");
    } finally {
      setLoading(false);
    }
  }

  function updateDocContent(index: number, content: string) {
    if (!bundle) return;
    const updated = bundle.documents.map((d, i) => (i === index ? { ...d, content } : d));
    setBundle({ ...bundle, documents: updated });
  }

  const tone = report ? readinessTone(report.readiness_score) : "warn";
  const toneClass =
    tone === "ready"
      ? "border-emerald-500/40 bg-emerald-500/15 text-emerald-300"
      : tone === "warn"
        ? "border-amber-500/40 bg-amber-500/15 text-amber-300"
        : "border-rose-500/40 bg-rose-500/15 text-rose-300";

  return (
    <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <header className="border-b border-slate-800 pb-6">
        <span className="rounded-full border border-sky-500/40 bg-sky-500/10 px-3 py-1 text-xs font-medium text-sky-300">
          Pharma / Regulatory GenAI · Protocol · Investigator&apos;s Brochure · CTD Module 2.5
        </span>
        <h1 className="mt-3 text-2xl font-bold text-white sm:text-3xl">
          Clinical Document Compliance &amp; Cross-Doc Consistency Agent
        </h1>
        <p className="mt-1 text-sm text-slate-400">
          Extracts clinical facts with line citations, flags numerical/safety contradictions across
          Protocol, IB, and CTD drafts, and synthesizes an auditable reconciled CTD overview.
        </p>
      </header>

      {error && (
        <div className="mt-4 rounded-lg border border-rose-500/40 bg-rose-950/40 px-4 py-3 text-sm text-rose-200">
          {error}
        </div>
      )}

      {/* Editable Source Document Bundle */}
      {bundle && (
        <section className="mt-6 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-sm font-semibold text-white">
              Study Bundle: <span className="font-mono text-sky-400">{bundle.study_id}</span>{" "}
              ({bundle.documents.length} Synthetic Artifacts)
            </h2>
            <button
              onClick={handleRunAudit}
              disabled={loading}
              className="rounded-lg bg-sky-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-sky-500 disabled:opacity-50"
            >
              {loading ? "Auditing Cross-Document Consistency..." : "Run Compliance Audit & Draft CTD"}
            </button>
          </div>

          <div className="grid gap-4 lg:grid-cols-3">
            {bundle.documents.map((doc, idx) => (
              <div
                key={doc.doc_id}
                className="rounded-xl border border-slate-800 bg-slate-900/80 p-4"
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono text-sky-400">{doc.doc_id}</span>
                  <span className="rounded bg-slate-800 px-2 py-0.5 text-slate-300">
                    {doc.doc_type}
                  </span>
                </div>
                <div className="mt-1 text-sm font-medium text-white">{doc.title}</div>
                <textarea
                  rows={8}
                  value={doc.content}
                  onChange={(e) => updateDocContent(idx, e.target.value)}
                  className="mt-3 w-full rounded-lg border border-slate-700 bg-slate-950 p-2.5 font-mono text-xs text-slate-200"
                />
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Audit Results & Reconciled CTD Draft */}
      {report && (
        <section className="mt-8 space-y-6">
          <div className={`rounded-xl border p-5 ${toneClass}`}>
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <div className="text-xs uppercase tracking-wider opacity-80">
                  Regulatory Submission Gate
                </div>
                <div className="mt-1 text-lg font-bold">{report.submission_gate}</div>
              </div>
              <div className="text-right">
                <div className="text-xs opacity-80">Readiness Score</div>
                <div className="text-3xl font-bold">{report.readiness_score}/100</div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-5">
            <h3 className="text-sm font-semibold text-white">
              Cross-Document Discrepancy Matrix ({report.discrepancies.length})
            </h3>
            <div className="mt-3 space-y-3">
              {report.discrepancies.map((d) => (
                <div
                  key={d.discrepancy_id}
                  className="rounded-lg border border-slate-800 bg-slate-950/60 p-4 text-xs"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <span
                      className={`rounded px-2 py-0.5 font-bold ${
                        d.severity === "CRITICAL"
                          ? "bg-rose-500/20 text-rose-300"
                          : d.severity === "MAJOR"
                            ? "bg-amber-500/20 text-amber-300"
                            : "bg-sky-500/20 text-sky-300"
                      }`}
                    >
                      {d.severity}
                    </span>
                    <span className="font-mono text-slate-300">{d.discrepancy_id}</span>
                    <span className="font-semibold text-white">{d.field_name}</span>
                  </div>
                  <p className="mt-2 text-slate-300">
                    Authoritative (<code>{d.authoritative_doc_id}</code>):{" "}
                    <strong className="text-emerald-300">{d.authoritative_value}</strong> vs.
                    Conflicting (<code>{d.conflicting_doc_id}</code>):{" "}
                    <strong className="text-rose-300">{d.conflicting_value}</strong>
                  </p>
                  <p className="mt-1 text-slate-400">{d.recommended_fix}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/15 p-5">
            <h3 className="text-sm font-semibold text-emerald-300">
              Reconciled CTD Module 2.5 Draft (Citation-Backed)
            </h3>
            <pre className="mt-3 whitespace-pre-wrap rounded-lg bg-slate-950/80 p-4 font-sans text-xs leading-relaxed text-slate-200">
              {report.reconciled_ctd_draft}
            </pre>
          </div>
        </section>
      )}
    </main>
  );
}
