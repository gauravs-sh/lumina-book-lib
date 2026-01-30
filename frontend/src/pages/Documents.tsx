import { FormEvent, useEffect, useState } from "react";
import { apiRequest } from "../api/client";

interface DocumentItem {
  id: number;
  filename: string;
  content: string;
}

export default function Documents() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ filename: "", content: "" });

  const loadDocuments = async () => {
    try {
      const data = await apiRequest<DocumentItem[]>("/documents");
      setDocuments(data);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  useEffect(() => {
    void loadDocuments();
  }, []);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await apiRequest("/documents", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setForm({ filename: "", content: "" });
      await loadDocuments();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <section className="card">
      <h2>Documents</h2>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Filename
          <input value={form.filename} onChange={(e) => setForm({ ...form, filename: e.target.value })} required />
        </label>
        <label>
          Content
          <textarea
            rows={4}
            value={form.content}
            onChange={(e) => setForm({ ...form, content: e.target.value })}
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit">Save Document</button>
      </form>
      <div className="list">
        {documents.map((doc) => (
          <article key={doc.id} className="list-item">
            <div>
              <h3>{doc.filename}</h3>
              <p className="muted">{doc.content.slice(0, 120)}...</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
