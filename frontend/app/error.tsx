"use client";

export default function GlobalError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="card">
      <h2>Something went wrong</h2>
      <p className="error">{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
