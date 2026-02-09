import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import App from "../App";

it("renders navigation", () => {
  render(
    <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <App />
    </BrowserRouter>
  );
  expect(screen.getByText(/Smart QA Platform/i)).toBeInTheDocument();
});
