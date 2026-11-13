import { useState } from "react";
import { deleteExam, describeError } from "../api/quizApi";
import useExams from "../hooks/useExams";
import ErrorMessage from "./ErrorMessage";
import ExamSkeleton from "./ExamSkeleton";
import ExamTable from "./ExamTable";

export default function ExamListPage({ onNew }) {
  const { status, exams, error, reload } = useExams();
  const [deletingId, setDeletingId] = useState(null);
  const [actionError, setActionError] = useState(null);

  async function handleDelete(exam) {
    setDeletingId(exam.id);
    setActionError(null);
    try {
      await deleteExam(exam.id);
      reload(); // refresh the list without reloading the page
    } catch (err) {
      setActionError(`No se pudo eliminar «${exam.title}». ${describeError(err)}`);
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <section>
      <div className="section-head">
        <h2>Exámenes</h2>
        <button type="button" onClick={onNew}>
          Nuevo examen
        </button>
      </div>
      {status === "loading" && <ExamSkeleton />}
      {status === "error" && <ErrorMessage message={error} onRetry={reload} />}
      {status === "ready" && (
        <ExamTable exams={exams} onDelete={handleDelete} deletingId={deletingId} actionError={actionError} />
      )}
    </section>
  );
}
