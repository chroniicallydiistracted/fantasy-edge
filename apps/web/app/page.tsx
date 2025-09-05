import Link from "next/link";
import { API_BASE } from "../lib/api";
export default function Home() {
  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Fantasy Edge</h1>
      <Link className="underline" href="/leagues">Go to Leagues</Link>
      <div className="mt-8">
        <Link
          href={`${API_BASE}/auth/yahoo/login`}
          className="inline-block rounded bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700"
        >
          Login with Yahoo
        </Link>
      </div>
    </div>
  );
}
