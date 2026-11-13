import { useState } from "react";
import ExamFormPage from "./components/ExamFormPage";
import ExamListPage from "./components/ExamListPage";

// Two pages, no router needed: "list" and "form".
export default function App() {
  const [page, setPage] = useState("list");
  return (
    <main className="app">
      <header>
        <h1>Cuestionarios</h1>
        <p className="muted">React + Axios consumiendo la API del laboratorio 8</p>
      </header>
      {page === "list" ? (
        <ExamListPage onNew={() => setPage("form")} />
      ) : (
        <ExamFormPage onDone={() => setPage("list")} />
      )}
    </main>
  );
}
