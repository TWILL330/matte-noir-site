import { Suspense } from 'react'
import Dashboard from '@/components/Dashboard'

export default function DashboardPage() {
  return (
    <Suspense fallback={<p className="text-sm text-gray-400">Loading…</p>}>
      <Dashboard />
    </Suspense>
  )
}
