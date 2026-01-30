import { FormEvent, useEffect, useState } from "react";
import { apiRequest } from "../api/client";

interface Book {
  id: number;
  title: string;
  author: string;
  genre: string;
  year_published: number;
  summary?: string;
}

export default function Books() {
  const [books, setBooks] = useState<Book[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    title: "",
    author: "",
    genre: "",
    year_published: 2024,
  });

  const loadBooks = async () => {
    try {
      const data = await apiRequest<Book[]>("/books");
      setBooks(data);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  useEffect(() => {
    void loadBooks();
  }, []);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      await apiRequest("/books", {
        method: "POST",
        body: JSON.stringify(form),
      });
      setForm({ title: "", author: "", genre: "", year_published: 2024 });
      await loadBooks();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await apiRequest(`/books/${id}`, { method: "DELETE" });
      await loadBooks();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <section className="card">
      <h2>Books</h2>
      <form onSubmit={handleSubmit} className="form">
        <label>
          Title
          <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required />
        </label>
        <label>
          Author
          <input value={form.author} onChange={(e) => setForm({ ...form, author: e.target.value })} required />
        </label>
        <label>
          Genre
          <input value={form.genre} onChange={(e) => setForm({ ...form, genre: e.target.value })} required />
        </label>
        <label>
          Year
          <input
            type="number"
            value={form.year_published}
            onChange={(e) => setForm({ ...form, year_published: Number(e.target.value) })}
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit">Add Book</button>
      </form>
      <div className="list">
        {books.map((book) => (
          <article key={book.id} className="list-item">
            <div>
              <h3>{book.title}</h3>
              <p>
                {book.author} • {book.genre} • {book.year_published}
              </p>
              {book.summary && <p className="muted">Summary: {book.summary}</p>}
            </div>
            <button onClick={() => handleDelete(book.id)}>Delete</button>
          </article>
        ))}
      </div>
    </section>
  );
}
