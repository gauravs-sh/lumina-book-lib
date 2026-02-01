"use client";

import { FormEvent, useEffect, useState } from "react";
import { api } from "../../lib/api";
import { useToast } from "../../components/ToastProvider";

export default function ProfilePage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [preferences, setPreferences] = useState("{}");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const { showToast } = useToast();

  useEffect(() => {
    const load = async () => {
      try {
        const profile = (await api.profile()) as { email: string };
        setEmail(profile.email);
        const pref = (await api.getPreferences()) as { preferences: Record<string, unknown> };
        setPreferences(JSON.stringify(pref.preferences, null, 2));
      } catch (err) {
        showToast((err as Error).message, "error");
        setError((err as Error).message);
      }
    };
    void load();
  }, []);

  const handleProfileSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setMessage(null);
    try {
      await api.updateProfile({ email: email || undefined, password: password || undefined });
      setMessage("Profile updated.");
      showToast("Profile updated.", "success");
      setPassword("");
    } catch (err) {
      showToast((err as Error).message, "error");
      setError((err as Error).message);
    }
  };

  const handlePreferencesSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setMessage(null);
    try {
      const parsed = JSON.parse(preferences);
      await api.updatePreferences(parsed);
      setMessage("Preferences saved.");
      showToast("Preferences saved.", "success");
    } catch (err) {
      showToast((err as Error).message || "Invalid JSON", "error");
      setError((err as Error).message || "Invalid JSON");
    }
  };

  return (
    <section className="card">
      <h2>Profile</h2>
      <form onSubmit={handleProfileSubmit} className="form">
        <label>
          Email
          <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
        </label>
        <label>
          New Password
          <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" />
        </label>
        <button type="submit">Update Profile</button>
      </form>
      <h3>Preferences</h3>
      <form onSubmit={handlePreferencesSubmit} className="form">
        <label>
          JSON Preferences
          <textarea value={preferences} onChange={(e) => setPreferences(e.target.value)} rows={6} />
        </label>
        <button type="submit">Save Preferences</button>
      </form>
    </section>
  );
}
