import { notFound } from 'next/navigation'
import Link from 'next/link'
import { fetchRecord } from '@/lib/api'
import RecordDetail from '@/components/RecordDetail'

export default async function RecordPage({ params }: { params: { id: string } }) {
  const id = Number(params.id)
  if (!Number.isInteger(id) || id <= 0) notFound()

  let record
  try {
    record = await fetchRecord(id)
  } catch {
    notFound()
  }

  return (
    <div className="max-w-2xl">
      <Link
        href="/"
        className="mb-6 inline-flex items-center gap-1 text-sm text-indigo-600 hover:underline"
      >
        ← Back to dashboard
      </Link>
      <RecordDetail record={record} />
    </div>
  )
}
