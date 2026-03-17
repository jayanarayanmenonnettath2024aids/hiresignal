import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { jobsAPI } from '../api/client'

export default function NewJob() {
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [jdText, setJdText] = useState('')
  const [topN, setTopN] = useState(5)
  const [weightSemantic, setWeightSemantic] = useState(0.4)
  const [weightTfidf, setWeightTfidf] = useState(0.25)
  const [weightSkills, setWeightSkills] = useState(0.25)
  const [weightExperience, setWeightExperience] = useState(0.1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const weightSum = useMemo(
    () => weightSemantic + weightTfidf + weightSkills + weightExperience,
    [weightSemantic, weightTfidf, weightSkills, weightExperience],
  )

  async function createJob(e: React.FormEvent) {
    e.preventDefault()
    setError('')

    if (!title.trim()) {
      setError('Title is required.')
      return
    }

    if (!jdText.trim()) {
      setError('Job description is required.')
      return
    }

    if (Math.abs(weightSum - 1) > 0.001) {
      setError('Weights must sum to 1.0.')
      return
    }

    setLoading(true)
    try {
      const response = await jobsAPI.create({
        title,
        jd_text: jdText,
        top_n: topN,
        weights: {
          weight_semantic: weightSemantic,
          weight_tfidf: weightTfidf,
          weight_skills: weightSkills,
          weight_experience: weightExperience,
        },
      })
      navigate(`/jobs/${response.data.id}`)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create job.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">New Screening Job</h1>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-100 text-sm font-medium"
          >
            Back to Dashboard
          </button>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <form onSubmit={createJob} className="bg-white rounded-xl shadow p-6 space-y-5">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Job Title</label>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Senior Python Backend Engineer"
              className="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Job Description</label>
            <textarea
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              rows={12}
              placeholder="Paste complete JD text..."
              className="w-full rounded-lg border border-gray-300 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Top N</label>
              <input
                type="number"
                min={1}
                max={50}
                value={topN}
                onChange={(e) => setTopN(Number(e.target.value) || 5)}
                className="w-full rounded-lg border border-gray-300 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="rounded-lg border border-gray-200 bg-gray-50 px-4 py-2.5 flex items-center justify-between">
              <span className="text-sm font-medium text-gray-600">Weights Sum</span>
              <span className={`text-sm font-bold ${Math.abs(weightSum - 1) < 0.001 ? 'text-green-600' : 'text-red-600'}`}>
                {weightSum.toFixed(2)}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Semantic Weight</label>
              <input
                type="number"
                step="0.05"
                min={0}
                max={1}
                value={weightSemantic}
                onChange={(e) => setWeightSemantic(Number(e.target.value))}
                className="w-full rounded-lg border border-gray-300 px-4 py-2.5"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">TF-IDF Weight</label>
              <input
                type="number"
                step="0.05"
                min={0}
                max={1}
                value={weightTfidf}
                onChange={(e) => setWeightTfidf(Number(e.target.value))}
                className="w-full rounded-lg border border-gray-300 px-4 py-2.5"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Skills Weight</label>
              <input
                type="number"
                step="0.05"
                min={0}
                max={1}
                value={weightSkills}
                onChange={(e) => setWeightSkills(Number(e.target.value))}
                className="w-full rounded-lg border border-gray-300 px-4 py-2.5"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Experience Weight</label>
              <input
                type="number"
                step="0.05"
                min={0}
                max={1}
                value={weightExperience}
                onChange={(e) => setWeightExperience(Number(e.target.value))}
                className="w-full rounded-lg border border-gray-300 px-4 py-2.5"
              />
            </div>
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
            {loading ? 'Creating...' : 'Create Job'}
          </button>
        </form>
      </div>
    </div>
  )
}
