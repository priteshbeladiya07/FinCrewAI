
import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Download,
  RefreshCw,
  FileText,
  Clock3
} from "lucide-react";

import {
  getResearchStatus,
  getResearchReport,
  getApiError
} from "../services/api";

import StatusBadge from "../components/StatusBadge";
import ReportContent from "../components/ReportContent";
import { formatDateTime } from "../utils/format";

export default function ResearchReport() {
  const { id } = useParams();

  const [job, setJob] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const s = await getResearchStatus(id);
      setJob(s);

      if (String(s.status).toLowerCase() === "completed") {
        try {
          setReport(await getResearchReport(id));
        } catch {
          setReport(s);
        }
      } else {
        setReport(s);
      }
    } catch (e) {
      setError(getApiError(e));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  const content =
    report?.final_report ||
    report?.report ||
    job?.final_report ||
    "";

  function download() {
    if (!content) return;

    const u = URL.createObjectURL(
      new Blob([content], {
        type: "text/markdown;charset=utf-8"
      })
    );

    const a = document.createElement("a");

    a.href = u;
    a.download = `${(job?.company || "research").replace(
      /[^a-z0-9-_]/gi,
      "_"
    )}-report.md`;

    a.click();

    URL.revokeObjectURL(u);
  }

  return (
    <div className="stack">
      <Link className="back" to="/history">
        <ArrowLeft size={16} />
        Back to research history
      </Link>

      {loading ? (
        <section className="panel loading">
          Loading research report…
        </section>
      ) : error ? (
        <section className="panel error">
          <b>Could not load this research</b>
          <p>{error}</p>

          <button
            className="secondary small"
            onClick={load}
          >
            Retry
          </button>
        </section>
      ) : (
        <>
          <section className="report-hero">
            <div>
              <div className="eyebrow">
                ▤ RESEARCH REPORT
              </div>

              <h2>
                {job?.company ||
                  report?.company ||
                  "Company research"}
              </h2>

              <p>
                {job?.ticker ||
                  report?.ticker ||
                  "Ticker not provided"}{" "}
                · <code>{id}</code>
              </p>
            </div>

            <div className="report-actions">
              <StatusBadge
                status={job?.status || report?.status}
              />

              <button
                className="secondary small"
                onClick={load}
              >
                <RefreshCw size={14} />
                Refresh
              </button>

              <button
                className="primary small"
                onClick={download}
                disabled={!content}
              >
                <Download size={14} />
                Export report
              </button>
            </div>
          </section>

          <div className="meta-grid">
            <div>
              <Clock3 />
              <small>Created</small>
              <b>
                {formatDateTime(
                  job?.created_at || report?.created_at
                )}
              </b>
            </div>

            <div>
              <RefreshCw />
              <small>Last updated</small>
              <b>
                {formatDateTime(
                  job?.updated_at || report?.updated_at
                )}
              </b>
            </div>

            <div>
              <FileText />
              <small>Research ID</small>
              <b className="mono">{id}</b>
            </div>
          </div>

          {["pending", "processing", "running"].includes(
            String(job?.status).toLowerCase()
          ) ? (
            <section className="panel processing">
              <div className="pulse-dots">
                <i />
                <i />
                <i />
              </div>

              <h3>Your AI research is in progress</h3>

              <p>
                The six-agent crew is working. Refresh this
                page to check for the completed report.
              </p>

              <button
                className="secondary small"
                onClick={load}
              >
                Check status
              </button>
            </section>
          ) : String(job?.status).toLowerCase() ===
            "failed" ? (
            <section className="panel error">
              <b>Research failed</b>
              <p>
                {job?.error ||
                  report?.error ||
                  "The backend reported a failure."}
              </p>
            </section>
          ) : (
            <section className="panel report-panel">
              <div className="panel-head">
                <div>
                  <h3>Final investment research</h3>
                  <p>
                    Consolidated output from your CrewAI
                    workflow
                  </p>
                </div>

                <span className="tag">FINAL REPORT</span>
              </div>

              <ReportContent content={content} />
            </section>
          )}
        </>
      )}
    </div>
  );
}
