export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="error-box" role="alert">
      <strong>No se pudieron cargar los exámenes</strong>
      <p>{message}</p>
      <button type="button" onClick={onRetry}>
        Reintentar
      </button>
    </div>
  );
}
