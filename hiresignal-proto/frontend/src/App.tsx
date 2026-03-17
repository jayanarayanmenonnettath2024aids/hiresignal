import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/auth.ts'
import Login from './pages/Login.tsx'
import Dashboard from './pages/Dashboard.tsx'
import NewJob from './pages/NewJob.tsx'
import JobDetail from './pages/JobDetail.tsx'
import SingleScreen from './pages/SingleScreen.tsx'
import Analytics from './pages/Analytics.tsx'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore()
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  const { token } = useAuthStore()

  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={token ? <Dashboard /> : <Navigate to="/login" replace />} />
        <Route path="/jobs/new" element={<ProtectedRoute><NewJob /></ProtectedRoute>} />
        <Route path="/jobs/:jobId" element={<ProtectedRoute><JobDetail /></ProtectedRoute>} />
        <Route path="/screen" element={<ProtectedRoute><SingleScreen /></ProtectedRoute>} />
        <Route path="/analytics" element={<ProtectedRoute><Analytics /></ProtectedRoute>} />
      </Routes>
    </Router>
  )
}
