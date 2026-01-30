import { Link } from "react-router-dom";
import { useAuth } from "./AuthProvider";

export default function Layout({ children }: { children: React.ReactNode }) {
  const { token, email, logout } = useAuth();

  return (
    <div className="app">
      <header className="app-header">
        <h1>Smart QA Platform</h1>
        <nav>
          <Link to="/">Home</Link>
          <Link to="/books">Books</Link>
          <Link to="/documents">Documents</Link>
          <Link to="/ingestion">Ingestion</Link>
          <Link to="/qa">Q&A</Link>
          <Link to="/users">Users</Link>
          {!token ? (
            <>
              <Link to="/login">Login</Link>
              <Link to="/signup">Sign Up</Link>
            </>
          ) : (
            <>
              {email && <span className="header-user">Signed in as {email}</span>}
              <button className="link-button" onClick={logout}>
                Logout
              </button>
            </>
          )}
        </nav>
      </header>
      <main className="app-content">{children}</main>
    </div>
  );
}
