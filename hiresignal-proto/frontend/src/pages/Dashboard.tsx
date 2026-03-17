import { useQuery } from '@tanstack/react-query'
import { jobsAPI, analyticsAPI } from '../api/client'
import { useNavigate } from 'react-router-dom'

export default function Dashboard() {
  const navigate = useNavigate()
  
  const { data: jobs, isLoading } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => jobsAPI.list().then((r) => r.data),
  })

  const { data: overview } = useQuery({
    queryKey: ['overview'],
    queryFn: () => analyticsAPI.getOverview().then((r) => r.data),
  })

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold">HireSignal Dashboard</h1>
          <button
            onClick={() => navigate('/jobs/new')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            + New Screening
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        {overview && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm">Jobs This Month</p>
              <p className="text-3xl font-bold">{overview.total_jobs}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm">Resumes Screened</p>
              <p className="text-3xl font-bold">{overview.total_resumes_screened}</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm">Avg Match Score</p>
              <p className="text-3xl font-bold">{(overview.avg_match_score * 100).toFixed(0)}%</p>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <p className="text-gray-600 text-sm">Quota Remaining</p>
              <p className="text-3xl font-bold">490</p>
            </div>
          </div>
        )}

        {/* Jobs Table */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold">Recent Screening Jobs</h2>
          </div>

          {isLoading ? (
            <div className="p-6 text-center text-gray-600">Loading...</div>
          ) : jobs && jobs.length > 0 ? (
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Title</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Progress</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Created</th>
                  <th className="px-6 py-3 text-right text-sm font-semibold text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {jobs.map((job: any) => (
                  <tr key={job.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => navigate(`/jobs/${job.id}`)}>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{job.title}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        job.status === 'done' ? 'bg-green-100 text-green-800' :
                        job.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {job.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {job.total_processed}/{job.total_submitted}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {new Date(job.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 text-right text-sm">
                      <button className="text-blue-600 hover:text-blue-800">View</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-6 text-center text-gray-600">
              No screening jobs yet. Create one to get started!
            </div>
          )}
        </div>

        {/* Quick action buttons */}
        <div className="mt-8 flex gap-4 justify-center">
          <button
            onClick={() => navigate('/screen')}
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-2 rounded-lg"
          >
            Quick Single Screen
          </button>
          <button
            onClick={() => navigate('/analytics')}
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-2 rounded-lg"
          >
            View Analytics
          </button>
        </div>
      </div>
    </div>
  )
}
