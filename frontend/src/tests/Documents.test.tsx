import { render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import Documents from "../pages/Documents";
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

it("renders documents page", async () => {
  render(
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <Documents />
      </AuthProvider>
    </BrowserRouter>
  );

  await waitFor(() => expect(globalThis.fetch).toHaveBeenCalled());
  expect(screen.getByText(/Documents/i)).toBeInTheDocument();
});
