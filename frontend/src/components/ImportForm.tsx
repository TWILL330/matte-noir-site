'use client'

import { useRef, useState } from 'react'
import type { ImportResponse } from '@/lib/importTypes'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const MAX_MB = 50
const ALLOWED = ['.csv', '.json']

type Status = 'idle' | 'loading' | 'success' | 'error'

export default function ImportForm() {
  const [status, setStatus] = useState<Status>('idle')
  const [message, setMessage] = useState('')
  const [result, setResult] = useState<ImportResponse | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  function validateFile(file: File): string | null {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase()
    if (!ALLOWED.includes(ext)) return `Only ${ALLOWED.join(' or ')} files are accepted.`
    if (file.size > MAX_MB * 1024 * 1024) return `File must be under ${MAX_MB} MB.`
    return null
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const file = inputRef.current?.files?.[0]
    if (!file) return

    const validationError = validateFile(file)
    if (validationError) {
      setStatus('error')
      setMessage(validationError)
      return
    }

    const body = new FormData()
    body.append('file', file)

    setStatus('loading')
    setMessage('')
    setResult(null)

    try {
      const res = await fetch(`${API_URL}/import`, { method: 'POST', body })
      const json = await res.json()
      if (!res.ok) throw new Error(json.detail ?? 'Upload failed')
      setStatus('success')
      setResult(json as ImportResponse)
      setMessage('')
      if (inputRef.current) inputRef.current.value = ''
    } catch (e: unknown) {
      setStatus('error')
      setMessage(e instanceof Error ? e.message : 'Unknown error')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-md space-y-5">
      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          Reddit export file
        </label>
        <p className="mb-2 text-xs text-gray-500">
          Accepts <code>.csv</code> or <code>.json</code>. See{' '}
          <code>sample_data/</code> for the expected column format.
          Max {MAX_MB} MB.
        </p>
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.json"
          required
          disabled={status === 'loading'}
          className="block w-full text-sm text-gray-700 file:mr-4 file:rounded-md file:border-0 file:bg-indigo-50 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-indigo-700 hover:file:bg-indigo-100 disabled:opacity-50"
        />
      </div>

      <button
        type="submit"
        disabled={status === 'loading'}
        className="flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        {status === 'loading' && (
          <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        )}
        {status === 'loading' ? 'Uploading…' : 'Upload and import'}
      </button>

      {/* Success result */}
      {status === 'success' && result && (
        <div className="rounded-md border border-green-200 bg-green-50 p-4 text-sm">
          <p className="font-semibold text-green-800">Import complete</p>
          <dl className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-green-700">
            <dt>Imported</dt><dd className="font-bold">{result.imported}</dd>
            <dt>Skipped (dupes)</dt><dd className="font-bold">{result.skipped}</dd>
            <dt>Errors</dt><dd className="font-bold">{result.errors}</dd>
            <dt>Total rows</dt><dd className="font-bold">{result.total}</dd>
          </dl>
          <a href="/" className="mt-3 block text-xs text-indigo-600 hover:underline">
            View dashboard →
          </a>
        </div>
      )}

      {/* Error */}
      {status === 'error' && (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {message}
        </div>
      )}
    </form>
  )
}
