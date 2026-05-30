import type { RecordFilters, RecordListResponse, RedditRecord } from './types'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, init)
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`)
  return res.json() as Promise<T>
}

function buildParams(filters: RecordFilters): URLSearchParams {
  const p = new URLSearchParams()
  Object.entries(filters).forEach(([k, v]) => {
    if (v !== undefined && v !== '') p.set(k, String(v))
  })
  return p
}

export async function fetchRecords(filters: RecordFilters = {}): Promise<RecordListResponse> {
  return request<RecordListResponse>(`/records?${buildParams(filters)}`)
}

export async function fetchRecord(id: number): Promise<RedditRecord> {
  return request<RedditRecord>(`/records/${id}`)
}

export function exportUrl(filters: RecordFilters = {}): string {
  return `${BASE_URL}/export?${buildParams(filters)}`
}
