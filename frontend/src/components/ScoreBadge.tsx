interface Props {
  label: string
  value: number | null
  size?: 'sm' | 'lg'
}

function colorClass(v: number): string {
  if (v >= 70) return 'bg-green-100 text-green-800'
  if (v >= 40) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
}

export default function ScoreBadge({ label, value, size = 'sm' }: Props) {
  if (value === null) return null
  const base =
    size === 'lg'
      ? 'inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-medium'
      : 'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium'
  return (
    <span className={`${base} ${colorClass(value)}`}>
      {label}
      <span className="font-bold">{Math.round(value)}</span>
    </span>
  )
}
