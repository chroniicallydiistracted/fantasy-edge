import Link from "next/link";
export default function Home() {
  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Fantasy Edge</h1>
      <Link className="underline" href="/leagues">Go to Leagues</Link>
    </div>
  );
}
