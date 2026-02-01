import { getToken, setToken } from "./auth";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (response.status === 401) {
    setToken(null);
  }
  if (!response.ok) {
    const errorBody = await response
      .json()
      .catch(() => ({ error_message: "Request failed", detail: "Request failed" }));
    const message =
      errorBody.error_message ||
      errorBody.detail ||
      (errorBody.data && errorBody.data.error_message) ||
      "Request failed";
    throw new Error(message);
  }
  if (response.status === 204) {
    return {} as T;
  }
  const payload = await response.json();
  if (payload && typeof payload === "object" && "data" in payload && "status" in payload) {
    const statusValue = (payload as { status: number | string }).status;
    const errorMessage = (payload as { error_message?: string }).error_message;
    const isErrorStatus =
      typeof statusValue === "number" ? statusValue >= 400 : String(statusValue).toLowerCase() === "error";
    if (errorMessage || isErrorStatus) {
      throw new Error(errorMessage || "Request failed");
    }
    return (payload as { data: T }).data;
  }
  if (payload && typeof payload === "object" && "data" in payload) {
    return (payload as { data: T }).data;
  }
  return payload as T;
}

export const api = {
  signup: (email: string, password: string) =>
    request("/auth/signup", { method: "POST", body: JSON.stringify({ email, password, role: "user" }) }),
  login: (email: string, password: string) =>
    request<{ access_token: string }>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  profile: () => request("/auth/profile"),
  updateProfile: (payload: { email?: string; password?: string }) =>
    request("/auth/profile", { method: "PUT", body: JSON.stringify(payload) }),
  logout: () => request("/auth/logout", { method: "POST" }),
  listBooks: (page = 1, size = 10) => request(`/books?page=${page}&size=${size}`),
  createBook: (payload: FormData) => request("/books", { method: "POST", body: payload }),
  updateBook: (
    bookId: number,
    payload: { title: string; author: string; genre: string; year_published: number; file?: File | null }
  ) => {
    if (payload.file) {
      const data = new FormData();
      data.append("title", payload.title);
      data.append("author", payload.author);
      data.append("genre", payload.genre);
      data.append("year_published", String(payload.year_published));
      data.append("file", payload.file);
      return request(`/books/${bookId}`, { method: "PUT", body: data });
    }
    const { file, ...rest } = payload;
    return request(`/books/${bookId}`, { method: "PUT", body: JSON.stringify(rest) });
  },
  deleteBook: (bookId: number) => request(`/books/${bookId}`, { method: "DELETE" }),
  deleteBookFile: (bookId: number) => request(`/books/${bookId}/file`, { method: "DELETE" }),
  borrowBook: (bookId: number) => request(`/books/${bookId}/borrow`, { method: "POST" }),
  returnBook: (bookId: number) => request(`/books/${bookId}/return`, { method: "POST" }),
  getBorrowStatus: (bookId: number) => request(`/books/${bookId}/borrow-status`),
  listReviews: (bookId: number) => request(`/books/${bookId}/reviews`),
  addReview: (bookId: number, review_text: string, rating: number) =>
    request(`/books/${bookId}/reviews`, { method: "POST", body: JSON.stringify({ review_text, rating }) }),
  bookAnalysis: (bookId: number) => request(`/books/${bookId}/analysis`),
  recommendations: () => request("/recommendations"),
  getPreferences: () => request("/users/me/preferences"),
  updatePreferences: (preferences: Record<string, unknown>) =>
    request("/users/me/preferences", { method: "PUT", body: JSON.stringify({ preferences }) }),
};
