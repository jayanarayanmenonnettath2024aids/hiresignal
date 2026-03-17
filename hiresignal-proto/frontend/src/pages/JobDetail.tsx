import { useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { exportAPI, feedbackAPI, jobsAPI } from '../api/client'

function statusClass(status: string): string {
  if (status === 'done') return 'bg-green-100 text-green-800'
  if (status === 'processing') return 'bg-blue-100 text-blue-800'
  if (status === 'failed') return 'bg-red-100 text-red-800'
  return 'bg-gray-100 text-gray-700'
}

export default function JobDetail() {
  const navigate = useNavigate()
  const { jobId } = useParams<{ jobId: string }>()
  const [uploadFiles, setUploadFiles] = useState<FileList | null>(null)
  const [uploading, setUploading] = useState(false)
  const [feedbackBusyId, setFeedbackBusyId] = useState<string | null>(null)
  const [error, setError] = useState('')

  const { data: job, refetch: refetchJob } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => jobsAPI.get(jobId as string).then((r) => r.data),
    enabled: Boolean(jobId),
    refetchInterval: 3000,
  })

  const { data: results, refetch: refetchResults } = useQuery({
    queryKey: ['results', jobId],
    queryFn: () => jobsAPI.getResults(jobId as string).then((r) => r.data),
    enabled: Boolean(jobId),
    refetchInterval: 3000,
  })

  const rankedResults = useMemo(
    () => (Array.isArray(results) ? [...results].sort((a: any, b: any) => (a.rank || 9999) - (b.rank || 9999)) : []),
    [results],
  )

  async function uploadResumes(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (!jobId) return
    if (!uploadFiles || uploadFiles.length === 0) {
      setError('Select one or more resume files first.')
      return
    }

    const formData = new FormData()
    Array.from(uploadFiles).forEach((f) => formData.append('files', f))

    setUploading(true)
    try {
      await jobsAPI.uploadResumes(jobId, formData)
      setUploadFiles(null)
      await refetchJob()
      await refetchResults()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed.')
    } finally {
      setUploading(false)
    }
  }

  async function addFeedback(resultId: string, action: 'shortlisted' | 'rejected') {
    setError('')
    setFeedbackBusyId(resultId + action)
    try {
      await feedbackAPI.create({ result_id: resultId, action })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Feedback save failed.')
    } finally {
      setFeedbackBusyId(null)
    }
  }

  async function downloadCsv() {
    if (!jobId) return
    const response = await exportAPI.csv(jobId)
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `job-${jobId}-results.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  async function downloadExcel() {
    if (!jobId) return
    const response = await exportAPI.excel(jobId)
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const a = document.createElement('a')
    a.href = url
    a.download = `job-${jobId}-results.xlsx`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">Job Detail</h1>
          <div className="flex items-center gap-2">
            <button onClick={() => navigate('/')} className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-100 text-sm font-medium">
              Dashboard
            </button>
            <button onClick={downloadCsv} className="px-4 py-2 rounded-lg bg-gray-800 hover:bg-black text-white text-sm font-medium">
              Export CSV
            </button>
            <button onClick={downloadExcel} className="px-4 py-2 rounded-lg bg-green-700 hover:bg-green-800 text-white text-sm font-medium">
              Export Excel
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {job && (
          <div className="bg-white rounded-xl shadow p-6 grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="md:col-span-2">
              <p className="text-sm text-gray-500">Title</p>
              <p className="text-lg font-semibold">{job.title}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Status</p>
              <span className={`inline-block mt-1 px-3 py-1 rounded-full text-xs font-semibold ${statusClass(job.status)}`}>
                {job.status}
              </span>
            </div>
            <div>
              <p className="text-sm text-gray-500">Processed</p>
              <p className="text-lg font-semibold">{job.total_processed}/{job.total_submitted}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Failed</p>
              <p className="text-lg font-semibold">{job.total_failed}</p>
            </div>
          </div>
        )}

        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Upload Resumes</h2>
          <form onSubmit={uploadResumes} className="space-y-4">
            <input
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.txt,.zip"
              onChange={(e) => setUploadFiles(e.target.files)}
              className="w-full text-sm"
            />
            {uploadFiles && uploadFiles.length > 0 && (
              <p className="text-sm text-gray-600">Selected {uploadFiles.length} file(s)</p>
            )}
            <button
              type="submit"
              disabled={uploading}
              className="px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-semibold"
            >
              {uploading ? 'Uploading...' : 'Upload & Process'}
            </button>
          </form>
        </div>

        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="bg-white rounded-xl shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold">Ranked Results</h2>
          </div>

          {rankedResults.length === 0 ? (
            <div className="p-6 text-sm text-gray-500">No results yet. Upload resumes to start screening.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[980px]">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Rank</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Filename</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Final</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Semantic</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">TF-IDF</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Skills</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Experience</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {rankedResults.map((r: any) => (
                    <tr key={r.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-semibold">{r.rank ?? '-'}</td>
                      <td className="px-4 py-3 text-sm">{r.filename}</td>
                      <td className="px-4 py-3 text-sm font-semibold">{(r.final_score * 100).toFixed(1)}%</td>
                      <td className="px-4 py-3 text-sm">{(r.score_semantic * 100).toFixed(1)}%</td>
                      <td className="px-4 py-3 text-sm">{(r.score_tfidf * 100).toFixed(1)}%</td>
                      <td className="px-4 py-3 text-sm">{(r.score_skills * 100).toFixed(1)}%</td>
                      <td className="px-4 py-3 text-sm">{(r.score_experience * 100).toFixed(1)}%</td>
                      <td className="px-4 py-3 text-sm">
                        <div className="flex items-center gap-2">
                          <button
                            disabled={feedbackBusyId === r.id + 'shortlisted'}
                            onClick={() => addFeedback(r.id, 'shortlisted')}
                            className="px-2.5 py-1 rounded bg-green-100 hover:bg-green-200 text-green-800 text-xs font-semibold"
                          >
                            Shortlist
                          </button>
                          <button
                            disabled={feedbackBusyId === r.id + 'rejected'}
                            onClick={() => addFeedback(r.id, 'rejected')}
                            className="px-2.5 py-1 rounded bg-red-100 hover:bg-red-200 text-red-800 text-xs font-semibold"
                          >
                            Reject
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
