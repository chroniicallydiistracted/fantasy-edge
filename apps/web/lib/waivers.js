/**
 * Map raw waiver data to simplified objects.
 * @param {any[]} raw
 * @returns {{player_id: number|string, name: string, delta_xfp: number, order: number}[]}
 */
export function mapWaivers(raw) {
  return raw.map((w) => ({
    player_id: w.player_id ?? w.id ?? 0,
    name: w.name ?? "Unknown Player",
    delta_xfp: w.delta_xfp ?? w.xfp ?? 0,
    order: w.order ?? 0,
  }));
}
