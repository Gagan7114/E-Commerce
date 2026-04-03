import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import PlatformLayout from './layouts/PlatformLayout'
import PlatformDashboard from './pages/platform/PlatformDashboard'
import PlatformPO from './pages/platform/PlatformPO'
import PlatformTruckLoading from './pages/platform/PlatformTruckLoading'
import PlatformDispatches from './pages/platform/PlatformDispatches'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/platform/:slug"
            element={
              <ProtectedRoute>
                <PlatformLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<PlatformDashboard />} />
            <Route path="po" element={<PlatformPO />} />
            <Route path="truck-loading" element={<PlatformTruckLoading />} />
            <Route path="dispatches" element={<PlatformDispatches />} />
          </Route>
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
