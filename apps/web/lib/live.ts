import { API_BASE } from "./api";

export function subscribeToLive(onMessage: (ev: MessageEvent) => void): () => void {
  const es = new EventSource(`${API_BASE}/live/subscribe`);
  es.onmessage = onMessage;
  return () => es.close();
}
