import { useCallback, useEffect, useState } from "react";
import { apiRequest } from "../api/client";

interface DocumentItem {
  id: number;
  filename: string;
}

interface IngestionJob {
  id: number;
  document_id: number;
  status: string;
  error?: string | null;
}

export default function Ingestion() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [jobs, setJobs] = useState<IngestionJob[]>([]);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [docs, jobList] = await Promise.all([
        apiRequest<DocumentItem[]>("/documents"),
        apiRequest<IngestionJob[]>("/ingestion/jobs"),
      ]);
      setDocuments(docs);
      setJobs(jobList);
    } catch (err) {
      setError((err as Error).message);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const hasActiveJobs = jobs.some((job) => job.status === "pending" || job.status === "running");

  useEffect(() => {
    if (!hasActiveJobs) {
      return;
    }

    const intervalId = window.setInterval(() => {
      void loadData();
    }, 3000);

    return () => window.clearInterval(intervalId);
  }, [hasActiveJobs, loadData]);

  const startIngestion = async (documentId: number) => {
    setError(null);
    try {
      await apiRequest(`/ingestion/${documentId}`, { method: "POST" });
      await loadData();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <section className="card">
      <h2>Ingestion</h2>
      {error && <p className="error">{error}</p>}
      <div className="list">
        {documents.map((doc) => (
          <article key={doc.id} className="list-item">
            <div>
              <h3>{doc.filename}</h3>
              <p className="muted">Document ID: {doc.id}</p>
            </div>
            <button onClick={() => startIngestion(doc.id)}>Ingest</button>
          </article>
        ))}
      </div>
      <h3>Jobs</h3>
      <div className="list">
        {jobs.map((job) => (
          <article key={job.id} className="list-item">
            <div>
              <p>
                Job #{job.id} • Document {job.document_id}
              </p>
              <p className="muted">Status: {job.status}</p>
              {job.error && <p className="error">{job.error}</p>}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
