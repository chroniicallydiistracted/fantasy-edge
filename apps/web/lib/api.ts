export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function apiFetch<T>(
  path: string,

  init: RequestInit = {}
): Promise<T> {
  let headers: HeadersInit | undefined = init.headers as any;
  // On the server, forward the incoming cookies to the API for auth
  if (typeof window === "undefined") {
    try {
      const mod = await import("next/headers");
      const cookieHeader = mod.cookies().toString();
      const h = new Headers(init.headers as any);
      if (cookieHeader) h.set("cookie", cookieHeader);
      headers = h;
    } catch {
      // ignore if not in a Next server context
    }
  }

  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers,
    ...init,
  });
  
  if (!res.ok) {
    throw new Error(`API request failed with status ${res.status}`);
  }
  return (await res.json()) as T;
}
