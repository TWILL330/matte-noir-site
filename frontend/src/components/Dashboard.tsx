'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { exportUrl, fetchRecords } from '@/lib/api'
import type { RecordFilters, RecordListResponse } from '@/lib/types'
import FilterBar from './FilterBar'
import RecordCard from './RecordCard'

const PAGE_SIZE = 20

export default function Dashboard() {
  const params = useSearchParams()
  const [data, setData] = useState<RecordListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const filters: RecordFilters = {
    q: params.get('q') ?? undefined,
    intent_stage: params.get('intent_stage') ?? undefined,
    min_abm_priority: params.get('min_abm_priority')
      ? Number(params.get('min_abm_priority'))
      : undefined,
    page: params.get('page') ? Number(params.get('page')) : 1,
    page_size: PAGE_SIZE,
  }

  useEffect(() => {
    setLoading(true)
    setError(null)
    fetchRecords(filters)
      .then(setData)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.toString()])

  return (
    <div className="space-y-6">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <FilterBar />
        <a
          href={exportUrl(filters)}
          className="rounded-md border px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Export CSV
        </a>
      </div>

      {/* State feedback */}
      {loading && <p className="text-sm text-gray-400">Loading…</p>}
      {error && <p className="text-sm text-red-500">Error: {error}</p>}

      {/* Results */}
      {data && !loading && (
        <>
          <p className="text-sm text-gray-500">
            {data.total.toLocaleString()} record{data.total !== 1 ? 's' : ''}
          </p>

          {data.records.length === 0 ? (
            <p className="text-sm text-gray-400">No records match the current filters.</p>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {data.records.map((r) => (
                <RecordCard key={r.id} record={r} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
