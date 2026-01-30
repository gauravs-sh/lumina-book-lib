import { render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { BrowserRouter } from "react-router-dom";
import Books from "../pages/Books";
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

it("renders books page", async () => {
  render(
    <BrowserRouter>
      <AuthProvider>
        <Books />
      </AuthProvider>
    </BrowserRouter>
  );

  expect(screen.getByText(/Books/i)).toBeInTheDocument();
});
