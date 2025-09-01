import { apiFetch } from "../../lib/api";

async function getLeagues() {
  return apiFetch<any>("/yahoo/leagues", { cache: "no-store" });
}

export default async function Leagues() {
  const data = await getLeagues();
  return <pre>{JSON.stringify(data, null, 2)}</pre>;
}
