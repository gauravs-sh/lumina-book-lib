import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { vi } from "vitest";
import Qa from "../pages/Qa";
import { AuthProvider } from "../components/AuthProvider";

beforeEach(() => {
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ answer: "ok", excerpts: [] }),
    status: 200,
  }) as unknown as typeof fetch;
});

afterEach(() => {
  vi.restoreAllMocks();
});

it("renders qa page", () => {
  render(
    <BrowserRouter>
      <AuthProvider>
        <Qa />
      </AuthProvider>
    </BrowserRouter>
  );

  expect(screen.getByText(/Q&A/i)).toBeInTheDocument();
});
