
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  Search,
  RefreshCw,
  ArrowUpRight,
  Filter
} from "lucide-react";

import {
  getResearchHistory,
  getApiError
} from "../services/api";

import StatusBadge from "../components/StatusBadge";
import EmptyState from "../components/EmptyState";
import { formatDateTime } from "../utils/format";

export default function ResearchHistory() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [q, setQ] = useState("");
  const [status, setStatus] = useState("all");

  async function load() {
    setLoading(true);
    setError("");

    try {
      setJobs(await getResearchHistory());
    } catch (e) {
      setError(getApiError(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const rows = useMemo(
    () =>
      jobs.filter(
        (j) =>
          `${j.company || ""} ${j.ticker || ""} ${j.research_id || ""}`
            .toLowerCase()
            .includes(q.toLowerCase()) &&
          (status === "all" ||
            String(j.status).toLowerCase() === status)
      ),
    [jobs, q, status]
  );

  return (
    <div className="stack">
      <div className="section-head">
        <div>
          <h2>Research history</h2>
          <p>All research jobs stored by your backend</p>
        </div>

        <button
          className="secondary small"
          onClick={load}
        >
          <RefreshCw size={14} />
          Refresh
        </button>
      </div>

      <section className="panel">
        <div className="toolbar">
          <div className="search">
            <Search size={16} />

            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search company, ticker or research ID…"
            />
          </div>

          <div className="filter">
            <Filter size={15} />

            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              <option value="all">All statuses</option>

              {["completed", "processing", "pending", "failed"].map(
                (s) => (
                  <option key={s}>{s}</option>
                )
              )}
            </select>
          </div>
        </div>

        {loading ? (
          <div className="loading">
            Loading saved research…
          </div>
        ) : error ? (
          <div className="error">
            <b>Unable to load history</b>
            <p>{error}</p>
            <small>
              Verify the history endpoint in api.js.
            </small>
          </div>
        ) : rows.length === 0 ? (
          <EmptyState
            title={
              jobs.length
                ? "No matching research"
                : "No research found"
            }
            description={
              jobs.length
                ? "Try changing your search or status filter."
                : "Start a new research job and it will appear here."
            }
          />
        ) : (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Company / Research ID</th>
                  <th>Ticker</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Updated</th>
                  <th />
                </tr>
              </thead>

              <tbody>
                {rows.map((j) => (
                  <tr key={j.research_id || j.id}>
                    <td>
                      <b>{j.company || "Unnamed company"}</b>
                      <small className="mono">
                        {j.research_id || j.id}
                      </small>
                    </td>

                    <td className="mono">
                      {j.ticker || "—"}
                    </td>

                    <td>
                      <StatusBadge status={j.status} />
                    </td>

                    <td>
                      {formatDateTime(j.created_at)}
                    </td>

                    <td>
                      {formatDateTime(j.updated_at)}
                    </td>

                    <td>
                      <Link
                        className="row-link"
                        to={`/research/${j.research_id || j.id}`}
                      >
                        <ArrowUpRight size={17} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="table-foot">
          Showing {rows.length} of {jobs.length} research jobs
        </div>
      </section>
    </div>
  );
}
