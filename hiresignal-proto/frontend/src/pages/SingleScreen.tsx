import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { screeningAPI } from '../api/client'
import type { SingleScreenResponse } from '../types/resume'

function scoreColor(score: number): string {
  if (score >= 0.75) return 'text-green-600'
  if (score >= 0.5) return 'text-amber-600'
  return 'text-red-600'
}

function qualityBadge(quality: string): string {
  if (quality === 'good') return 'bg-green-100 text-green-800'
  if (quality === 'ocr_used') return 'bg-blue-100 text-blue-800'
  return 'bg-amber-100 text-amber-800'
}

export default function SingleScreen() {
  const navigate = useNavigate()
  const [jdText, setJdText] = useState('')
  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<SingleScreenResponse | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')

    if (!jdText.trim()) {
      setError('Please paste the job description first.')
      return
    }

    if (!resumeFile) {
      setError('Please upload a resume file.')
      return
    }

    const formData = new FormData()
    formData.append('jd_text', jdText)
    formData.append('resume_file', resumeFile)

    setLoading(true)
    try {
      const response = await screeningAPI.singleScreen(formData)
      setResult(response.data)
    } catch (err: any) {
      setResult(null)
      setError(err.response?.data?.detail || 'Single screening failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const scoreRows = result
    ? [
        { label: 'Final', value: result.final_score },
        { label: 'Semantic', value: result.score_semantic },
        { label: 'TF-IDF', value: result.score_tfidf },
        { label: 'Skills', value: result.score_skills },
        { label: 'Experience', value: result.score_experience },
      ]
    : []

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">Single Resume Screen</h1>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-100 text-sm font-medium"
          >
            Back to Dashboard
          </button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Input</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Job Description</label>
              <textarea
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                rows={12}
                placeholder="Paste the full JD here..."
                className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Resume File</label>
              <input
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                onChange={(e) => setResumeFile(e.target.files?.[0] || null)}
                className="w-full text-sm"
              />
              {resumeFile && (
                <p className="mt-2 text-sm text-gray-600">
                  Selected: <span className="font-medium">{resumeFile.name}</span>
                </p>
              )}
            </div>

            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-2.5 font-semibold transition"
            >
              {loading ? 'Screening...' : 'Run Single Screen'}
            </button>
          </form>
        </div>

        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Result</h2>

          {!result && !loading && (
            <div className="h-full rounded-lg border border-dashed border-gray-300 bg-gray-50 p-6 text-sm text-gray-500">
              Submit a JD and resume to see score breakdown, skills gap, extraction quality, and NLP flags.
            </div>
          )}

          {loading && (
            <div className="h-full rounded-lg border border-blue-200 bg-blue-50 p-6 text-sm text-blue-700">
              Screening in progress. Usually completes in a few seconds...
            </div>
          )}

          {result && (
            <div className="space-y-5">
              <div className="flex items-center justify-between rounded-lg bg-gray-50 px-4 py-3 border border-gray-200">
                <div>
                  <p className="text-sm text-gray-500">Candidate</p>
                  <p className="font-semibold">{result.filename || 'resume'}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-gray-500">Final Score</p>
                  <p className={`text-3xl font-bold ${scoreColor(result.final_score)}`}>
                    {(result.final_score * 100).toFixed(1)}%
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {scoreRows.map((row) => (
                  <div key={row.label} className="rounded-lg border border-gray-200 p-3">
                    <p className="text-sm text-gray-500">{row.label} Score</p>
                    <p className={`text-xl font-semibold ${scoreColor(row.value)}`}>
                      {(row.value * 100).toFixed(1)}%
                    </p>
                  </div>
                ))}
              </div>

              <div className="flex items-center gap-3 text-sm">
                <span className={`px-3 py-1 rounded-full font-medium ${qualityBadge(result.extraction_quality)}`}>
                  {result.extraction_quality}
                </span>
                <span className="px-3 py-1 rounded-full bg-gray-100 text-gray-700 font-medium">
                  language: {result.language_detected || 'en'}
                </span>
                {typeof result.processing_ms === 'number' && (
                  <span className="px-3 py-1 rounded-full bg-gray-100 text-gray-700 font-medium">
                    {result.processing_ms} ms
                  </span>
                )}
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <h3 className="text-sm font-semibold text-green-700 mb-2">Matched Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {result.matched_skills?.length ? (
                      result.matched_skills.map((skill) => (
                        <span key={skill} className="px-2.5 py-1 rounded-md bg-green-100 text-green-800 text-xs font-medium">
                          {skill}
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-gray-500">No matched skills detected</span>
                    )}
                  </div>
                </div>

                <div>
                  <h3 className="text-sm font-semibold text-amber-700 mb-2">Missing Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {result.missing_skills?.length ? (
                      result.missing_skills.map((skill) => (
                        <span key={skill} className="px-2.5 py-1 rounded-md bg-amber-100 text-amber-800 text-xs font-medium">
                          {skill}
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-gray-500">No major skill gaps detected</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="rounded-lg border border-gray-200 p-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Detected Experience</h3>
                <p className="text-sm text-gray-600">
                  {typeof result.years_experience_detected === 'number'
                    ? `${result.years_experience_detected.toFixed(1)} years`
                    : 'Not detected'}
                </p>
              </div>

              <div className="rounded-lg border border-gray-200 p-4">
                <h3 className="text-sm font-semibold text-gray-700 mb-2">Flags</h3>
                <div className="flex flex-wrap gap-2">
                  {result.flags && Object.keys(result.flags).length > 0 ? (
                    Object.entries(result.flags).map(([key, value]) => (
                      <span
                        key={key}
                        className={`px-2.5 py-1 rounded-md text-xs font-medium ${
                          value ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {key}: {String(value)}
                      </span>
                    ))
                  ) : (
                    <span className="text-sm text-gray-500">No flags raised</span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
