'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ChevronRight, Loader2, Cog, Zap, Building2, Code, Heart, Building, Briefcase, BarChart3, DollarSign, Calendar, Clock, MapPin, Globe, Trophy } from 'lucide-react'

interface QuizFormData {
  career: string
  current_education: 'hs' | 'some_college' | 'aa' | 'ba'
  gpa: number
  budget: 'low' | 'medium' | 'high'
  timeline: 'fast' | 'normal' | 'flexible'
  location: 'miami' | 'florida' | 'anywhere'
  goals: string[]
  has_transfer_credits: boolean
  veteran_status: boolean
  work_schedule: 'full-time-student' | 'part-time-student'
  learning_preferences: string[]
  priority: string
}

export default function QuizPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const [formData, setFormData] = useState<QuizFormData>({
    career: '',
    current_education: 'hs',
    gpa: 3.0,
    budget: 'medium',
    timeline: 'normal',
    location: 'miami',
    goals: [],
    has_transfer_credits: false,
    veteran_status: false,
    work_schedule: 'full-time-student',
    learning_preferences: [],
    priority: 'cost'
  })

  const handleCheckboxChange = (field: 'goals' | 'learning_preferences', value: string) => {
    const current = formData[field]
    const updated = current.includes(value)
      ? current.filter(item => item !== value)
      : [...current, value]
    setFormData({ ...formData, [field]: updated })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      // Call the API (Worker or direct to Python)
      const apiUrl = process.env.NEXT_PUBLIC_WORKER_API_URL || 'http://localhost:8000/api/plan'

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quiz_data: formData })
      })

      if (!response.ok) {
        throw new Error('Failed to generate roadmap')
      }

      const data = await response.json()

      console.log('[Quiz] Backend response:', data)
      console.log('[Quiz] Roadmap data:', data.roadmap)

      if (!data.success) {
        throw new Error(data.error || 'Failed to generate roadmap')
      }

      // Store roadmap in sessionStorage to avoid URL length limits
      const roadmapJson = JSON.stringify(data.roadmap)
      sessionStorage.setItem('careerpilot_roadmap', roadmapJson)
      console.log('[Quiz] Stored roadmap in sessionStorage')
      console.log('[Quiz] Verify storage - length:', roadmapJson.length)
      console.log('[Quiz] Verify storage - read back:', sessionStorage.getItem('careerpilot_roadmap')?.substring(0, 100))

      // Small delay to ensure storage is written before navigation
      setTimeout(() => {
        router.push('/roadmap')
      }, 100)

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen py-12">
      <div className="container mx-auto px-4 max-w-3xl">
        <div className="text-center mb-12 animate-fade-in">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4">
            Career Planning Quiz
          </h1>
          <p className="text-gray-600">
            Answer these questions to get your personalized roadmap
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="card animate-slide-up">
            {/* Question 1: Career Goal */}
            <div className="mb-6">
              <label className="label-field">
                1. What is your target career? *
              </label>
              <select
                value={formData.career}
                onChange={(e) => setFormData({ ...formData, career: e.target.value })}
                className="input-field"
                required
              >
                <option value="">Select a career...</option>
                <option value="Mechanical Engineer">Mechanical Engineer</option>
                <option value="Electrical Engineer">Electrical Engineer</option>
                <option value="Civil Engineer">Civil Engineer</option>
                <option value="Software Developer">Software Developer</option>
                <option value="Registered Nurse">Registered Nurse</option>
                <option value="Architect">Architect</option>
                <option value="Accountant">Accountant</option>
                <option value="Data Scientist">Data Scientist</option>
              </select>
            </div>

            {/* Question 2: Current Education */}
            <div className="mb-6">
              <label className="label-field">
                2. What is your current education level? *
              </label>
              <select
                value={formData.current_education}
                onChange={(e) => setFormData({ ...formData, current_education: e.target.value as any })}
                className="input-field"
              >
                <option value="hs">High school graduate</option>
                <option value="some_college">Some college credits</option>
                <option value="aa">Associate's degree (AA/AS)</option>
                <option value="ba">Bachelor's degree</option>
              </select>
            </div>

            {/* Question 3: GPA */}
            <div className="mb-6">
              <label className="label-field">
                3. What is your current GPA? *
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="4"
                value={formData.gpa}
                onChange={(e) => setFormData({ ...formData, gpa: parseFloat(e.target.value) })}
                className="input-field"
                required
              />
              <p className="text-sm text-gray-500 mt-1">0.0 - 4.0 scale</p>
            </div>

            {/* Question 4: Budget */}
            <div className="mb-6">
              <label className="label-field">
                4. What is your total education budget? *
              </label>
              <div className="space-y-2">
                <label className="flex items-center p-3 border-2 rounded-lg cursor-pointer hover:border-blue-400 transition">
                  <input
                    type="radio"
                    name="budget"
                    value="low"
                    checked={formData.budget === 'low'}
                    onChange={(e) => setFormData({ ...formData, budget: e.target.value as any })}
                    className="mr-3"
                  />
                  <DollarSign className="w-5 h-5 text-cyan-400 mr-2" />
                  <span className="font-medium">Under $30,000 (Low)</span>
                </label>
                <label className="flex items-center p-3 border-2 rounded-lg cursor-pointer hover:border-blue-400 transition">
                  <input
                    type="radio"
                    name="budget"
                    value="medium"
                    checked={formData.budget === 'medium'}
                    onChange={(e) => setFormData({ ...formData, budget: e.target.value as any })}
                    className="mr-3"
                  />
                  <DollarSign className="w-5 h-5 text-cyan-400 mr-2" />
                  <span className="font-medium">$30,000 - $80,000 (Medium)</span>
                </label>
                <label className="flex items-center p-3 border-2 rounded-lg cursor-pointer hover:border-blue-400 transition">
                  <input
                    type="radio"
                    name="budget"
                    value="high"
                    checked={formData.budget === 'high'}
                    onChange={(e) => setFormData({ ...formData, budget: e.target.value as any })}
                    className="mr-3"
                  />
                  <DollarSign className="w-5 h-5 text-cyan-400 mr-2" />
                  <span className="font-medium">Over $80,000 (High)</span>
                </label>
              </div>
            </div>

            {/* Question 5: Timeline */}
            <div className="mb-6">
              <label className="label-field">
                5. What is your timeline preference? *
              </label>
              <select
                value={formData.timeline}
                onChange={(e) => setFormData({ ...formData, timeline: e.target.value as any })}
                className="input-field"
              >
                <option value="fast">Fastest path possible (2-3 years)</option>
                <option value="normal">Standard timeline (4 years)</option>
                <option value="flexible">Flexible, can take longer (5+ years)</option>
              </select>
            </div>

            {/* Question 6: Location */}
            <div className="mb-6">
              <label className="label-field">
                6. Where are you willing to study? *
              </label>
              <select
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value as any })}
                className="input-field"
              >
                <option value="miami">Must stay in Miami</option>
                <option value="florida">Anywhere in Florida</option>
                <option value="anywhere">Open to out-of-state</option>
              </select>
            </div>

            {/* Question 7: Work Schedule */}
            <div className="mb-6">
              <label className="label-field">
                7. What is your work schedule? *
              </label>
              <select
                value={formData.work_schedule}
                onChange={(e) => setFormData({ ...formData, work_schedule: e.target.value as any })}
                className="input-field"
              >
                <option value="full-time-student">Full-time student (not working)</option>
                <option value="part-time-student">Part-time student (working full-time)</option>
              </select>
            </div>

            {/* Question 8: Transfer Credits */}
            <div className="mb-6">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.has_transfer_credits}
                  onChange={(e) => setFormData({ ...formData, has_transfer_credits: e.target.checked })}
                  className="mr-3 w-5 h-5"
                />
                <span className="label-field mb-0">
                  8. I have existing college transfer credits
                </span>
              </label>
            </div>

            {/* Question 9: Veteran Status */}
            <div className="mb-6">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.veteran_status}
                  onChange={(e) => setFormData({ ...formData, veteran_status: e.target.checked })}
                  className="mr-3 w-5 h-5"
                />
                <span className="label-field mb-0">
                  9. I am a veteran or active military (GI Bill eligible)
                </span>
              </label>
            </div>

            {/* Question 10: Career Goals */}
            <div className="mb-6">
              <label className="label-field">
                10. What are your career goals? (Select all that apply)
              </label>
              <div className="space-y-2">
                {['internship', 'research', 'masters', 'phd', 'PE_license', 'startup'].map(goal => (
                  <label key={goal} className="flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.goals.includes(goal)}
                      onChange={() => handleCheckboxChange('goals', goal)}
                      className="mr-3 w-5 h-5"
                    />
                    <span className="capitalize">{goal.replace('_', ' ')}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Question 11: Learning Preferences */}
            <div className="mb-6">
              <label className="label-field">
                11. What are your learning preferences? (Select all that apply)
              </label>
              <div className="space-y-2">
                {['hands-on', 'theory', 'online', 'in-person'].map(pref => (
                  <label key={pref} className="flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.learning_preferences.includes(pref)}
                      onChange={() => handleCheckboxChange('learning_preferences', pref)}
                      className="mr-3 w-5 h-5"
                    />
                    <span className="capitalize">{pref.replace('-', ' ')}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Question 12: Priority */}
            <div className="mb-6">
              <label className="label-field">
                12. What is your top priority?
              </label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                className="input-field"
              >
                <option value="cost">Lowest cost</option>
                <option value="speed">Fastest completion</option>
                <option value="prestige">School reputation</option>
              </select>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4 text-red-700">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full text-lg flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Generating your roadmap...
              </>
            ) : (
              <>
                Generate My Roadmap
                <ChevronRight className="w-5 h-5" />
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
