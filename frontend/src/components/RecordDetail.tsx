import type { RedditRecord } from '@/lib/types'
import ScoreBadge from './ScoreBadge'
import TagList from './TagList'

export default function RecordDetail({ record }: { record: RedditRecord }) {
  const hasReasons = Object.keys(record.score_reasons).length > 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <p className="mb-1 text-xs text-gray-400">
          r/{record.subreddit} · {record.source_type} · u/{record.author}
        </p>
        <h2 className="text-xl font-semibold">{record.title ?? '(comment)'}</h2>
        {record.url && (
          <a
            href={record.url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-1 block truncate text-xs text-indigo-600 hover:underline"
          >
            {record.url}
          </a>
        )}
      </div>

      {/* Body */}
      {record.body && (
        <p className="whitespace-pre-wrap rounded-md bg-gray-50 p-4 text-sm text-gray-700">
          {record.body}
        </p>
      )}

      {/* Scores */}
      <div>
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
          Scores
        </h3>
        <div className="flex flex-wrap gap-2">
          <ScoreBadge label="ICP Fit" value={record.icp_fit_score} />
          <ScoreBadge label="Pain Severity" value={record.pain_severity_score} />
          <ScoreBadge label="Purchase Intent" value={record.purchase_intent_score} />
          <ScoreBadge label="ABM Priority" value={record.abm_priority_score} />
        </div>
        {hasReasons && (
          <ul className="mt-3 space-y-1">
            {Object.entries(record.score_reasons).map(([key, reason]) => (
              <li key={key} className="text-xs text-gray-500">
                <span className="font-medium text-gray-700">{key}:</span> {reason}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Tags */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500">
            Industries
          </h3>
          <TagList tags={record.industries} color="indigo" />
        </div>
        <div>
          <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500">
            Buyer Roles
          </h3>
          <TagList tags={record.buyer_roles} color="violet" />
        </div>
        <div>
          <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500">
            Pain Points
          </h3>
          <TagList tags={record.pain_points} color="rose" />
        </div>
        <div>
          <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500">
            Competitors
          </h3>
          <TagList tags={record.competitors} color="amber" />
        </div>
      </div>

      {record.intent_stage && (
        <div>
          <h3 className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500">
            Intent Stage
          </h3>
          <TagList tags={[record.intent_stage]} color="sky" />
        </div>
      )}
    </div>
  )
}
