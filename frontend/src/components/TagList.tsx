type Color = 'indigo' | 'violet' | 'rose' | 'amber' | 'sky'

const colorMap: Record<Color, string> = {
  indigo: 'bg-indigo-50 text-indigo-700 ring-indigo-200',
  violet: 'bg-violet-50 text-violet-700 ring-violet-200',
  rose: 'bg-rose-50 text-rose-700 ring-rose-200',
  amber: 'bg-amber-50 text-amber-700 ring-amber-200',
  sky: 'bg-sky-50 text-sky-700 ring-sky-200',
}

interface Props {
  tags: string[]
  color?: Color
}

export default function TagList({ tags, color = 'indigo' }: Props) {
  if (!tags.length) return <span className="text-xs text-gray-400">—</span>
  return (
    <div className="flex flex-wrap gap-1">
      {tags.map((tag) => (
        <span
          key={tag}
          className={`inline-flex items-center rounded px-1.5 py-0.5 text-xs font-medium ring-1 ring-inset ${colorMap[color]}`}
        >
          {tag}
        </span>
      ))}
    </div>
  )
}
