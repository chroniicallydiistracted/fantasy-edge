'use client'
import { useSearchParams } from 'next/navigation'
export default function Callback() {
  const sp = useSearchParams();
  return <pre>{JSON.stringify({ code: sp.get('code'), state: sp.get('state') }, null, 2)}</pre>
}
