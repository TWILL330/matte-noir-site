import Link from 'next/link'
import type { RedditRecord } from '@/lib/types'
import ScoreBadge from './ScoreBadge'
import TagList from './TagList'

export default function RecordCard({ record }: { record: RedditRecord }) {
  const preview = record.title ?? record.body?.slice(0, 80) ?? '(no content)'

  return (
    <Link
      href={`/records/${record.id}`}
      className="block rounded-lg border bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <p className="truncate font-medium text-gray-900">{preview}</p>
          <p className="mt-0.5 text-xs text-gray-400">
            r/{record.subreddit} · {record.source_type} · u/{record.author}
          </p>
        </div>
        <div className="flex shrink-0 flex-col items-end gap-1">
          <ScoreBadge label="ABM" value={record.abm_priority_score} />
          <ScoreBadge label="Intent" value={record.purchase_intent_score} />
        </div>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-gray-500">
        <div>
          <span className="font-medium">Industries</span>
          <div className="mt-1">
            <TagList tags={record.industries} color="indigo" />
          </div>
        </div>
        <div>
          <span className="font-medium">Pain points</span>
          <div className="mt-1">
            <TagList tags={record.pain_points} color="rose" />
          </div>
        </div>
      </div>

      {record.intent_stage && (
        <p className="mt-2 text-xs text-gray-400">
          Stage: <span className="font-medium text-gray-600">{record.intent_stage}</span>
        </p>
      )}
    </Link>
  )
}
