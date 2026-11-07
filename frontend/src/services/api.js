
import axios from "axios";

const BASE =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

export const API_PATHS = {
  submitResearch: "/api/v1/research",

  status: (id) =>
    `/api/v1/research/${encodeURIComponent(id)}`,

  report: (id) =>
    `/api/v1/research/${encodeURIComponent(id)}/report`,

  history: "/api/v1/research/history",

  stockHistory: (ticker) =>
    `/api/v1/stocks/${encodeURIComponent(ticker)}/history`
};

export const api = axios.create({
  baseURL: BASE,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json"
  }
});

const unwrap = (d) =>
  d?.data && typeof d.data === "object"
    ? d.data
    : d;

export async function submitResearch(company, ticker = "") {
  const body = ticker.trim()
    ? {
        company: company.trim(),
        ticker: ticker.trim()
      }
    : {
        company: company.trim()
      };

  const { data } = await api.post(
    API_PATHS.submitResearch,
    body
  );

  const result = unwrap(data);

  return {
    ...result,
    research_id:
      result.research_id ||
      result.id ||
      result.job_id ||
      result.data?.research_id
  };
}

export async function getResearchStatus(id) {
  const { data } = await api.get(
    API_PATHS.status(id)
  );

  return unwrap(data);
}

export async function getResearchReport(id) {
  const { data } = await api.get(
    API_PATHS.report(id)
  );

  return unwrap(data);
}

export async function getResearchHistory() {
  const { data } = await api.get(
    API_PATHS.history
  );

  const d = unwrap(data);

  return Array.isArray(d)
    ? d
    : d.items ||
        d.results ||
        d.research_jobs ||
        d.history ||
        [];
}

export async function getStockHistory(
  ticker,
  period = "1y"
) {
  const { data } = await api.get(
    API_PATHS.stockHistory(ticker),
    {
      params: { period }
    }
  );

  const d = unwrap(data);

  return Array.isArray(d)
    ? d
    : d.history ||
        d.prices ||
        d.data ||
        [];
}

export function getApiError(e) {
  const detail = e?.response?.data?.detail;

  if (detail) {
    return typeof detail === "string"
      ? detail
      : JSON.stringify(detail);
  }

  if (!e?.response) {
    return "Cannot connect to FastAPI. Check that the backend is running and VITE_API_BASE_URL is correct.";
  }

  return e.message || "API request failed.";
}
