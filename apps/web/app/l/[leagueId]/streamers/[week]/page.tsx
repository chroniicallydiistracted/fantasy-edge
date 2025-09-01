import { apiFetch } from "../../../../../lib/api";

async function getStreamers(week: string) {
  const [def, idp] = await Promise.all([
    apiFetch<any[]>(`/streamers/def?week=${week}`, { cache: "no-store" }),
    apiFetch<any[]>(`/streamers/idp?week=${week}`, { cache: "no-store" }),
  ]);
  return { def, idp };
}

export default async function StreamersPage({
  params,
}: {
  params: { leagueId: string; week: string };
}) {
  const { def, idp } = await getStreamers(params.week);
  return (
    <div>
      <h1 className="mb-4 text-xl font-bold">Week {params.week} Streamers</h1>
      <section>
        <h2 className="mt-2 font-semibold">DEF Streamers</h2>
        <ul>
          {def.map((s) => (
            <li key={s.player_id}>
              {s.rank}. {s.name} ({s.projected_points})
            </li>
          ))}
        </ul>
      </section>
      <section className="mt-4">
        <h2 className="mt-2 font-semibold">IDP Streamers</h2>
        <ul>
          {idp.map((s) => (
            <li key={s.player_id}>
              {s.rank}. {s.name} ({s.projected_points})
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
