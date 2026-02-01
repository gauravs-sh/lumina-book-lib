import "../styles/globals.css";
import { ReactNode } from "react";
import AppHeader from "../components/AppHeader";
import { AuthProvider } from "../components/AuthProvider";
import { ToastProvider } from "../components/ToastProvider";

export const metadata = {
  title: "LuminaLib",
  description: "Intelligent Library System",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <ToastProvider>
            <div className="app">
              <AppHeader />
              <main className="app-content">{children}</main>
            </div>
          </ToastProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
