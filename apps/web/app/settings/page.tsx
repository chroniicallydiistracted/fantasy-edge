"use client";

import { useState } from "react";
import { parseCsv } from "../../lib/csv";

export default function SettingsPage() {
  const [rows, setRows] = useState<string[][]>([]);
  const [sheetUrl, setSheetUrl] = useState("");

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    setRows(parseCsv(text));
  };

  return (
    <div>
      <h1 className="mb-4 text-xl font-bold">Settings</h1>
      <div>
        <label className="block font-semibold">Google Sheets URL</label>
        <input
          type="text"
          value={sheetUrl}
          onChange={(e) => setSheetUrl(e.target.value)}
          className="border p-1"
        />
      </div>
      <div className="mt-4">
        <label className="block font-semibold">Import CSV</label>
        <input type="file" accept=".csv" onChange={handleFile} />
      </div>
      {rows.length > 0 && (
        <table className="mt-4">
          <tbody>
            {rows.map((r, i) => (
              <tr key={i}>
                {r.map((c, j) => (
                  <td key={j} className="px-2">
                    {c}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
