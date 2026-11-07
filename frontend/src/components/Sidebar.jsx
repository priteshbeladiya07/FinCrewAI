import { NavLink } from "react-router-dom";
import { Activity, LayoutDashboard, Search, Clock3, Settings2, Sparkles, X } from "lucide-react";

const items = [
  ["/", "Overview", LayoutDashboard],
  ["/new-research", "New research", Search],
  ["/history", "Research library", Clock3],
];

export default function Sidebar({ open = false, onClose = () => {} }) {
  return <>
    <button className={`scrim ${open ? "show" : ""}`} onClick={onClose} aria-label="Close navigation" />
    <aside className={`sidebar ${open ? "sidebar-open" : ""}`}>
      <div className="brand">
        <div className="brand-mark"><Activity size={21} /></div>
        <div className="brand-copy"><b>FinCrew <em>AI</em></b><small>INTELLIGENCE WORKSPACE</small></div>
        <button className="close-nav" onClick={onClose} aria-label="Close menu"><X size={18} /></button>
      </div>
      <div className="workspace-switch"><div className="workspace-avatar">F</div><div><b>Financial Research</b><small>Personal workspace</small></div><span className="switch-dots">•••</span></div>
      <div className="nav-caption">WORKSPACE</div>
      <nav>{items.map(([to, label, Icon]) => <NavLink key={to} to={to} end={to === "/"} onClick={onClose} className={({ isActive }) => isActive ? "nav active" : "nav"}><Icon size={17} /><span>{label}</span>{to === "/new-research" && <kbd>NEW</kbd>}</NavLink>)}</nav>
      <div className="nav-caption nav-caption-spaced">PREFERENCES</div>
      <NavLink to="/settings" onClick={onClose} className={({ isActive }) => isActive ? "nav active" : "nav"}><Settings2 size={17} /><span>Settings</span></NavLink>
      <div className="side-bottom">
        <div className="crew-box"><div className="crew-icon"><Sparkles size={17} /></div><div><b>Your AI research crew</b><small>6 specialist agents</small></div><span className="online-dot" /></div>
        <div className="side-foot"><Activity size={14} /> Research with a wider lens</div>
      </div>
    </aside>
  </>;
}
