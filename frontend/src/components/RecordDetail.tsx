import type { RedditRecord } from '@/lib/types'
import ScoreBadge from './ScoreBadge'
import TagList from './TagList'

const SCORE_DIMS = [
  { key: 'icp_fit_score',         label: 'ICP Fit',         reason_key: 'icp_fit' },
  { key: 'pain_severity_score',   label: 'Pain Severity',   reason_key: 'pain_severity' },
  { key: 'purchase_intent_score', label: 'Purchase Intent', reason_key: 'purchase_intent' },
  { key: 'abm_priority_score',    label: 'ABM Priority',    reason_key: 'abm_priority' },
] as const

export default function RecordDetail({ record }: { record: RedditRecord }) {
  return (
    <div className="space-y-8">

      {/* ── Header ──────────────────────────────────────────────── */}
      <div>
        <p className="mb-1 text-xs text-gray-400">
          r/{record.subreddit} · {record.source_type}
          {record.author ? ` · u/${record.author}` : ''}
          {record.created_utc
            ? ` · ${new Date(record.created_utc).toLocaleDateString()}`
            : ''}
        </p>
        <h2 className="text-xl font-semibold leading-snug">
          {record.title ?? '(comment — no title)'}
        </h2>
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
        {(record.reddit_score !== null || record.num_comments !== null) && (
          <p className="mt-1 text-xs text-gray-400">
            {record.reddit_score !== null ? `↑ ${record.reddit_score} upvotes` : ''}
            {record.reddit_score !== null && record.num_comments !== null ? ' · ' : ''}
            {record.num_comments !== null ? `${record.num_comments} comments` : ''}
          </p>
        )}
      </div>

      {/* ── Body ────────────────────────────────────────────────── */}
      {record.body && (
        <div className="rounded-md border bg-gray-50 p-4 text-sm text-gray-700">
          <p className="whitespace-pre-wrap">{record.body}</p>
        </div>
      )}

      {/* ── Scores ──────────────────────────────────────────────── */}
      <div>
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-500">
          Signal Scores
        </h3>
        <div className="grid gap-3 sm:grid-cols-2">
          {SCORE_DIMS.map(({ key, label, reason_key }) => {
            const val = record[key]
            const reason = record.score_reasons[reason_key]
            if (val === null) return null
            return (
              <div key={key} className="rounded-md border bg-white p-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">{label}</span>
                  <ScoreBadge label="" value={val} size="lg" />
                </div>
                {reason && (
                  <p className="mt-1.5 text-xs text-gray-500 leading-relaxed">{reason}</p>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* ── Tags ────────────────────────────────────────────────── */}
      <div>
        <h3 className="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-500">
          Tags
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <TagSection label="Industries"  tags={record.industries}  color="indigo" />
          <TagSection label="Buyer Roles" tags={record.buyer_roles} color="violet" />
          <TagSection label="Pain Points" tags={record.pain_points} color="rose" />
          <TagSection label="Competitors" tags={record.competitors} color="amber" />
          {record.intent_stage && (
            <TagSection label="Intent Stage" tags={[record.intent_stage]} color="sky" />
          )}
        </div>
      </div>

    </div>
  )
}

function TagSection({
  label,
  tags,
  color,
}: {
  label: string
  tags: string[]
  color: 'indigo' | 'violet' | 'rose' | 'amber' | 'sky'
}) {
  return (
    <div>
      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500">
        {label}
      </p>
      <TagList tags={tags} color={color} />
    </div>
  )
}
