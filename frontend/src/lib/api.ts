import type { Facets, RecordFilters, RecordListResponse, RedditRecord } from './types'

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    cache: 'no-store',
  })
  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const body = await res.json()
      detail = body.detail ?? detail
    } catch {
      // ignore parse error
    }
    throw new Error(detail)
  }
  return res.json() as Promise<T>
}

function buildParams(filters: RecordFilters): URLSearchParams {
  const p = new URLSearchParams()
  Object.entries(filters).forEach(([k, v]) => {
    if (v !== undefined && v !== '' && v !== null) p.set(k, String(v))
  })
  return p
}

export async function fetchRecords(filters: RecordFilters = {}): Promise<RecordListResponse> {
  return request<RecordListResponse>(`/records?${buildParams(filters)}`)
}

export async function fetchRecord(id: number): Promise<RedditRecord> {
  return request<RedditRecord>(`/records/${id}`)
}

export async function fetchFacets(): Promise<Facets> {
  return request<Facets>('/records/facets')
}

export function exportUrl(filters: RecordFilters = {}): string {
  return `${BASE_URL}/export?${buildParams(filters)}`
}
