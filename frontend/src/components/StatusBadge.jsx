
import { tone, titleCase } from "../utils/format";

export default function StatusBadge({ status }) {
  return (
    <span className={`badge ${tone(status)}`}>
      <i />
      {titleCase(status || "pending")}
    </span>
  );
}
