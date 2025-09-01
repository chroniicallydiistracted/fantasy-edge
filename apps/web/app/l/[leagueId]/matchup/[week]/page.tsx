import { apiFetch } from "../../../../../lib/api";

async function getMatchups(leagueId: string, week: string) {
  const data = await apiFetch<any>(
    `/yahoo/league/${leagueId}/matchups?week=${week}`,
    { cache: "no-store" }
  );
  const raw = data.matchups ?? [];
  return raw.map((m: any) => {
    const teams = m.matchup?.teams ?? m.teams ?? [];
    const names = teams.map(
      (t: any) => t.team?.[0]?.name ?? t.name ?? "Unknown Team"
    );
    return { teams: names };
  });
}

export default async function MatchupPage({
  params,
}: {
  params: { leagueId: string; week: string };
}) {
  const matchups = await getMatchups(params.leagueId, params.week);
  return (
    <div>
      <h1 className="mb-4 text-xl font-bold">
        Week {params.week} Matchups
      </h1>
      <ul>
        {matchups.map((m, idx) => (
          <li key={idx}>{m.teams.join(" vs ")}</li>
        ))}
      </ul>
    </div>
  );
}
