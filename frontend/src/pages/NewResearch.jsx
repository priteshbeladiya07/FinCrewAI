
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Building2,
  ArrowRight,
  Sparkles,
  Info
} from "lucide-react";

import { submitResearch, getApiError } from "../services/api";

export default function NewResearch() {
  const [company, setCompany] = useState("");
  const [ticker, setTicker] = useState("");
  const [showTicker, setShowTicker] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const nav = useNavigate();

  async function submit(e) {
    e.preventDefault();

    if (!company.trim()) {
      setError("Enter a company name to continue.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const r = await submitResearch(
        company,
        ticker && showTicker ? ticker : ""
      );

      if (!r.research_id) {
        throw new Error(
          "API response did not include research_id. Check submitResearch() in api.js."
        );
      }

      nav(`/research/${r.research_id}`, {
        state: { submitted: true }
      });
    } catch (e) {
      setError(
        e.response
          ? getApiError(e)
          : e.message || getApiError(e)
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack narrow">
      <div className="intro">
        <div className="intro-icon">
          <Sparkles />
        </div>

        <div>
          <h2>Start company research</h2>
          <p>
            Submit a company and let your six-agent crew prepare a
            consolidated research report.
          </p>
        </div>
      </div>

      <section className="panel form-panel">
        <div className="panel-head">
          <div>
            <h3>Research details</h3>
            <p>Enter the company you want to analyze.</p>
          </div>

          <span className="tag">STEP 01 / 01</span>
        </div>

        <form onSubmit={submit}>
          <label>
            Company name <em>*</em>
          </label>

          <div className="input">
            <Building2 size={18} />

            <input
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              placeholder="e.g. Tata Steel, Apple, Microsoft"
              autoFocus
            />
          </div>

          <small className="hint">
            You can enter a company name even if you don't know its
            ticker symbol.
          </small>

          <button
            type="button"
            className="toggle"
            onClick={() => setShowTicker(!showTicker)}
          >
            {showTicker
              ? "− Hide optional ticker"
              : "+ I know the ticker (optional)"}
          </button>

          {showTicker && (
            <>
              <label>Ticker symbol</label>

              <div className="input">
                <input
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value)}
                  placeholder="e.g. TATASTEEL.NS"
                />
              </div>
            </>
          )}

          {error && (
            <div className="form-error">
              {error}
            </div>
          )}

          <div className="info">
            <Info size={17} />
            Research may take a few minutes. Your report will be
            saved in Research History.
          </div>

          <button
            className="primary submit"
            disabled={loading}
          >
            {loading ? (
              "Submitting research…"
            ) : (
              <>
                Start AI research <ArrowRight size={17} />
              </>
            )}
          </button>
        </form>
      </section>

      <section className="panel">
        <h3>What happens next?</h3>

        <div className="steps">
          {[
            "Company and market news are gathered",
            "Five specialist agents analyze different dimensions",
            "Investment agent combines findings into one report",
            "Final report is saved to research history"
          ].map((s, i) => (
            <div key={s}>
              <b>{i + 1}</b>
              <span>{s}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
