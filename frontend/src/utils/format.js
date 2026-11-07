
export const formatDateTime = (v) => {
  if (!v) return "—";

  const d = new Date(v);

  return Number.isNaN(d.getTime())
    ? String(v)
    : new Intl.DateTimeFormat("en-IN", {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit"
      }).format(d);
};

export const tone = (s = "") => {
  const status = String(s).toLowerCase();

  return ["completed", "success"].includes(status)
    ? "success"
    : ["failed", "error"].includes(status)
      ? "danger"
      : ["processing", "running", "pending"].includes(status)
        ? "warning"
        : "neutral";
};

export const titleCase = (s = "") =>
  String(s)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
