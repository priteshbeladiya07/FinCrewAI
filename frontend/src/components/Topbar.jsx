import { Menu, Bell, ChevronRight, Command } from "lucide-react";
import { useLocation, Link } from "react-router-dom";

const names = {
  "/": ["Overview", "Your financial research command center"],
  "/new-research": ["New research", "Launch a coordinated company analysis"],
  "/history": ["Research library", "Explore and revisit previous analyses"],
  "/settings": ["Settings", "Manage your workspace connection"],
};

export default function Topbar({ onMenu }) {
  const loc = useLocation();
  const [title, sub] = names[loc.pathname] || ["Research report", "A consolidated view of your company research"];
  return <header className="topbar">
    <button className="menu-btn" onClick={onMenu} aria-label="Open navigation"><Menu size={20} /></button>
    <div className="top-heading"><div className="breadcrumb"><span>FINCREW AI</span><ChevronRight size={12} /><b>{title}</b></div><p>{sub}</p></div>
    <div className="top-actions"><span className="api-status"><i /> LOCAL WORKSPACE</span><Link to="/new-research" className="top-new"><Command size={14} /> New analysis</Link><div className="avatar">FC</div></div>
  </header>;
}
