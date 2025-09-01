import Link from "next/link";

export default function Nav() {
  return (
    <nav className="flex items-center justify-between py-4">
      <Link href="/" className="font-bold">
        Fantasy Edge
      </Link>
      <div className="space-x-4">
        <Link href="/leagues" className="underline">
          Leagues
        </Link>
        <Link href="/login" className="underline">
          Login
        </Link>
      </div>
    </nav>
  );
}
