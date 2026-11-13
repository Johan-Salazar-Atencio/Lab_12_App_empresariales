export default function ExamTable({ exams, onDelete, deletingId, actionError }) {
  if (exams.length === 0) return <p className="muted">No hay exámenes todavía.</p>;
  return (
    <>
      {actionError && (
        <p className="error-box" role="alert">
          {actionError}
        </p>
      )}
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Título</th>
            <th>Preguntas</th>
            <th>Creado</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {exams.map((exam) => (
            <tr key={exam.id}>
              <td>{exam.id}</td>
              <td>{exam.title}</td>
              <td>{exam.question_count}</td>
              <td>{new Date(exam.created_at).toLocaleDateString("es-PE")}</td>
              <td>
                <button
                  type="button"
                  className="danger"
                  disabled={deletingId === exam.id}
                  onClick={() => onDelete(exam)}
                >
                  {deletingId === exam.id ? "Borrando…" : "Eliminar"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
