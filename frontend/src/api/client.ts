const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000/api/v1";

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem("token");
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(errorBody.detail || "Request failed");
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}

export async function login(email: string, password: string): Promise<string> {
  const credentials = btoa(`${email}:${password}`);
  const response = await fetch(`${API_BASE}/auth/token`, {
    method: "POST",
    headers: {
      Authorization: `Basic ${credentials}`,
    },
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({ detail: "Invalid login" }));
    throw new Error(errorBody.detail || "Invalid login");
  }

  const data = await response.json();
  return data.access_token as string;
}
