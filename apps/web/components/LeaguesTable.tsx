"use client";

import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import Link from "next/link";

export type League = {
  league_id: string;
  name: string;
};

export default function LeaguesTable({ leagues }: { leagues: League[] }) {
  const columns: ColumnDef<League>[] = [
    { accessorKey: "name", header: "Name" },
    {
      accessorKey: "league_id",
      header: "League ID",
      cell: (info) => (
        <Link
          href={`/l/${info.getValue<string>()}/matchup/1`}
          className="text-blue-600 underline"
        >
          {info.getValue<string>()}
        </Link>
      ),
    },
  ];

  const table = useReactTable({
    data: leagues,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <table className="min-w-full divide-y divide-gray-200">
      <thead className="bg-gray-50">
        {table.getHeaderGroups().map((group) => (
          <tr key={group.id}>
            {group.headers.map((header) => (
              <th
                key={header.id}
                className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
              >
                {flexRender(
                  header.column.columnDef.header,
                  header.getContext()
                )}
              </th>
            ))}
          </tr>
        ))}
      </thead>
      <tbody className="divide-y divide-gray-200 bg-white">
        {table.getRowModel().rows.map((row) => (
          <tr key={row.id}>
            {row.getVisibleCells().map((cell) => (
              <td key={cell.id} className="whitespace-nowrap px-6 py-4">
                {flexRender(cell.column.columnDef.cell, cell.getContext())}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
