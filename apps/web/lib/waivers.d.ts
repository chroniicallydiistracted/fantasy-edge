// apps/web/lib/waivers.d.ts
// Type shim for the JS module `lib/waivers.js` so TS/Next can compile.

export type WaiverRow = {
  player_id: string | number;
  name: string;
  delta_xfp: number;
  order: number;
  // allow extra fields without type errors
  [key: string]: unknown;
};

export declare function mapWaivers(input: unknown[]): WaiverRow[];