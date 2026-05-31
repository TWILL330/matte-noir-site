'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { type FormEvent, useCallback, useEffect, useState } from 'react'
import { fetchFacets } from '@/lib/api'
import type { Facets } from '@/lib/types'

const SCORE_OPTIONS = [
  { label: 'Any priority', value: '' },
  { label: 'High (≥ 70)', value: '70' },
  { label: 'Medium+ (≥ 40)', value: '40' },
]

export default function FilterBar() {
  const router = useRouter()
  const params = useSearchParams()
  const [facets, setFacets] = useState<Facets | null>(null)

  useEffect(() => {
    fetchFacets().then(setFacets).catch(() => null)
  }, [])

  const update = useCallback(
    (key: string, value: string) => {
      const next = new URLSearchParams(params.toString())
      value ? next.set(key, value) : next.delete(key)
      next.delete('page')
      router.push(`/?${next}`)
    },
    [params, router],
  )

  function onSearch(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const q = (e.currentTarget.elements.namedItem('q') as HTMLInputElement).value.trim()
    update('q', q)
  }

  function clearAll() {
    router.push('/')
  }

  const hasFilters = ['q', 'subreddit', 'industry', 'buyer_role', 'pain_point',
    'competitor', 'intent_stage', 'min_abm_priority'].some((k) => params.get(k))

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        {/* Text search */}
        <form onSubmit={onSearch} className="flex gap-2">
          <input
            name="q"
            defaultValue={params.get('q') ?? ''}
            placeholder="Search posts and comments…"
            className="w-60 rounded-md border px-3 py-1.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            type="submit"
            className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
          >
            Search
          </button>
        </form>

        {/* Industry */}
        <Select
          value={params.get('industry') ?? ''}
          placeholder="Industry"
          options={facets?.industries ?? []}
          onChange={(v) => update('industry', v)}
        />

        {/* Buyer role */}
        <Select
          value={params.get('buyer_role') ?? ''}
          placeholder="Buyer role"
          options={facets?.buyer_roles ?? []}
          onChange={(v) => update('buyer_role', v)}
        />

        {/* Pain point */}
        <Select
          value={params.get('pain_point') ?? ''}
          placeholder="Pain point"
          options={facets?.pain_points ?? []}
          onChange={(v) => update('pain_point', v)}
        />

        {/* Competitor */}
        <Select
          value={params.get('competitor') ?? ''}
          placeholder="Competitor"
          options={facets?.competitors ?? []}
          onChange={(v) => update('competitor', v)}
        />

        {/* Intent stage */}
        <Select
          value={params.get('intent_stage') ?? ''}
          placeholder="Intent stage"
          options={facets?.intent_stages ?? []}
          onChange={(v) => update('intent_stage', v)}
        />

        {/* ABM priority threshold */}
        <select
          value={params.get('min_abm_priority') ?? ''}
          onChange={(e) => update('min_abm_priority', e.target.value)}
          className="rounded-md border px-2 py-1.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          {SCORE_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>

        {hasFilters && (
          <button
            onClick={clearAll}
            className="text-xs text-gray-400 underline hover:text-gray-700"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Active filter chips */}
      {hasFilters && (
        <div className="flex flex-wrap gap-2">
          {Array.from(params.entries())
            .filter(([k]) => k !== 'page' && k !== 'page_size')
            .map(([k, v]) => (
              <span
                key={k}
                className="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700 ring-1 ring-indigo-200"
              >
                {k.replace(/_/g, ' ')}: {v}
                <button
                  onClick={() => update(k, '')}
                  className="ml-0.5 text-indigo-400 hover:text-indigo-700"
                  aria-label={`Remove ${k} filter`}
                >
                  ×
                </button>
              </span>
            ))}
        </div>
      )}
    </div>
  )
}

// ── Shared select ──────────────────────────────────────────────────────────
function Select({
  value,
  placeholder,
  options,
  onChange,
}: {
  value: string
  placeholder: string
  options: string[]
  onChange: (v: string) => void
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-md border px-2 py-1.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
    >
      <option value="">All {placeholder.toLowerCase()}s</option>
      {options.map((o) => (
        <option key={o} value={o}>
          {o}
        </option>
      ))}
    </select>
  )
}
