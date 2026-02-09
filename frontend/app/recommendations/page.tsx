"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { api } from "../../lib/api";
import { useAuth } from "../../components/AuthProvider";
import { useToast } from "../../components/ToastProvider";
 
interface Book {
  id: number;
  title: string;
  author: string;
  genre: string;
  year_published: number;
}

export default function RecommendationsPage() {
  const { token } = useAuth();
  const [books, setBooks] = useState<Book[]>([]);
  const { showToast } = useToast();

  const loadRecommendations = useCallback(async () => {
    if (!token) {
      return;
    }
    try {
      const data = (await api.recommendations()) as Book[];
      setBooks(data);
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  }, [token, showToast]);

  useEffect(() => {
    void loadRecommendations();
  }, [loadRecommendations]);

  if (!token) {
    return (
      <section className="card">
        <h2>Recommendations</h2>
        <p className="muted">Please log in to view recommendations.</p>
        <Link href="/login">Go to Login</Link>
      </section>
    );
  }

  return (
    <section className="card">
      <h2>Recommendations</h2>
      <div className="list">
        {books.map((book) => (
          <article key={book.id} className="list-item">
            <div>
              <h3>{book.title}</h3>
              <p>
                {book.author} • {book.genre} • {book.year_published}
              </p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
