import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './hooks/useAuth'
import Login from './components/Login'
import Register from './components/Register'
import Dashboard from './components/Dashboard'
import ExperienceMap from './components/ExperienceMap'
import ExperienceDetails from './components/ExperienceDetails'
import Profile from './components/Profile'
import AdminPanel from './components/AdminPanel'
import Navigation from './components/Navigation'
import { Toaster } from '@/components/ui/sonner'
import './App.css'

function AppContent() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <Router>
        {user && <Navigation />}
        <main className={user ? 'pt-16' : ''}>
          <Routes>
            {!user ? (
              <>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="*" element={<Navigate to="/login" replace />} />
              </>
            ) : (
              <>
                <Route path="/" element={<Dashboard />} />
                <Route path="/map" element={<ExperienceMap />} />
                <Route path="/experience/:id" element={<ExperienceDetails />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/admin" element={<AdminPanel />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </>
            )}
          </Routes>
        </main>
        <Toaster />
      </Router>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App

