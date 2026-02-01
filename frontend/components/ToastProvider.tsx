"use client";

import { createContext, ReactNode, useContext, useMemo, useState } from "react";

type ToastType = "success" | "error";

interface ToastContextValue {
  showToast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toast, setToast] = useState<{ message: string; type: ToastType } | null>(null);

  const showToast = (text: string, type: ToastType = "error") => {
    setToast({ message: text, type });
    window.setTimeout(() => {
      setToast(null);
    }, 1000);
  };

  const value = useMemo(() => ({ showToast }), []);

  return (
    <ToastContext.Provider value={value}>
      {children}
      {toast && (
        <div className={`toast toast-${toast.type}`}>
          <span className="toast-icon" aria-hidden="true">
            {toast.type === "success" ? "✔" : "⚠"}
          </span>
          <span>{toast.message}</span>
        </div>
      )}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) {
    throw new Error("useToast must be used within ToastProvider");
  }
  return ctx;
}
