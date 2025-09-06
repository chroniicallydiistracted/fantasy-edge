"use client";

import { useState } from "react";
import { apiFetch } from "../lib/api";

export default function YahooLoginButton({
  className = "rounded bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700",
  children = "Sign in with Yahoo",
}: {
  className?: string;
  children?: React.ReactNode;
}) {
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    if (loading) return;
    setLoading(true);
    try {
      const { redirect } = await apiFetch<{ redirect: string }>(
        "/auth/yahoo/login"
      );
      if (redirect && typeof window !== "undefined") {
        window.location.assign(redirect);
      }
    } catch (err) {
      // Basic fallback: stop loading so user can retry
      console.error("Failed to initiate Yahoo login:", err);
      setLoading(false);
    }
  };

  return (
    <button onClick={handleClick} disabled={loading} className={className}>
      {loading ? "Redirecting…" : children}
    </button>
  );
}

