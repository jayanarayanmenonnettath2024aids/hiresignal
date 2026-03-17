export interface ResumeResult {
  id: string
  job_id: string
  tenant_id: string
  filename: string
  file_key: string
  content_hash: string
  score_semantic: number
  score_tfidf: number
  score_skills: number
  score_experience: number
  final_score: number
  extracted_text: string
  extraction_quality: 'good' | 'ocr_used' | 'poor'
  language_detected: string
  extracted_text_length: number
  matched_skills: string[]
  missing_skills: string[]
  years_experience_detected?: number
  flags: Record<string, boolean>
  status: 'pending' | 'done' | 'failed'
  error_message?: string
  processing_ms?: number
  rank?: number
  created_at: string
  updated_at: string
}

export interface ResumeResultResponse extends ResumeResult {}

export interface SingleScreenRequest {
  jd_text: string
  resume_file?: File
}

export interface SingleScreenResponse {
  final_score: number
  score_semantic: number
  score_tfidf: number
  score_skills: number
  score_experience: number
  matched_skills: string[]
  missing_skills: string[]
  years_experience_detected?: number
  flags: Record<string, boolean>
}

export interface FeedbackCreate {
  result_id: string
  action: 'shortlist' | 'reject'
  notes?: string
}

export interface Feedback {
  id: string
  result_id: string
  job_id: string
  tenant_id: string
  user_id: string
  action: 'shortlist' | 'reject'
  notes?: string
  created_at: string
}
