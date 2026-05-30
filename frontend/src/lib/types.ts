export type SourceType = 'post' | 'comment'
export type IntentStage = 'awareness' | 'consideration' | 'decision' | 'frustration' | 'advocacy'

export interface RedditRecord {
  id: number
  source_id: string
  source_type: SourceType
  subreddit: string | null
  author: string | null
  title: string | null
  body: string | null
  url: string | null
  created_utc: string | null
  reddit_score: number | null
  num_comments: number | null
  imported_at: string

  industries: string[]
  buyer_roles: string[]
  pain_points: string[]
  competitors: string[]
  intent_stage: string | null

  // Scores are integers 0–100
  icp_fit_score: number | null
  pain_severity_score: number | null
  purchase_intent_score: number | null
  abm_priority_score: number | null
  score_reasons: Record<string, string>
}

export interface RecordListResponse {
  total: number
  page: number
  page_size: number
  records: RedditRecord[]
}

export interface Facets {
  industries: string[]
  buyer_roles: string[]
  pain_points: string[]
  competitors: string[]
  intent_stages: string[]
  subreddits: string[]
}

export interface RecordFilters {
  q?: string
  subreddit?: string
  industry?: string
  buyer_role?: string
  pain_point?: string
  competitor?: string
  intent_stage?: string
  min_icp_fit?: number
  min_pain_severity?: number
  min_purchase_intent?: number
  min_abm_priority?: number
  page?: number
  page_size?: number
}
