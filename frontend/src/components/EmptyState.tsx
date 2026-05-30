import Link from 'next/link'

interface Props {
  hasFilters: boolean
}

export default function EmptyState({ hasFilters }: Props) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed py-20 text-center">
      <p className="text-2xl">🔍</p>
      {hasFilters ? (
        <>
          <p className="mt-3 font-medium text-gray-700">No records match these filters</p>
          <p className="mt-1 text-sm text-gray-400">Try removing a filter or broadening your search.</p>
        </>
      ) : (
        <>
          <p className="mt-3 font-medium text-gray-700">No records yet</p>
          <p className="mt-1 text-sm text-gray-400">Import a CSV or JSON file to get started.</p>
          <Link
            href="/import"
            className="mt-4 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
          >
            Import data
          </Link>
        </>
      )}
    </div>
  )
}
