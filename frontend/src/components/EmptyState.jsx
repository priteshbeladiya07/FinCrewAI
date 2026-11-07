
import { FileSearch } from "lucide-react";

export default function EmptyState({
  title = "Nothing here yet",
  description = "Your saved research will appear here."
}) {
  return (
    <div className="empty">
      <FileSearch size={27} />

      <h3>{title}</h3>

      <p>{description}</p>
    </div>
  );
}
