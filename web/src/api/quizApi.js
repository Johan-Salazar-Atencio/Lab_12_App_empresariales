// API client module: the base URL lives only here, so no component writes an address by hand.
import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api";
// Reads are public; writes (POST, DELETE) need the token of a person. It comes from .env.local (not in git).
const TOKEN = import.meta.env.VITE_QUIZ_TOKEN;

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 8000,
  headers: TOKEN ? { Authorization: `Token ${TOKEN}` } : {},
});

/** GET /exams/ -> array of exams. `signal` lets the caller cancel the request. */
export async function listExams({ signal } = {}) {
  const response = await client.get("/exams/", { params: { page_size: 50 }, signal });
  return response.data.results;
}

/** POST /exams/ with { title } -> the created exam. */
export async function createExam(title) {
  const response = await client.post("/exams/", { title });
  return response.data;
}

/** DELETE /exams/{id}/ -> nothing (204). */
export async function deleteExam(id) {
  await client.delete(`/exams/${id}/`);
}

export function isCancel(error) {
  return axios.isCancel(error);
}

/** Turns any axios error into a message the interface can show. */
export function describeError(error) {
  if (error.response) {
    const { status, data } = error.response;
    if (data && typeof data === "object") {
      const parts = Object.entries(data).map(([field, messages]) => {
        const text = Array.isArray(messages) ? messages.join(" ") : String(messages);
        return field === "detail" ? text : `${field}: ${text}`;
      });
      if (parts.length) return `La API respondió ${status}. ${parts.join(" | ")}`;
    }
    return `La API respondió ${status}.`;
  }
  if (error.request) {
    return `No hay respuesta de la API en ${BASE_URL}. El servidor está apagado o el navegador bloqueó la petición (CORS).`;
  }
  return error.message;
}
