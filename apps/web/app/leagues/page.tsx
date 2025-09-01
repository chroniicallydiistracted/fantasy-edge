import LeaguesTable, { League } from "../../components/LeaguesTable";
import { apiFetch } from "../../lib/api";

async function getLeagues(): Promise<League[]> {
  const data = await apiFetch<any>("/yahoo/leagues", { cache: "no-store" });
  const raw = data.leagues ?? data.fantasy_content?.leagues ?? [];
  return raw.map((l: any) => ({
    league_id: l.league_id ?? l.league_key ?? l.id ?? "unknown",
    name: l.name ?? l.league_name ?? "Unnamed League",
  }));
}

export default async function Leagues() {
  const leagues = await getLeagues();
  return (
    <div>
      <h1 className="mb-4 text-xl font-bold">Leagues</h1>
      <LeaguesTable leagues={leagues} />
    </div>
  );
}
