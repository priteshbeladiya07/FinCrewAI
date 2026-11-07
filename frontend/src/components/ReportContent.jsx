
import React from "react";

function parseReport(content) {
  if (!content) return null;

  // API may return an object directly.
  if (typeof content === "object") return content;

  const cleaned = String(content)
    .trim()
    .replace(/^```(?:json)?\s*/i, "")
    .replace(/\s*```$/, "");

  try {
    return JSON.parse(cleaned);
  } catch {
    return null;
  }
}

function OutlookBadge({ value }) {
  const outlook = (value || "Not available").toLowerCase();

  let className = "report-badge neutral";

  if (outlook.includes("bullish")) {
    className = "report-badge positive";
  } else if (outlook.includes("bearish")) {
    className = "report-badge negative";
  } else if (outlook.includes("moderate")) {
    className = "report-badge warning";
  }

  return <span className={className}>{value || "Not available"}</span>;
}

function FactorCard({ factor, type }) {
  return (
    <article className="factor-card">
      <div className="factor-heading">
        <span className={`factor-indicator ${type}`}>
          {type === "positive" ? "+" : "−"}
        </span>
        <h4>{factor.title}</h4>
      </div>

      <p>{factor.evidence}</p>

      {factor.significance && (
        <div className="factor-significance">
          <strong>Why it matters</strong>
          <p>{factor.significance}</p>
        </div>
      )}

      {factor.time_horizon && (
        <span className="factor-horizon">
          {factor.time_horizon}
        </span>
      )}
    </article>
  );
}

function HorizonCard({ title, data }) {
  if (!data) return null;

  return (
    <article className="horizon-card">
      <h4>{title}</h4>
      <OutlookBadge value={data.outlook} />

      <p className="horizon-evidence">
        {data.supporting_evidence}
      </p>

      <div className="horizon-risk">
        <strong>Main risk</strong>
        <p>{data.main_risk}</p>
      </div>
    </article>
  );
}

function BulletList({ items }) {
  if (!Array.isArray(items) || items.length === 0) {
    return <p className="muted">No information available.</p>;
  }

  return (
    <ul className="report-list">
      {items.map((item, index) => (
        <li key={index}>{item}</li>
      ))}
    </ul>
  );
}

function PlainTextReport({ content }) {
  return (
    <div className="report-text">
      {String(content).split(/\r?\n/).map((line, index) => {
        const text = line.trim();

        if (!text) return <div className="space" key={index} />;

        if (/^#{1,3}\s/.test(text)) {
          const level = Math.min(text.match(/^#+/)[0].length + 1, 4);
          return React.createElement(
            `h${level}`,
            { key: index },
            text.replace(/^#{1,3}\s/, "")
          );
        }

        if (/^[-*]\s/.test(text)) {
          return <p className="bullet" key={index}>• {text.slice(2)}</p>;
        }

        return <p key={index}>{text}</p>;
      })}
    </div>
  );
}

export default function ReportContent({ content = "" }) {
  const report = parseReport(content);

  // Preserve support for existing non-JSON reports.
  if (!report) {
    return content ? (
      <PlainTextReport content={content} />
    ) : (
      <p className="muted">No final report has been saved yet.</p>
    );
  }

  return (
    <div className="structured-report">

      {/* Company header */}
      <section className="report-company">
        <div>
          <h2>{report.company || "Company Research"}</h2>
          <p className="muted">
            {report.ticker || "Ticker unavailable"} · Final investment research
          </p>
        </div>
        <OutlookBadge value={report.overall_outlook} />
      </section>

      {/* Summary metrics */}
      <section className="report-metrics">
        <article className="metric-card">
          <span>Overall Outlook</span>
          <OutlookBadge value={report.overall_outlook} />
        </article>

        <article className="metric-card">
          <span>Confidence</span>
          <strong>{report.confidence || "N/A"}</strong>
        </article>

        <article className="metric-card">
          <span>Risk Level</span>
          <strong>{report.risk_level || "N/A"}</strong>
        </article>
      </section>

      {/* Executive summary */}
      <section className="report-section">
        <h3>Executive Summary</h3>
        <p>{report.executive_summary || "No summary available."}</p>

        {report.outlook_justification && (
          <div className="report-justification">
            <strong>Outlook justification</strong>
            <p>{report.outlook_justification}</p>
          </div>
        )}
      </section>

      {/* Positive factors */}
      <section className="report-section">
        <h3>Positive Factors</h3>

        <div className="factor-grid">
          {report.positive_factors?.length ? (
            report.positive_factors.map((factor, index) => (
              <FactorCard
                key={index}
                factor={factor}
                type="positive"
              />
            ))
          ) : (
            <p className="muted">No positive factors reported.</p>
          )}
        </div>
      </section>

      {/* Negative factors */}
      <section className="report-section">
        <h3>Negative Factors</h3>

        <div className="factor-grid">
          {report.negative_factors?.length ? (
            report.negative_factors.map((factor, index) => (
              <FactorCard
                key={index}
                factor={factor}
                type="negative"
              />
            ))
          ) : (
            <p className="muted">No negative factors reported.</p>
          )}
        </div>
      </section>

      {/* Time horizon */}
      <section className="report-section">
        <h3>Investment Outlook by Time Horizon</h3>

        <div className="horizon-grid">
          <HorizonCard
            title="Short Term"
            data={report.time_horizon?.short_term}
          />

          <HorizonCard
            title="Medium Term"
            data={report.time_horizon?.medium_term}
          />

          <HorizonCard
            title="Long Term"
            data={report.time_horizon?.long_term}
          />
        </div>
      </section>

      {/* Sentiment and risk */}
      {report.sentiment_risk && (
        <section className="report-section">
          <h3>Sentiment & Risk Analysis</h3>

          <div className="two-column-report">
            <div>
              <h4>Positive Signals</h4>
              <BulletList items={report.sentiment_risk.positive_signals} />
            </div>

            <div>
              <h4>Key Risks</h4>
              <BulletList items={report.sentiment_risk.key_risks} />
            </div>
          </div>

          {report.sentiment_risk.competing_signals?.length > 0 && (
            <details className="report-details">
              <summary>View competing signals</summary>

              {report.sentiment_risk.competing_signals.map((signal, index) => (
                <article className="signal-card" key={index}>
                  <h4>{signal.topic}</h4>

                  <p>
                    <strong>Positive evidence:</strong>{" "}
                    {signal.positive_evidence}
                  </p>

                  <p>
                    <strong>Opposing evidence:</strong>{" "}
                    {signal.opposing_evidence}
                  </p>

                  <p>
                    <strong>Investment significance:</strong>{" "}
                    {signal.investment_significance}
                  </p>
                </article>
              ))}
            </details>
          )}

          {report.sentiment_risk.consistency_summary && (
            <div className="report-justification">
              <strong>Consistency summary</strong>
              <p>{report.sentiment_risk.consistency_summary}</p>
            </div>
          )}
        </section>
      )}

      {/* Monitoring */}
      <section className="report-section">
        <h3>Monitoring Points</h3>
        <BulletList items={report.monitoring_points} />
      </section>

      {/* Detailed analysis */}
      {report.detailed_analysis && (
        <section className="report-section">
          <h3>Detailed Agent Analysis</h3>

          {Object.entries(report.detailed_analysis).map(([agent, analysis]) => (
            <details className="report-details" key={agent}>
              <summary>
                {agent.charAt(0).toUpperCase() + agent.slice(1)} Analysis
              </summary>
              <p>{analysis}</p>
            </details>
          ))}
        </section>
      )}

      {/* Limitations */}
      <section className="report-section">
        <details className="report-details">
          <summary>Research Limitations</summary>
          <BulletList items={report.limitations} />
        </details>
      </section>

      {/* Conclusion */}
      <section className="report-section">
        <h3>Conclusion</h3>
        <p>{report.conclusion || "No conclusion available."}</p>
      </section>

      {/* Disclaimer */}
      <section className="report-disclaimer">
        <strong>Investment Disclaimer</strong>
        <p>{report.disclaimer || "This report is for informational purposes only."}</p>
      </section>

    </div>
  );
}
