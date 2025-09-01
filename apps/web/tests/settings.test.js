import test from 'node:test';
import assert from 'node:assert';
import { parseCsv } from '../lib/csv.js';

test('parseCsv splits lines and cells', () => {
  const csv = 'a,b\n1,2';
  const rows = parseCsv(csv);
  assert.deepStrictEqual(rows, [ ['a','b'], ['1','2'] ]);
});
