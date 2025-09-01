async function getLeagues() {
  const res = await fetch(process.env.NEXT_PUBLIC_API_BASE + "/yahoo/leagues", { cache: 'no-store' });
  return res.json();
}
export default async function Leagues() {
  const data = await getLeagues();
  return <pre>{JSON.stringify(data, null, 2)}</pre>;
}
