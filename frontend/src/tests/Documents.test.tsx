import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { vi } from "vitest";
import Documents from "../pages/Documents";
import { AuthProvider } from "../components/AuthProvider";

beforeEach(() => {
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => [],
    status: 200,
  }) as unknown as typeof fetch;
});

afterEach(() => {
  vi.restoreAllMocks();
});

it("renders documents page", () => {
  render(
    <BrowserRouter>
      <AuthProvider>
        <Documents />
      </AuthProvider>
    </BrowserRouter>
  );

  expect(screen.getByText(/Documents/i)).toBeInTheDocument();
});
