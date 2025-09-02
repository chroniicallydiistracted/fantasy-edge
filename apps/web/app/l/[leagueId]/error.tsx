"use client";

export default function Error({ error }: { error: Error }) {
  return (
    <div role="alert" className="text-red-600">
      Failed to load league data: {error.message}
    </div>
  );
}
