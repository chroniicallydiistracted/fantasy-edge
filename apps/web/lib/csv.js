/**
 * Parse a CSV string into rows of cells.
 * @param {string} text
 * @returns {string[][]}
 */
export function parseCsv(text) {
  return text
    .trim()
    .split(/\r?\n/)
    .filter((line) => line.length > 0)
    .map((line) => line.split(',').map((c) => c.trim()));
}
