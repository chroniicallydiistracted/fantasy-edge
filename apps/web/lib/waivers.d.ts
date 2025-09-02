// apps/web/lib/waivers.d.ts
// Type shim for the JS module `lib/waivers.js` so TS/Next can compile.

export type WaiverRow = {
  // include the common fields your UI likely touches; extras are allowed
  id?: string | number;
  playerId?: string | number;
  name?: string;
  position?: string;
  team?: string;
  deltaXfp?: number;
  faabLow?: number;
  faabHigh?: number;
  acquireProb?: number;
  // allow any additional properties without type errors
  [key: string]: unknown;
};

export declare function mapWaivers(input: unknown): WaiverRow[];