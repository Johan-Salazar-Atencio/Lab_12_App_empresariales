import { useCallback, useEffect, useState } from "react";
import { describeError, isCancel, listExams } from "../api/quizApi";

/** Loads the exams and exposes the three states of a request: loading, ready (data) and error. */
export default function useExams() {
  const [state, setState] = useState({ status: "loading", exams: [], error: null });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    setState((current) => ({ ...current, status: "loading", error: null }));
    listExams({ signal: controller.signal })
      .then((exams) => setState({ status: "ready", exams, error: null }))
      .catch((error) => {
        if (isCancel(error)) return;
        setState({ status: "error", exams: [], error: describeError(error) });
      });
    return () => controller.abort();
  }, [attempt]);

  // Refreshing (after delete, retry) repeats the effect.
  const reload = useCallback(() => setAttempt((n) => n + 1), []);

  return { ...state, reload };
}
