import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import Qa from "../pages/Qa";
import { AuthProvider } from "../components/AuthProvider";

beforeEach(() => {
  globalThis.fetch = jest.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ answer: "ok", excerpts: [] }),
    status: 200,
  }) as unknown as typeof fetch;
});

afterEach(() => {
  jest.restoreAllMocks();
});

it("renders qa page", () => {
  render(
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <Qa />
      </AuthProvider>
    </BrowserRouter>
  );

  expect(screen.getByText(/Q&A/i)).toBeInTheDocument();
});
