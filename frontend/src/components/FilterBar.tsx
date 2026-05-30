'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { type FormEvent, useCallback } from 'react'

const INTENT_STAGES = ['awareness', 'consideration', 'decision', 'frustration', 'advocacy']

export default function FilterBar() {
  const router = useRouter()
  const params = useSearchParams()

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
    const q = (e.currentTarget.elements.namedItem('q') as HTMLInputElement).value
    update('q', q)
  }

  return (
    <div className="flex flex-wrap items-center gap-3">
      <form onSubmit={onSearch} className="flex gap-2">
        <input
          name="q"
          defaultValue={params.get('q') ?? ''}
          placeholder="Search posts and comments…"
          className="rounded-md border px-3 py-1.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          type="submit"
          className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700"
        >
          Search
        </button>
      </form>

      <select
        value={params.get('intent_stage') ?? ''}
        onChange={(e) => update('intent_stage', e.target.value)}
        className="rounded-md border px-2 py-1.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
      >
        <option value="">All intent stages</option>
        {INTENT_STAGES.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>

      <select
        value={params.get('min_abm_priority') ?? ''}
        onChange={(e) => update('min_abm_priority', e.target.value)}
        className="rounded-md border px-2 py-1.5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
      >
        <option value="">Any ABM priority</option>
        <option value="0.7">High (≥ 70)</option>
        <option value="0.4">Medium+ (≥ 40)</option>
      </select>
    </div>
  )
}
