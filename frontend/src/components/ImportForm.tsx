'use client'

import { useRef, useState } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

type Status = 'idle' | 'loading' | 'success' | 'error'

export default function ImportForm() {
  const [status, setStatus] = useState<Status>('idle')
  const [message, setMessage] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const file = inputRef.current?.files?.[0]
    if (!file) return

    const body = new FormData()
    body.append('file', file)

    setStatus('loading')
    setMessage('')

    try {
      const res = await fetch(`${API_URL}/import`, { method: 'POST', body })
      const json = await res.json()
      if (!res.ok) throw new Error(json.detail ?? 'Upload failed')
      setStatus('success')
      setMessage(`Imported ${json.imported} records.`)
      if (inputRef.current) inputRef.current.value = ''
    } catch (e: unknown) {
      setStatus('error')
      setMessage(e instanceof Error ? e.message : 'Unknown error')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-md space-y-4">
      <div>
        <label className="mb-1 block text-sm font-medium">Reddit export file</label>
        <p className="mb-2 text-xs text-gray-500">
          Accepts CSV or JSON. See <code>sample_data/</code> for expected columns.
        </p>
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.json"
          required
          className="block w-full text-sm text-gray-700 file:mr-4 file:rounded-md file:border-0 file:bg-indigo-50 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-indigo-700 hover:file:bg-indigo-100"
        />
      </div>

      <button
        type="submit"
        disabled={status === 'loading'}
        className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
      >
        {status === 'loading' ? 'Uploading…' : 'Upload and import'}
      </button>

      {status === 'success' && <p className="text-sm text-green-600">{message}</p>}
      {status === 'error' && <p className="text-sm text-red-600">{message}</p>}
    </form>
  )
}
