import { render, screen } from "@testing-library/react";
import AppHeader from "../components/AppHeader";
import { AuthProvider } from "../components/AuthProvider";

describe("AppHeader", () => {
  it("shows login links when signed out", () => {
    render(
      <AuthProvider>
        <AppHeader />
      </AuthProvider>
    );

    expect(screen.getByText(/Login/i)).toBeInTheDocument();
    expect(screen.getByText(/Sign Up/i)).toBeInTheDocument();
  });
});
