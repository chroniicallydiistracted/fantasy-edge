import Link from "next/link";

export default function LoginPage() {
  return (
    <div className="flex h-screen items-center justify-center">
      <Link
        href="https://api.misfits.westfam.media/auth/yahoo/login"
        className="rounded bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700"
      >
        Sign in with Yahoo
      </Link>
    </div>
  );
}
