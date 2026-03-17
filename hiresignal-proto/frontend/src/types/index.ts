export type { Job, JobCreate, JobResponse, JDPreviewResponse } from './job'
export type { ResumeResult, ResumeResultResponse, SingleScreenRequest, SingleScreenResponse, Feedback, FeedbackCreate } from './resume'

export interface User {
  id: string
  email: string
  full_name?: string
  role: 'hr' | 'admin'
  tenant_id: string
}

export interface AuthState {
  token: string | null
  user: User | null
  setToken: (token: string) => void
  setUser: (user: User) => void
  logout: () => void
}
