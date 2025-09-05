import Link from "next/link";
import { API_BASE } from "../../lib/api";

export default function LoginPage() {
  return (
    <div className="flex h-screen items-center justify-center">
      <Link
        href={`${API_BASE}/auth/yahoo/login`}
        className="rounded bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700"
      >
        Sign in with Yahoo
      </Link>
    </div>
  );
}
