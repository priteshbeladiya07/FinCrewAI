import { useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import Dashboard from "./pages/Dashboard";
import NewResearch from "./pages/NewResearch";
import ResearchHistory from "./pages/ResearchHistory";
import ResearchReport from "./pages/ResearchReport";
import Settings from "./pages/Settings";

export default function App() {
  const [mobile, setMobile] = useState(false);
  return <div className="app">
    <Sidebar open={mobile} onClose={() => setMobile(false)} />
    <div className="main">
      <Topbar onMenu={() => setMobile(!mobile)} />
      <main className="content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/new-research" element={<NewResearch />} />
          <Route path="/history" element={<ResearchHistory />} />
          <Route path="/research/:id" element={<ResearchReport />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <footer><b>FinCrew AI</b><span>Multi-Agent Financial Research Platform</span><span>Research responsibly · Not investment advice</span></footer>
      </main>
    </div>
  </div>;
}
