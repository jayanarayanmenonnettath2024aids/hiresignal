import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { analyticsAPI } from '../api/client'

export default function Analytics() {
  const navigate = useNavigate()

  const { data: overview } = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: () => analyticsAPI.getOverview().then((r) => r.data),
  })

  const { data: trend } = useQuery({
    queryKey: ['analytics-trend'],
    queryFn: () => analyticsAPI.getScoreTrend().then((r) => r.data),
  })

  const { data: skills } = useQuery({
    queryKey: ['analytics-skills'],
    queryFn: () => analyticsAPI.getSkills().then((r) => r.data),
  })

  const avgRecent = useMemo(() => {
    if (!Array.isArray(trend) || trend.length === 0) return 0
    const values = trend.slice(-20).map((t: any) => t.score || 0)
    return values.reduce((a: number, b: number) => a + b, 0) / values.length
  }, [trend])

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold">Analytics</h1>
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 rounded-lg border border-gray-300 hover:bg-gray-100 text-sm font-medium"
          >
            Back to Dashboard
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl shadow p-5">
            <p className="text-sm text-gray-500">Total Jobs</p>
            <p className="text-3xl font-bold mt-1">{overview?.total_jobs ?? 0}</p>
          </div>
          <div className="bg-white rounded-xl shadow p-5">
            <p className="text-sm text-gray-500">Resumes Screened</p>
            <p className="text-3xl font-bold mt-1">{overview?.total_resumes_screened ?? 0}</p>
          </div>
          <div className="bg-white rounded-xl shadow p-5">
            <p className="text-sm text-gray-500">Average Match</p>
            <p className="text-3xl font-bold mt-1">{(((overview?.avg_match_score as number) || 0) * 100).toFixed(1)}%</p>
          </div>
          <div className="bg-white rounded-xl shadow p-5">
            <p className="text-sm text-gray-500">Recent Trend (20)</p>
            <p className="text-3xl font-bold mt-1">{(avgRecent * 100).toFixed(1)}%</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Top Matched Skills</h2>
            {skills?.top_matched_skills?.length ? (
              <div className="space-y-2">
                {skills.top_matched_skills.map((row: any) => (
                  <div key={row.skill} className="flex items-center justify-between rounded-lg bg-green-50 border border-green-100 px-3 py-2">
                    <span className="text-sm font-medium text-green-900">{row.skill}</span>
                    <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-700">{row.count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No matched skills data yet.</p>
            )}
          </div>

          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Top Missing Skills</h2>
            {skills?.top_missing_skills?.length ? (
              <div className="space-y-2">
                {skills.top_missing_skills.map((row: any) => (
                  <div key={row.skill} className="flex items-center justify-between rounded-lg bg-amber-50 border border-amber-100 px-3 py-2">
                    <span className="text-sm font-medium text-amber-900">{row.skill}</span>
                    <span className="text-xs px-2 py-1 rounded-full bg-amber-100 text-amber-700">{row.count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500">No missing skills data yet.</p>
            )}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Scores</h2>
          {Array.isArray(trend) && trend.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 lg:grid-cols-10 gap-2">
              {trend.slice(-30).map((point: any, idx: number) => {
                const pct = Math.max(0, Math.min(100, ((point.score || 0) * 100)))
                return (
                  <div key={`${point.date}-${idx}`} className="rounded border border-gray-200 p-2 bg-gray-50">
                    <p className="text-[11px] text-gray-500">#{idx + 1}</p>
                    <p className="text-sm font-semibold text-gray-900">{pct.toFixed(0)}%</p>
                  </div>
                )
              })}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No trend data available.</p>
          )}
        </div>
      </div>
    </div>
  )
}
