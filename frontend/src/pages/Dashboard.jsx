import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Plus, RefreshCw, ArrowUpRight, CheckCircle2, Clock3, BriefcaseBusiness, Activity, ArrowRight, Newspaper, Landmark, CandlestickChart, MessagesSquare, ShieldAlert, BrainCircuit, Sparkles, Database, TrendingUp } from "lucide-react";
import { getResearchHistory, getApiError } from "../services/api";
import StatusBadge from "../components/StatusBadge";
import EmptyState from "../components/EmptyState";
import { formatDateTime } from "../utils/format";

const agents = [
  ["01", "News intelligence", "Events, catalysts & company updates", Newspaper],
  ["02", "Fundamental analysis", "Financial health & valuation", Landmark],
  ["03", "Technical analysis", "Price action & indicators", CandlestickChart],
  ["04", "Market sentiment", "Narratives & investor mood", MessagesSquare],
  ["05", "Risk assessment", "Downside factors & exposure", ShieldAlert],
  ["06", "Investment synthesis", "Cross-agent conclusions", BrainCircuit],
];

export default function Dashboard() {
  const [jobs, setJobs] = useState([]), [loading, setLoading] = useState(true), [error, setError] = useState("");
  async function load() { setLoading(true); setError(""); try { setJobs(await getResearchHistory()); } catch (e) { setError(getApiError(e)); } finally { setLoading(false); } }
  useEffect(() => { load(); }, []);
  const stats = useMemo(() => ({ total: jobs.length, done: jobs.filter(x => String(x.status).toLowerCase() === "completed").length, active: jobs.filter(x => ["pending", "processing", "running"].includes(String(x.status).toLowerCase())).length, failed: jobs.filter(x => String(x.status).toLowerCase() === "failed").length }), [jobs]);
  return <div className="stack dashboard-page">
    <section className="hero">
      <div className="hero-copy"><div className="eyebrow"><span className="eyebrow-pulse" /> MULTI-AGENT FINANCIAL INTELLIGENCE</div><h2>Clarity behind<br /><span>every investment.</span></h2><p>Six specialist AI agents. One consolidated research view. Make your next company analysis more structured, evidence-led and easier to navigate.</p><Link to="/new-research" className="primary"><Plus size={17} /> Start company research <ArrowRight size={16} /></Link><div className="hero-foot"><span><i /> Research workspace</span><span>Built for deeper analysis</span></div></div>
      <div className="hero-visual" aria-hidden="true"><div className="visual-grid" /><div className="visual-ring ring-one" /><div className="visual-ring ring-two" /><div className="visual-core"><Activity size={34} /><b>FIN</b><small>INTELLIGENCE</small></div><div className="orbit-node node-a"><Newspaper /></div><div className="orbit-node node-b"><Landmark /></div><div className="orbit-node node-c"><CandlestickChart /></div><div className="orbit-node node-d"><BrainCircuit /></div><div className="visual-label label-a">SIGNALS</div><div className="visual-label label-b">SYNTHESIS</div></div>
    </section>

    <div className="section-head"><div><div className="eyebrow muted-eyebrow">YOUR WORKSPACE</div><h2>Research overview</h2><p>A live snapshot of jobs saved by your backend.</p></div><button className="secondary small" onClick={load} disabled={loading}><RefreshCw size={14} className={loading ? "spin" : ""} /> Refresh data</button></div>
    <section className="stats">
      {[[BriefcaseBusiness, "Research jobs", stats.total, "All submitted analyses", "blue"], [CheckCircle2, "Completed reports", stats.done, "Successfully generated", "green"], [Clock3, "In progress", stats.active, "Pending or processing", "amber"], [Activity, "Failed jobs", stats.failed, "Need review", "rose"]].map(([Icon, label, value, hint, tone]) => <article className="stat" key={label}><div className={`stat-top ${tone}`}><Icon size={17} /><span>{label}</span><ArrowUpRight size={14} /></div><strong>{loading ? "—" : value}</strong><p>{hint}</p></article>)}
    </section>

    <div className="dashboard-grid">
      <section className="panel recent-panel"><div className="panel-head"><div><div className="eyebrow muted-eyebrow">LATEST ACTIVITY</div><h3>Recent research</h3><p>Your latest company analyses and their status.</p></div><Link className="text-link" to="/history">Research library <ArrowUpRight size={15} /></Link></div>
        {loading ? <div className="loading"><span className="loader" />Loading research activity…</div> : error ? <div className="connection-error"><div className="error-icon"><Database size={18} /></div><div><b>Research history isn't connected yet</b><p>{error}</p><small>Once the history endpoint is aligned, your saved reports will appear here.</small></div></div> : jobs.length === 0 ? <EmptyState title="Your research starts here" description="Submit a company to create your first multi-agent research report." /> : <div className="table-scroll"><table><thead><tr><th>Company</th><th>Symbol</th><th>Status</th><th>Created</th><th /></tr></thead><tbody>{jobs.slice(0, 6).map(j => <tr key={j.research_id || j.id}><td><b>{j.company || "Unnamed company"}</b><small className="mono">{j.research_id || j.id}</small></td><td className="mono ticker-cell">{j.ticker || "—"}</td><td><StatusBadge status={j.status} /></td><td>{formatDateTime(j.created_at)}</td><td><Link className="row-link" to={`/research/${j.research_id || j.id}`} aria-label="Open report"><ArrowUpRight size={16} /></Link></td></tr>)}</tbody></table></div>}
        {!loading && !error && jobs.length > 0 && <div className="panel-bottom"><span>Showing {Math.min(jobs.length, 6)} of {jobs.length} saved jobs</span><Link to="/history">View complete history <ArrowRight size={13} /></Link></div>}
      </section>
      <section className="panel workflow-panel"><div className="panel-head"><div><div className="eyebrow muted-eyebrow">HOW IT WORKS</div><h3>One coordinated crew</h3><p>Specialists contribute distinct perspectives.</p></div><span className="agent-count">06 AGENTS</span></div><div className="workflow-list">{agents.map(([n, name, desc, Icon], i) => <div className="workflow-agent" key={n}><div className="workflow-icon"><Icon size={16} /></div><div className="workflow-copy"><b>{name}</b><small>{desc}</small></div><span className="agent-index">{n}</span>{i !== agents.length - 1 && <i className="workflow-line" />}</div>)}</div></section>
    </div>

    <section className="insight-strip"><div className="insight-icon"><TrendingUp size={19} /></div><div><b>Evidence before conclusions</b><p>Market charts and financial indicators should be populated from verified backend data—not illustrative numbers. Connect the relevant data endpoints to unlock live visualizations.</p></div><Link to="/settings" className="text-link">Workspace setup <ArrowUpRight size={14} /></Link></section>
    <section className="bottom-cta"><div className="cta-mark"><Sparkles size={20} /></div><div><b>Ready to investigate a company?</b><p>Start a new analysis and let your six-agent crew build the research picture.</p></div><Link to="/new-research" className="secondary">Start research <ArrowRight size={15} /></Link></section>
  </div>;
}
