import test from 'node:test';
import assert from 'node:assert';
import { mapWaivers } from '../lib/waivers.js';

test('mapWaivers normalizes waiver fields', () => {
  const raw = [
    { player_id: 1, delta_xfp: 2, order: 1, name: 'A' },
    { id: 2, xfp: 3, order: 2, name: 'B' },
  ];
  const mapped = mapWaivers(raw);
  assert.deepStrictEqual(mapped, [
    { player_id: 1, name: 'A', delta_xfp: 2, order: 1 },
    { player_id: 2, name: 'B', delta_xfp: 3, order: 2 },
  ]);
});
