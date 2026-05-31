'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { exportUrl, fetchRecords } from '@/lib/api'
import type { RecordFilters, RecordListResponse } from '@/lib/types'
import EmptyState from './EmptyState'
import FilterBar from './FilterBar'
import RecordCard from './RecordCard'
import Spinner from './Spinner'

const PAGE_SIZE = 20

export default function Dashboard() {
  const params = useSearchParams()
  const router = useRouter()
  const [data, setData] = useState<RecordListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const page = params.get('page') ? Number(params.get('page')) : 1

  const filters: RecordFilters = {
    q: params.get('q') ?? undefined,
    subreddit: params.get('subreddit') ?? undefined,
    industry: params.get('industry') ?? undefined,
    buyer_role: params.get('buyer_role') ?? undefined,
    pain_point: params.get('pain_point') ?? undefined,
    competitor: params.get('competitor') ?? undefined,
    intent_stage: params.get('intent_stage') ?? undefined,
    min_abm_priority: params.get('min_abm_priority')
      ? Number(params.get('min_abm_priority'))
      : undefined,
    page,
    page_size: PAGE_SIZE,
  }

  useEffect(() => {
    setLoading(true)
    setError(null)
    fetchRecords(filters)
      .then((d) => { setData(d); setError(null) })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.toString()])

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 0

  function goPage(p: number) {
    const next = new URLSearchParams(params.toString())
    next.set('page', String(p))
    router.push(`/?${next}`)
  }

  const hasFilters = ['q', 'subreddit', 'industry', 'buyer_role', 'pain_point',
    'competitor', 'intent_stage', 'min_abm_priority'].some((k) => params.get(k))

  return (
    <div className="space-y-6">

      {/* Toolbar */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <FilterBar />
        <a
          href={exportUrl(filters)}
          className="shrink-0 rounded-md border px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Export CSV
        </a>
      </div>

      {/* Loading */}
      {loading && <Spinner label="Loading records…" />}

      {/* Error */}
      {!loading && error && (
        <div className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <p className="font-medium">Could not load records</p>
          <p className="mt-0.5 text-xs">{error}</p>
          <button
            onClick={() => setLoading(true)}
            className="mt-2 text-xs text-red-500 underline hover:text-red-700"
          >
            Retry
          </button>
        </div>
      )}

      {/* Results */}
      {!loading && data && (
        <>
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-500">
              {data.total.toLocaleString()} record{data.total !== 1 ? 's' : ''}
              {totalPages > 1 && (
                <span className="ml-2 text-gray-400">
                  · page {page} of {totalPages}
                </span>
              )}
            </p>
          </div>

          {data.records.length === 0 ? (
            <EmptyState hasFilters={hasFilters} />
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {data.records.map((r) => (
                <RecordCard key={r.id} record={r} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={() => goPage(page - 1)}
                disabled={page <= 1}
                className="rounded-md border px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-40"
              >
                ← Prev
              </button>
              <span className="text-sm text-gray-500">
                {page} / {totalPages}
              </span>
              <button
                onClick={() => goPage(page + 1)}
                disabled={page >= totalPages}
                className="rounded-md border px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-40"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
