export interface ImportResponse {
  import_run_id: number
  filename: string
  total: number
  imported: number
  skipped: number
  errors: number
  status: string
}
