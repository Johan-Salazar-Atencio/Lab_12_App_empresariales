import { useState } from "react";
import { createExam, describeError } from "../api/quizApi";

export default function ExamFormPage({ onDone }) {
  const [title, setTitle] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(event) {
    event.preventDefault(); // the browser must not submit the form by itself
    setSending(true);
    setError(null);
    try {
      await createExam(title);
      onDone(); // back to the list, which loads again
    } catch (err) {
      setError(describeError(err)); // shows the message the API returned
      setSending(false);
    }
  }

  return (
    <section>
      <h2>Nuevo examen</h2>
      <form onSubmit={handleSubmit} noValidate>
        <label htmlFor="title">Título del examen</label>
        <input id="title" value={title} onChange={(event) => setTitle(event.target.value)} />
        {error && (
          <p className="error-box" role="alert">
            {error}
          </p>
        )}
        <div className="actions">
          <button type="submit" disabled={sending}>
            {sending ? "Guardando…" : "Guardar"}
          </button>
          <button type="button" className="secondary" onClick={onDone}>
            Cancelar
          </button>
        </div>
      </form>
    </section>
  );
}
