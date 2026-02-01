import { render, screen } from "@testing-library/react";
import LoginPage from "../app/login/page";
import { AuthProvider } from "../components/AuthProvider";

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: jest.fn() }),
}));

jest.mock("../lib/api", () => ({
  api: {
    login: jest.fn(async () => ({ access_token: "token" })),
  },
}));

describe("LoginPage", () => {
  it("renders login form", () => {
    render(
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    );

    expect(screen.getByRole("heading", { name: /Login/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
  });
});
