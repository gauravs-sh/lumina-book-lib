import { FormEvent, useState } from "react";
import { apiRequest } from "../api/client";

interface AnswerResponse {
  answer: string;
  excerpts: string[];
}

export default function Qa() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<AnswerResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await apiRequest<AnswerResponse>("/qa", {
        method: "POST",
        body: JSON.stringify({ question }),
      });
      setAnswer(response);
    } catch (err) {
      setError((err as Error).message);
      setAnswer(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <h2>Q&A</h2>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Question
          <textarea value={question} onChange={(e) => setQuestion(e.target.value)} rows={3} required />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? "Asking..." : "Ask"}
        </button>
      </form>
      {answer && (
        <div className="card-sub">
          <h3>Answer</h3>
          <p>{answer.answer}</p>
          <h4>Relevant Excerpts</h4>
          <ul>
            {answer.excerpts.map((excerpt, index) => (
              <li key={index}>{excerpt.slice(0, 200)}...</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}
