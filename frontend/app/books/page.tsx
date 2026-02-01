"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { api } from "../../lib/api";
import { useToast } from "../../components/ToastProvider";
import { useAuth } from "../../components/AuthProvider";

interface Book {
  id: number;
  title: string;
  author: string;
  genre: string;
  year_published: number;
  summary?: string | null;
  review_summary?: string | null;
  file_name?: string | null;
  content_type?: string | null;
  file_size?: number | null;
}

interface BookListResponse {
  items: Book[];
  page: number;
  size: number;
  total: number;
}

type BorrowStatus = "Available" | "Borrowed" | "Returned";

interface BorrowInfo {
  status: BorrowStatus;
  borrowed_at?: string | null;
  returned_at?: string | null;
}

export default function BooksPage() {
  const { token } = useAuth();
  const [books, setBooks] = useState<Book[]>([]);
  const [page, setPage] = useState(1);
  const [size] = useState(10);
  const [total, setTotal] = useState(0);
  const { showToast } = useToast();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const [pendingSummaryIds, setPendingSummaryIds] = useState<Record<number, boolean>>({});
  const [form, setForm] = useState({ title: "", author: "", genre: "", year_published: 2024 });
  const [file, setFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<Record<number, string>>({});
  const [highlightedAnalysisId, setHighlightedAnalysisId] = useState<number | null>(null);
  const [reviewText, setReviewText] = useState<Record<number, string>>({});
  const [reviewRating, setReviewRating] = useState<Record<number, number>>({});
  const [reviewAvailability, setReviewAvailability] = useState<Record<number, boolean>>({});
  const [borrowStatus, setBorrowStatus] = useState<Record<number, BorrowInfo>>({});

  const formatTimestamp = (value?: string | null) => {
    if (!value) return null;
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return value;
    return parsed.toLocaleString();
  };

  const loadBooks = useCallback(async () => {
    try {
      const response = (await api.listBooks(page, size)) as BookListResponse;
      setBooks(response.items);
      setTotal(response.total);
      setPendingSummaryIds((prev) => {
        const next = { ...prev };
        response.items.forEach((book) => {
          if (book.summary) {
            delete next[book.id];
          }
        });
        return next;
      });
      if (response.items.length) {
        const entries = await Promise.all(
          response.items.map(async (book) => {
            const [reviews, status] = await Promise.all([
              api.listReviews(book.id).catch(() => [] as Array<unknown>),
              api.getBorrowStatus(book.id).catch(() => ({ status: "Available" })),
            ]);
            return [book.id, { reviews, status }] as const;
          })
        );
        const availability: Record<number, boolean> = {};
        const statusMap: Record<number, BorrowInfo> = {};
        entries.forEach(([bookId, result]) => {
          availability[bookId] = (result.reviews as Array<unknown>).length > 0;
          const status = result.status as BorrowInfo;
          statusMap[bookId] = {
            status: (status.status as BorrowStatus) || "Available",
            borrowed_at: status.borrowed_at,
            returned_at: status.returned_at,
          };
        });
        setReviewAvailability(availability);
        setBorrowStatus((prev) => ({ ...prev, ...statusMap }));
      }
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  }, [page, size, showToast]);

  useEffect(() => {
    void loadBooks();
  }, [loadBooks]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      if (editingBook) {
        await api.updateBook(editingBook.id, {
          title: form.title,
          author: form.author,
          genre: form.genre,
          year_published: form.year_published,
          file,
        });
        showToast("Book updated.", "success");
      } else {
        if (!file) {
          showToast("Please select a file.", "error");
          return;
        }
        const data = new FormData();
        data.append("title", form.title);
        data.append("author", form.author);
        data.append("genre", form.genre);
        data.append("year_published", String(form.year_published));
        data.append("file", file);
        const created = (await api.createBook(data)) as Book;
        if (created?.id) {
          setPendingSummaryIds((prev) => ({ ...prev, [created.id]: true }));
        }
        showToast("Book created.", "success");
      }

      setForm({ title: "", author: "", genre: "", year_published: 2024 });
      setFile(null);
      setEditingBook(null);
      setIsModalOpen(false);
      await loadBooks();
      window.setTimeout(() => {
        void loadBooks();
      }, 1500);
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

  const openCreateModal = () => {
    setEditingBook(null);
    setForm({ title: "", author: "", genre: "", year_published: 2024 });
    setFile(null);
    setIsModalOpen(true);
  };

  const openEditModal = (book: Book) => {
    setEditingBook(book);
    setForm({
      title: book.title,
      author: book.author,
      genre: book.genre,
      year_published: book.year_published,
    });
    setFile(null);
    setIsModalOpen(true);
  };

  const handleBorrow = async (bookId: number) => {
    try {
      const borrow = (await api.borrowBook(bookId)) as { borrowed_at?: string; returned_at?: string | null };
      showToast("Book borrowed.", "success");
      setBorrowStatus((prev) => ({
        ...prev,
        [bookId]: { status: "Borrowed", borrowed_at: borrow.borrowed_at, returned_at: borrow.returned_at ?? null },
      }));
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

  const handleReturn = async (bookId: number) => {
    try {
      const borrow = (await api.returnBook(bookId)) as { borrowed_at?: string; returned_at?: string | null };
      showToast("Book returned.", "success");
      setBorrowStatus((prev) => ({
        ...prev,
        [bookId]: { status: "Returned", borrowed_at: borrow.borrowed_at, returned_at: borrow.returned_at ?? null },
      }));
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

  const handleReview = async (bookId: number) => {
    try {
      await api.addReview(bookId, reviewText[bookId] || "", reviewRating[bookId] || 5);
      showToast("Review submitted.", "success");
      setReviewAvailability((prev) => ({ ...prev, [bookId]: true }));
      await loadBooks();
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

  const loadAnalysis = async (bookId: number) => {
    try {
      const result = (await api.bookAnalysis(bookId)) as { review_summary?: string };
      setAnalysis((prev) => ({ ...prev, [bookId]: result.review_summary || "No analysis yet." }));
      setHighlightedAnalysisId(bookId);
      window.setTimeout(() => {
        setHighlightedAnalysisId((current) => (current === bookId ? null : current));
      }, 1200);
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

  const handleDeleteBook = async (bookId: number) => {
    if (!window.confirm("Delete this book and all associated data?")) {
      return;
    }
    try {
      await api.deleteBook(bookId);
      showToast("Book deleted.", "success");
      setReviewAvailability((prev) => {
        const next = { ...prev };
        delete next[bookId];
        return next;
      });
      setBorrowStatus((prev) => {
        const next = { ...prev };
        delete next[bookId];
        return next;
      });
      await loadBooks();
    } catch (err) {
      showToast((err as Error).message, "error");
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / size));
  if (!token) {
    return (
      <section className="card">
        <h2>Books</h2>
        <p className="muted">Please log in to view books.</p>
        <Link href="/login">Go to Login</Link>
      </section>
    );
  }

  return (
    <section className="card">
      <div className="page-header">
        <h2>Books</h2>
        <button type="button" onClick={openCreateModal}>
          Add new book
        </button>
      </div>
      <div className="list">
        {books.map((book) => (
          <article key={book.id} className="list-item">
            <div>
              <div className="list-item-header">
                <h3>{book.title}</h3>
                <span className="status-tags">
                  {borrowStatus[book.id]?.status === "Returned" ? (
                    <>
                      <span
                        className="status-tag status-returned"
                        title={formatTimestamp(borrowStatus[book.id]?.returned_at) || undefined}
                      >
                        <span className="status-icon" aria-hidden="true">
                          ✅
                        </span>
                        Returned
                      </span>
                      <span className="status-tag status-available">
                        <span className="status-icon" aria-hidden="true">
                          📘
                        </span>
                        Available
                      </span>
                    </>
                  ) : borrowStatus[book.id]?.status === "Borrowed" ? (
                    <span
                      className="status-tag status-borrowed"
                      title={formatTimestamp(borrowStatus[book.id]?.borrowed_at) || undefined}
                    >
                      <span className="status-icon" aria-hidden="true">
                        📕
                      </span>
                      Borrowed
                    </span>
                  ) : (
                    <span className="status-tag status-available">
                      <span className="status-icon" aria-hidden="true">
                        📘
                      </span>
                      Available
                    </span>
                  )}
                </span>
              </div>
              <p>
                {book.author} • {book.genre} • {book.year_published}
              </p>
              {book.summary && <p className="muted">Summary: {book.summary}</p>}
              {analysis[book.id] && (
                <p className={`muted analysis ${highlightedAnalysisId === book.id ? "analysis-highlight" : ""}`}>
                  Review Analysis: {analysis[book.id]}
                </p>
              )}
            </div>
            <div className="actions">
              <div className="button-row">
                {borrowStatus[book.id]?.status === "Borrowed" ? (
                  <button onClick={() => handleReturn(book.id)}>Return</button>
                ) : (
                  <button onClick={() => handleBorrow(book.id)}>Borrow</button>
                )}
                {reviewAvailability[book.id] && <button onClick={() => loadAnalysis(book.id)}>Load Analysis</button>}
                {book.file_name && <button onClick={() => openEditModal(book)}>Edit</button>}
                <button onClick={() => handleDeleteBook(book.id)}>Delete</button>
              </div>
            </div>
            <div className="form-inline">
              <input
                placeholder="Review"
                value={reviewText[book.id] || ""}
                onChange={(e) =>
                  setReviewText((prev) => ({
                    ...prev,
                    [book.id]: e.target.value,
                  }))
                }
              />
              <input
                type="number"
                min={1}
                max={5}
                value={reviewRating[book.id] || 5}
                onChange={(e) =>
                  setReviewRating((prev) => ({
                    ...prev,
                    [book.id]: Number(e.target.value),
                  }))
                }
              />
              <button onClick={() => handleReview(book.id)}>Submit Review</button>
            </div>
          </article>
        ))}
      </div>
      <div className="pagination">
        <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>
          Prev
        </button>
        <span>
          Page {page} of {totalPages}
        </span>
        <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page >= totalPages}>
          Next
        </button>
      </div>
      {isModalOpen && (
        <div className="modal-backdrop" role="dialog" aria-modal="true">
          <div className="modal-card">
            <div className="modal-header">
              <h3>{editingBook ? "Edit book" : "Add new book"}</h3>
              <button type="button" className="link-button" onClick={() => setIsModalOpen(false)}>
                Close
              </button>
            </div>
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
              <label>
                Book File (PDF or text)
                <input
                  type="file"
                  accept=".pdf,.txt"
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                  required={!editingBook}
                />
              </label>
              {editingBook?.file_name && (
                <p className="muted">Current file: {editingBook.file_name}</p>
              )}
              <div className="modal-actions">
                <button type="button" className="link-button" onClick={() => setIsModalOpen(false)}>
                  Cancel
                </button>
                <button type="submit">{editingBook ? "Update" : "Save"}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}
