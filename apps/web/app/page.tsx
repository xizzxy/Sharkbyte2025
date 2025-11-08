'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Sparkles, ArrowRight, Loader2, GraduationCap, TrendingUp, DollarSign } from 'lucide-react'
import QuizForm from '@/components/QuizForm'

export default function HomePage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleQuizSubmit = async (quizData: any) => {
    setLoading(true)
    setError('')

    try {
      // Call the API
      const apiUrl = process.env.NEXT_PUBLIC_WORKER_API_URL || 'http://localhost:8000/api/plan'

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quiz_data: quizData })
      })

      if (!response.ok) {
        throw new Error('Failed to generate roadmap')
      }

      const data = await response.json()

      console.log('[HomePage] Backend response:', data)
      console.log('[HomePage] Roadmap data:', data.roadmap)

      if (!data.success) {
        throw new Error(data.error || 'Failed to generate roadmap')
      }

      // Store roadmap in sessionStorage to avoid URL length limits
      const roadmapJson = JSON.stringify(data.roadmap)
      sessionStorage.setItem('careerpilot_roadmap', roadmapJson)
      console.log('[HomePage] Stored roadmap in sessionStorage')
      console.log('[HomePage] Verify storage - length:', roadmapJson.length)
      console.log('[HomePage] Verify storage - read back:', sessionStorage.getItem('careerpilot_roadmap')?.substring(0, 100))

      // Navigate to roadmap page
      router.push('/roadmap')

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-slate-900 to-black relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
        <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
      </div>

      {/* Hero Header */}
      <div className="relative overflow-hidden">
        <div className="relative container mx-auto px-4 py-12 text-center">
          <div className="inline-flex items-center gap-2 bg-gradient-to-r from-cyan-600/20 to-purple-600/20 backdrop-blur-xl px-4 py-2 rounded-full border border-cyan-500/30 shadow-lg shadow-cyan-500/20 mb-6 animate-fade-in">
            <Sparkles className="w-5 h-5 text-cyan-400 animate-pulse" />
            <span className="text-sm font-semibold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
              Powered by AI
            </span>
          </div>

          <h1 className="text-6xl md:text-8xl font-black mb-6 animate-slide-up drop-shadow-2xl">
            <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-500 bg-clip-text text-transparent">
              CareerPilot AI
            </span>
          </h1>

          <p className="text-xl md:text-2xl text-gray-300 mb-4 max-w-3xl mx-auto font-medium animate-fade-in drop-shadow-lg">
            Your personalized roadmap from <span className="text-cyan-400 font-bold">Miami Dade College</span> to your dream career
          </p>

          <p className="text-gray-400 max-w-2xl mx-auto mb-8 animate-fade-in">
            Get AI-powered recommendations for programs, transfer universities, costs, and career outcomes in minutes.
          </p>

          {/* Quick Stats */}
          <div className="flex flex-wrap justify-center gap-8 mb-12 animate-slide-up">
            <div className="flex items-center gap-3 bg-gray-800/40 backdrop-blur-xl px-6 py-3 rounded-2xl border border-cyan-500/20 shadow-lg hover:shadow-cyan-500/30 transition-all hover:scale-105">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/50">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
              <div className="text-left">
                <div className="text-sm text-gray-400">Programs</div>
                <div className="text-2xl font-bold text-white">50+</div>
              </div>
            </div>
            <div className="flex items-center gap-3 bg-gray-800/40 backdrop-blur-xl px-6 py-3 rounded-2xl border border-blue-500/20 shadow-lg hover:shadow-blue-500/30 transition-all hover:scale-105">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/50">
                <DollarSign className="w-6 h-6 text-white" />
              </div>
              <div className="text-left">
                <div className="text-sm text-gray-400">Avg Savings</div>
                <div className="text-2xl font-bold text-white">$40K+</div>
              </div>
            </div>
            <div className="flex items-center gap-3 bg-gray-800/40 backdrop-blur-xl px-6 py-3 rounded-2xl border border-purple-500/20 shadow-lg hover:shadow-purple-500/30 transition-all hover:scale-105">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-500/50">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div className="text-left">
                <div className="text-sm text-gray-400">Career Paths</div>
                <div className="text-2xl font-bold text-white">100+</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quiz Section */}
      <div className="container mx-auto px-4 pb-20 relative">
        <div className="max-w-4xl mx-auto">
          {/* Progress Indicator */}
          <div className="mb-8 text-center animate-fade-in">
            <div className="inline-flex items-center gap-2 bg-gray-800/60 backdrop-blur-xl px-6 py-3 rounded-full border border-gray-700 shadow-lg">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white flex items-center justify-center font-bold text-sm shadow-lg shadow-cyan-500/50">
                1
              </div>
              <ArrowRight className="w-4 h-4 text-gray-500" />
              <div className="w-8 h-8 rounded-full bg-gray-700 text-gray-400 flex items-center justify-center font-bold text-sm">
                2
              </div>
              <ArrowRight className="w-4 h-4 text-gray-500" />
              <div className="w-8 h-8 rounded-full bg-gray-700 text-gray-400 flex items-center justify-center font-bold text-sm">
                3
              </div>
            </div>
            <p className="text-sm text-gray-400 mt-3">Answer questions → AI analyzes → Get your roadmap</p>
          </div>

          {/* Quiz Card */}
          <div className="bg-gray-800/60 backdrop-blur-xl rounded-3xl shadow-2xl p-8 md:p-12 border border-gray-700 animate-slide-up relative overflow-hidden">
            {/* Card Glow Effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-blue-500/10 to-purple-500/10 opacity-50"></div>

            <div className="mb-8 relative">
              <h2 className="text-3xl font-bold mb-2 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent drop-shadow-lg">
                Tell us about yourself
              </h2>
              <p className="text-gray-400">
                We'll use AI to create your personalized career roadmap
              </p>
            </div>

            {loading ? (
              <div className="py-20 text-center relative">
                <div className="inline-block">
                  <Loader2 className="w-16 h-16 animate-spin text-cyan-400 mb-4 drop-shadow-lg" />
                  <h3 className="text-2xl font-bold mb-2 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent drop-shadow-lg">
                    Generating your roadmap...
                  </h3>
                  <p className="text-gray-400">Our AI agents are researching the best paths for you</p>
                  <div className="mt-6 space-y-2 text-sm text-gray-400">
                    <div className="flex items-center justify-center gap-2 animate-fade-in">
                      <div className="w-2 h-2 bg-cyan-500 rounded-full animate-pulse shadow-lg shadow-cyan-500/50"></div>
                      <span>Analyzing your profile...</span>
                    </div>
                    <div className="flex items-center justify-center gap-2 animate-fade-in" style={{animationDelay: '200ms'}}>
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse shadow-lg shadow-blue-500/50"></div>
                      <span>Researching MDC programs...</span>
                    </div>
                    <div className="flex items-center justify-center gap-2 animate-fade-in" style={{animationDelay: '400ms'}}>
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse shadow-lg shadow-purple-500/50"></div>
                      <span>Calculating costs & ROI...</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <>
                {error && (
                  <div className="mb-6 bg-red-900/40 backdrop-blur-sm border-2 border-red-500/50 rounded-xl p-4 text-red-200 animate-fade-in relative">
                    <p className="font-semibold">⚠️ Oops! Something went wrong</p>
                    <p className="text-sm mt-1 text-red-300">{error}</p>
                    <button
                      onClick={() => setError('')}
                      className="mt-2 text-sm underline hover:no-underline text-red-300"
                    >
                      Try again
                    </button>
                  </div>
                )}

                <div className="relative">
                  <QuizForm onSubmit={handleQuizSubmit} />
                </div>
              </>
            )}
          </div>

          {/* Trust Indicators */}
          <div className="mt-12 text-center text-sm text-gray-400 animate-fade-in">
            <p className="mb-2">✨ Powered by Google Vertex AI • Real data from BLS.gov & College Scorecard</p>
            <p className="flex items-center justify-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></span>
              Your data is secure and never shared
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
