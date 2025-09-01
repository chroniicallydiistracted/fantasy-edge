import { apiFetch } from "../../../../../lib/api";
import { mapWaivers } from "../../../../../lib/waivers";

async function getWaivers(teamId: string, week: string) {
  const data = await apiFetch<any>(
    `/team/${teamId}/waivers?week=${week}&horizon=2`,
    { cache: "no-store" }
  );
  return mapWaivers(data.waivers ?? []);
}

export default async function WaiversPage({
  params,
  searchParams,
}: {
  params: { leagueId: string; week: string };
  searchParams: { teamId?: string };
}) {
  const teamId = searchParams.teamId;
  if (!teamId) {
    return <div>teamId query param required</div>;
  }
  const waivers = await getWaivers(teamId, params.week);
  return (
    <div>
      <h1 className="mb-4 text-xl font-bold">Week {params.week} Waivers</h1>
      <ul>
        {waivers.map((w) => (
          <li key={w.player_id}>
            {w.order}. {w.name} ({w.delta_xfp})
          </li>
        ))}
      </ul>
    </div>
  );
}
