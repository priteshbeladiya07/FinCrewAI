
import { useState } from "react";
import {
  Server,
  ShieldCheck,
  ExternalLink,
  Copy,
  Check
} from "lucide-react";

export default function Settings() {
  const base =
    import.meta.env.VITE_API_BASE_URL ||
    "/api";

  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(base);

      setCopied(true);

      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard access may be unavailable.
    }
  }

  return (
    <div className="stack narrow">
      <div className="intro">
        <div className="intro-icon">
          <Server />
        </div>

        <div>
          <h2>Workspace settings</h2>
          <p>
            Review your frontend connection and setup information.
          </p>
        </div>
      </div>

      <section className="panel settings">
        <div className="panel-head">
          <div>
            <h3>Backend connection</h3>
            <p>FastAPI service configured for this frontend</p>
          </div>

          <span className="tag">CONFIGURED</span>
        </div>

        <label>API base URL</label>

        <div className="copy-field">
          <code>{base}</code>

          <button onClick={copy}>
            {copied ? (
              <Check size={16} />
            ) : (
              <Copy size={16} />
            )}
          </button>
        </div>

        <p className="info">
          <ShieldCheck size={17} />
          Set this in your frontend .env file as
          VITE_API_BASE_URL, then restart Vite.
        </p>

        <a
          className="secondary"
          href={`${base.replace(/\/+$/, "")}/docs`}
          target="_blank"
          rel="noreferrer"
        >
          Open FastAPI Swagger docs
          <ExternalLink size={14} />
        </a>
      </section>

      <section className="panel settings">
        <h3>API route configuration</h3>

        <p className="muted">
          Endpoint paths are centralized in{" "}
          <code>src/services/api.js</code>. Compare them with
          Swagger and update them if your backend routes differ.
        </p>

        <div className="routes">
          {[
            "POST /v1/research",
            "GET /v1/research/history",
            "GET /v1/research/{research_id}",
            "GET /v1/research/{research_id}/report"
          ].map((x) => (
            <code key={x}>{x}</code>
          ))}
        </div>
      </section>
    </div>
  );
}
