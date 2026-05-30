import ImportForm from '@/components/ImportForm'

export default function ImportPage() {
  return (
    <div className="max-w-xl">
      <h2 className="mb-1 text-lg font-semibold">Import Reddit data</h2>
      <p className="mb-6 text-sm text-gray-500">
        Upload a CSV or JSON file. Records will be normalized, tagged, and scored automatically.
      </p>
      <ImportForm />
    </div>
  )
}
