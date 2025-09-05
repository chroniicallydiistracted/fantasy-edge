import { API_BASE } from "./api";

export function subscribeToLive(
  leagueKey: string,
  week: number,
  onMessage: (ev: MessageEvent) => void
): () => void {
  let es: EventSource | null = null;
  let retry = 1000;

  const connect = () => {
    const url = `${API_BASE}/live/subscribe?league_key=${encodeURIComponent(
      leagueKey
    )}&week=${week}`;
    // withCredentials ensures cookies are sent cross-origin when CORS allows it
    es = new EventSource(url, { withCredentials: true } as any);
    es.onmessage = onMessage;
    es.onerror = () => {
      es?.close();
      setTimeout(connect, retry);
      retry = Math.min(retry * 2, 30000);
    };
  };

  connect();
  return () => es?.close();
}
