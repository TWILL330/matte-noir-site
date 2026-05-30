interface Props {
  label: string
  value: number | null
}

function colorClass(v: number): string {
  if (v >= 0.7) return 'bg-green-100 text-green-800'
  if (v >= 0.4) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
}

export default function ScoreBadge({ label, value }: Props) {
  if (value === null) return null
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${colorClass(value)}`}
    >
      {label}
      <span className="font-bold">{Math.round(value * 100)}</span>
    </span>
  )
}
