import { render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import Books from "../pages/Books";
import { AuthProvider } from "../components/AuthProvider";

beforeEach(() => {
  globalThis.fetch = jest.fn().mockResolvedValue({
    ok: true,
    json: async () => [],
    status: 200,
  }) as unknown as typeof fetch;
});

afterEach(() => {
  jest.restoreAllMocks();
});

it("renders books page", async () => {
  render(
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <Books />
      </AuthProvider>
    </BrowserRouter>
  );

  await waitFor(() => expect(globalThis.fetch).toHaveBeenCalled());
  expect(screen.getByText(/Books/i)).toBeInTheDocument();
});
