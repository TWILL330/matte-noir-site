import Link from 'next/link'
import type { RedditRecord } from '@/lib/types'
import ScoreBadge from './ScoreBadge'
import TagList from './TagList'

export default function RecordCard({ record }: { record: RedditRecord }) {
  const preview = record.title ?? record.body?.slice(0, 100) ?? '(no content)'

  return (
    <Link
      href={`/records/${record.id}`}
      className="flex flex-col rounded-lg border bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="line-clamp-2 font-medium text-gray-900 leading-snug">{preview}</p>
          <p className="mt-1 truncate text-xs text-gray-400">
            r/{record.subreddit} · {record.source_type}
            {record.author ? ` · u/${record.author}` : ''}
          </p>
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1">
          <ScoreBadge label="ABM" value={record.abm_priority_score} />
          <ScoreBadge label="Intent" value={record.purchase_intent_score} />
        </div>
      </div>

      {/* Tags */}
      <div className="mt-3 grid grid-cols-2 gap-x-4 gap-y-2 text-xs text-gray-500">
        {record.industries.length > 0 && (
          <div>
            <span className="font-medium">Industry</span>
            <div className="mt-0.5">
              <TagList tags={record.industries.slice(0, 2)} color="indigo" />
            </div>
          </div>
        )}
        {record.pain_points.length > 0 && (
          <div>
            <span className="font-medium">Pain</span>
            <div className="mt-0.5">
              <TagList tags={record.pain_points.slice(0, 2)} color="rose" />
            </div>
          </div>
        )}
        {record.competitors.length > 0 && (
          <div>
            <span className="font-medium">Competitors</span>
            <div className="mt-0.5">
              <TagList tags={record.competitors.slice(0, 2)} color="amber" />
            </div>
          </div>
        )}
        {record.intent_stage && (
          <div>
            <span className="font-medium">Intent</span>
            <div className="mt-0.5">
              <TagList tags={[record.intent_stage]} color="sky" />
            </div>
          </div>
        )}
      </div>
    </Link>
  )
}
