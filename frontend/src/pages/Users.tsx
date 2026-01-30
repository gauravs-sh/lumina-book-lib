import { useEffect, useState } from "react";
import { apiRequest } from "../api/client";

interface User {
  id: number;
  email: string;
  role: string;
}

export default function Users() {
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);

  const loadUsers = async () => {
    try {
      const data = await apiRequest<User[]>("/users");
      setUsers(data);
    } catch (err) {
      setError((err as Error).message);
    }
  };

  useEffect(() => {
    void loadUsers();
  }, []);

  return (
    <section className="card">
      <h2>User Management</h2>
      {error && <p className="error">{error}</p>}
      <div className="list">
        {users.map((user) => (
          <article key={user.id} className="list-item">
            <div>
              <p>{user.email}</p>
              <p className="muted">Role: {user.role}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
