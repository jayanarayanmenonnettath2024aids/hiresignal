export interface Job {
  id: string
  tenant_id: string
  created_by: string
  title: string
  jd_text: string
  jd_skills_extracted: string[]
  jd_quality_score: number
  jd_is_vague: boolean
  weight_semantic: number
  weight_tfidf: number
  weight_skills: number
  weight_experience: number
  total_submitted: number
  total_processed: number
  total_failed: number
  status: 'pending' | 'processing' | 'done' | 'failed'
  started_at?: string
  completed_at?: string
  created_at: string
  updated_at: string
}

export interface JobCreate {
  title: string
  jd_text: string
  weights?: {
    weight_semantic?: number
    weight_tfidf?: number
    weight_skills?: number
    weight_experience?: number
  }
  top_n?: number
}

export interface JobResponse extends Job {}

export interface JDPreviewResponse {
  skills: string[]
  quality_score: number
  is_vague: boolean
  min_yoe?: number
}
