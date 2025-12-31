'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

interface HealthStatus {
  status: string
  service: string
}

export default function Home() {
  const router = useRouter()
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setHealth(data))
      .catch(err => setError('Backend not available'))
  }, [])

  return (
    <main className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-bold text-gray-800">StakeholderSim</h1>
          <nav className="flex gap-4">
            <a href="/dashboard" className="text-gray-600 hover:text-gray-800">Dashboard</a>
            <a href="/assignments" className="text-gray-600 hover:text-gray-800">Assignments</a>
            <a href="/scenarios" className="text-gray-600 hover:text-gray-800">Practice</a>
            <a href="/instructor" className="text-indigo-600 hover:text-indigo-800">Instructor</a>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            Master Stakeholder Communication
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Practice presenting your data science work to AI-powered stakeholder personas.
            Get realistic feedback without the pressure of real meetings.
          </p>
        </div>

        {/* Development Warning */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-8 max-w-2xl mx-auto">
          <p className="text-sm text-yellow-700">
            <strong>Development Mode</strong> - Using mock authentication.
            See PRE_DEPLOYMENT_CHECKLIST.md before production.
          </p>
        </div>

        {/* CTA Buttons */}
        <div className="flex justify-center gap-4 mb-16">
          <button
            onClick={() => router.push('/scenarios')}
            className="bg-blue-500 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-blue-600 shadow-lg hover:shadow-xl transition-all"
          >
            Start Practicing
          </button>
          <button
            onClick={() => router.push('/history')}
            className="bg-white text-gray-700 px-8 py-3 rounded-lg text-lg font-semibold hover:bg-gray-50 border border-gray-300"
          >
            View History
          </button>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white rounded-lg p-6 shadow-md">
            <div className="text-3xl mb-4">🎭</div>
            <h3 className="text-lg font-semibold mb-2">Realistic Personas</h3>
            <p className="text-gray-600">
              Practice with 6 different stakeholder types - from skeptical VPs to
              budget-conscious CFOs.
            </p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-md">
            <div className="text-3xl mb-4">🔄</div>
            <h3 className="text-lg font-semibold mb-2">Unlimited Practice</h3>
            <p className="text-gray-600">
              No embarrassment, no judgment. Practice as many times as you need to
              build confidence.
            </p>
          </div>
          <div className="bg-white rounded-lg p-6 shadow-md">
            <div className="text-3xl mb-4">📊</div>
            <h3 className="text-lg font-semibold mb-2">Detailed Feedback</h3>
            <p className="text-gray-600">
              Get graded against a professional rubric with specific feedback for
              improvement.
            </p>
          </div>
        </div>

        {/* System Status */}
        <div className="max-w-md mx-auto">
          <div className="bg-white rounded-lg p-4 shadow-md">
            <h3 className="text-sm font-medium text-gray-500 mb-2">System Status</h3>
            {error ? (
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                <span className="text-red-600">{error}</span>
              </div>
            ) : health ? (
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                <span className="text-green-600">
                  All systems operational
                </span>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></span>
                <span className="text-gray-500">Checking...</span>
              </div>
            )}

            {/* Dev Links */}
            <div className="mt-4 pt-4 border-t flex gap-4 text-sm">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 hover:underline"
              >
                API Docs
              </a>
              <a
                href="http://localhost:8000/api/v1/auth/mock-users"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 hover:underline"
              >
                Mock Users
              </a>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
