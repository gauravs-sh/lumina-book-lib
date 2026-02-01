"use client";

import Link from "next/link";
import { useAuth } from "./AuthProvider";
import { api } from "../lib/api";

export default function AppHeader() {
  const { token, email, logout } = useAuth();

  const handleLogout = async () => {
    try {
      await api.logout();
    } finally {
      logout();
    }
  };

  return (
    <header className="app-header">
      <h1>LuminaLib</h1>
      <nav>
        <Link href="/">Home</Link>
        {token ? (
          <>
            <Link href="/books">Books</Link>
            <Link href="/recommendations">Recommendations</Link>
            <Link href="/profile">Profile</Link>
            {email && <span className="header-user">{email}</span>}
            <button className="link-button" onClick={handleLogout}>
              Logout
            </button>
          </>
        ) : (
          <>
            <Link href="/login">Login</Link>
            <Link href="/signup">Sign Up</Link>
          </>
        )}
      </nav>
    </header>
  );
}
