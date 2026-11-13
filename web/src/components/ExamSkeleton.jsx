export default function ExamSkeleton() {
  return (
    <div className="skeleton" role="status" aria-label="Cargando exámenes">
      {[0, 1, 2, 3].map((n) => (
        <div key={n} className="skeleton-row" />
      ))}
      <p className="muted">Cargando exámenes…</p>
    </div>
  );
}
