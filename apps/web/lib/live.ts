import { API_BASE } from "./api";

export function subscribeToLive(onMessage: (ev: MessageEvent) => void): () => void {
  let es: EventSource | null = null;
  let retry = 1000;

  const connect = () => {
    es = new EventSource(`${API_BASE}/live/subscribe`);
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
