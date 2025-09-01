"use client";

import { API_BASE } from "../../lib/api";

export default function LoginPage() {
  const handleLogin = () => {
    window.location.href = `${API_BASE}/auth/yahoo/login`;
  };

  return (
    <div className="flex h-screen items-center justify-center">
      <button
        onClick={handleLogin}
        className="rounded bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700"
      >
        Sign in with Yahoo
      </button>
    </div>
  );
}
