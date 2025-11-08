'use client'

import { useState } from 'react'
import { ChevronRight } from 'lucide-react'

interface QuizFormProps {
  onSubmit: (data: any) => void
}

export default function QuizForm({ onSubmit }: QuizFormProps) {
  const [formData, setFormData] = useState({
    career: '',
    current_education: 'hs' as 'hs' | 'some_college' | 'aa' | 'ba',
    gpa: 3.0,
    budget: 'medium' as 'low' | 'medium' | 'high',
    timeline: 'normal' as 'fast' | 'normal' | 'flexible',
    location: 'miami' as 'miami' | 'florida' | 'anywhere',
    goals: [] as string[],
    has_transfer_credits: false,
    veteran_status: false,
    work_schedule: 'full-time-student' as 'full-time-student' | 'part-time-student',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const handleGoalToggle = (goal: string) => {
    setFormData(prev => ({
      ...prev,
      goals: prev.goals.includes(goal)
        ? prev.goals.filter(g => g !== goal)
        : [...prev.goals, goal]
    }))
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-8 relative">
      {/* Question 1: Career */}
      <div className="space-y-3 animate-fade-in">
        <label className="block">
          <span className="text-lg font-bold text-white mb-2 block">
            1. What is your target career? <span className="text-red-400">*</span>
          </span>
          <select
            value={formData.career}
            onChange={(e) => setFormData({ ...formData, career: e.target.value })}
            className="w-full px-5 py-4 rounded-xl border-2 border-gray-600 bg-gray-700/50 text-white focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/20 outline-none transition-all text-lg shadow-sm hover:border-cyan-400 backdrop-blur-sm"
            required
          >
            <option value="">Select your dream career...</option>
            <option value="Mechanical Engineer">⚙️ Mechanical Engineer</option>
            <option value="Electrical Engineer">⚡ Electrical Engineer</option>
            <option value="Civil Engineer">🏗️ Civil Engineer</option>
            <option value="Software Developer">💻 Software Developer</option>
            <option value="Registered Nurse">🏥 Registered Nurse</option>
            <option value="Architect">🏛️ Architect</option>
            <option value="Accountant">💼 Accountant</option>
            <option value="Data Scientist">📊 Data Scientist</option>
          </select>
        </label>
      </div>

      {/* Question 2: Current Education */}
      <div className="space-y-3">
        <label className="block">
          <span className="text-lg font-bold text-white mb-2 block">
            2. Current education level <span className="text-red-400">*</span>
          </span>
          <select
            value={formData.current_education}
            onChange={(e) => setFormData({ ...formData, current_education: e.target.value as any })}
            className="w-full px-5 py-4 rounded-xl border-2 border-gray-600 bg-gray-700/50 text-white focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/20 outline-none transition-all text-lg shadow-sm hover:border-cyan-400 backdrop-blur-sm"
          >
            <option value="hs">🎓 High school graduate</option>
            <option value="some_college">📚 Some college credits</option>
            <option value="aa">🎖️ Associate's degree (AA/AS)</option>
            <option value="ba">🏆 Bachelor's degree</option>
          </select>
        </label>
      </div>

      {/* Question 3: GPA */}
      <div className="space-y-3">
        <label className="block">
          <span className="text-lg font-bold text-white mb-2 block">
            3. Current GPA
          </span>
          <div className="flex items-center gap-4">
            <input
              type="range"
              min="0"
              max="4"
              step="0.1"
              value={formData.gpa}
              onChange={(e) => setFormData({ ...formData, gpa: parseFloat(e.target.value) })}
              className="flex-1 h-3 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-6 [&::-webkit-slider-thumb]:h-6 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-cyan-400 [&::-webkit-slider-thumb]:shadow-lg [&::-webkit-slider-thumb]:shadow-cyan-500/50"
            />
            <div className="text-3xl font-bold text-cyan-400 min-w-[80px] text-center bg-gray-700/50 backdrop-blur-sm px-4 py-2 rounded-xl border border-cyan-500/30 shadow-lg shadow-cyan-500/20">
              {formData.gpa.toFixed(1)}
            </div>
          </div>
          <p className="text-sm text-gray-400 mt-2">0.0 - 4.0 scale</p>
        </label>
      </div>

      {/* Question 4: Budget */}
      <div className="space-y-3">
        <span className="text-lg font-bold text-white mb-3 block">
          4. Total education budget <span className="text-red-400">*</span>
        </span>
        <div className="grid md:grid-cols-3 gap-4">
          {[
            { value: 'low', icon: '💰', label: 'Under $30K', desc: 'Community college focus' },
            { value: 'medium', icon: '💰💰', label: '$30K - $80K', desc: 'Balanced approach' },
            { value: 'high', icon: '💰💰💰', label: 'Over $80K', desc: 'Prestige options' }
          ].map((option) => (
            <label
              key={option.value}
              className={`cursor-pointer group block p-5 rounded-xl border-2 transition-all hover:scale-105 ${
                formData.budget === option.value
                  ? 'border-cyan-500 bg-gradient-to-br from-cyan-700 to-blue-800 shadow-lg shadow-cyan-500/30'
                  : 'border-gray-600 bg-gray-700/30 hover:border-cyan-400 shadow-sm backdrop-blur-sm'
              }`}
            >
              <input
                type="radio"
                name="budget"
                value={option.value}
                checked={formData.budget === option.value}
                onChange={(e) => setFormData({ ...formData, budget: e.target.value as any })}
                className="sr-only"
              />
              <div className="text-3xl mb-2">{option.icon}</div>
              <div className="font-bold text-white">{option.label}</div>
              <div className="text-sm text-gray-400 mt-1">{option.desc}</div>
            </label>
          ))}
        </div>
      </div>

      {/* Question 5: Timeline */}
      <div className="space-y-3">
        <span className="text-lg font-bold text-white mb-3 block">
          5. Timeline preference
        </span>
        <div className="grid md:grid-cols-3 gap-4">
          {[
            { value: 'fast', icon: '⚡', label: 'Fastest', desc: '2-3 years' },
            { value: 'normal', icon: '📅', label: 'Standard', desc: '4 years' },
            { value: 'flexible', icon: '🕐', label: 'Flexible', desc: '5+ years' }
          ].map((option) => (
            <label
              key={option.value}
              className={`cursor-pointer block p-5 rounded-xl border-2 transition-all hover:scale-105 ${
                formData.timeline === option.value
                  ? 'border-purple-500 bg-gradient-to-br from-purple-700 to-pink-800 shadow-lg shadow-purple-500/30'
                  : 'border-gray-600 bg-gray-700/30 backdrop-blur-sm hover:border-purple-400 shadow-sm'
              }`}
            >
              <input
                type="radio"
                name="timeline"
                value={option.value}
                checked={formData.timeline === option.value}
                onChange={(e) => setFormData({ ...formData, timeline: e.target.value as any })}
                className="sr-only"
              />
              <div className="text-3xl mb-2">{option.icon}</div>
              <div className="font-bold text-white">{option.label}</div>
              <div className="text-sm text-gray-400 mt-1">{option.desc}</div>
            </label>
          ))}
        </div>
      </div>

      {/* Question 6: Location */}
      <div className="space-y-3">
        <label className="block">
          <span className="text-lg font-bold text-white mb-2 block">
            6. Where are you willing to study?
          </span>
          <select
            value={formData.location}
            onChange={(e) => setFormData({ ...formData, location: e.target.value as any })}
            className="w-full px-5 py-4 rounded-xl border-2 border-gray-600 bg-gray-700/50 text-white focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/20 outline-none transition-all text-lg shadow-sm hover:border-cyan-400 backdrop-blur-sm"
          >
            <option value="miami">🏖️ Must stay in Miami</option>
            <option value="florida">🌴 Anywhere in Florida</option>
            <option value="anywhere">🌎 Open to out-of-state</option>
          </select>
        </label>
      </div>

      {/* Question 7: Work Schedule */}
      <div className="space-y-3">
        <label className="block">
          <span className="text-lg font-bold text-white mb-2 block">
            7. Work schedule
          </span>
          <select
            value={formData.work_schedule}
            onChange={(e) => setFormData({ ...formData, work_schedule: e.target.value as any })}
            className="w-full px-5 py-4 rounded-xl border-2 border-gray-600 bg-gray-700/50 text-white focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/20 outline-none transition-all text-lg shadow-sm hover:border-cyan-400 backdrop-blur-sm"
          >
            <option value="full-time-student">👨‍🎓 Full-time student (not working)</option>
            <option value="part-time-student">💼 Part-time student (working full-time)</option>
          </select>
        </label>
      </div>

      {/* Question 8 & 9: Checkboxes */}
      <div className="space-y-4">
        <label className="flex items-start gap-3 cursor-pointer group p-4 rounded-xl border-2 border-gray-600 bg-gray-700/30 hover:border-cyan-400 hover:bg-gray-700/50 transition-all backdrop-blur-sm">
          <input
            type="checkbox"
            checked={formData.has_transfer_credits}
            onChange={(e) => setFormData({ ...formData, has_transfer_credits: e.target.checked })}
            className="mt-1 w-5 h-5 text-cyan-500 rounded border-gray-500 bg-gray-700 focus:ring-cyan-500 focus:ring-offset-gray-800"
          />
          <div>
            <span className="font-semibold text-white">I have existing college transfer credits</span>
            <p className="text-sm text-gray-400">This may shorten your path</p>
          </div>
        </label>

        <label className="flex items-start gap-3 cursor-pointer group p-4 rounded-xl border-2 border-gray-600 bg-gray-700/30 hover:border-cyan-400 hover:bg-gray-700/50 transition-all backdrop-blur-sm">
          <input
            type="checkbox"
            checked={formData.veteran_status}
            onChange={(e) => setFormData({ ...formData, veteran_status: e.target.checked })}
            className="mt-1 w-5 h-5 text-cyan-500 rounded border-gray-500 bg-gray-700 focus:ring-cyan-500 focus:ring-offset-gray-800"
          />
          <div>
            <span className="font-semibold text-white">I am a veteran or active military</span>
            <p className="text-sm text-gray-400">You may be eligible for GI Bill benefits</p>
          </div>
        </label>
      </div>

      {/* Question 10: Career Goals */}
      <div className="space-y-3">
        <span className="text-lg font-bold text-white mb-3 block">
          10. Career goals (select all that apply)
        </span>
        <div className="grid md:grid-cols-2 gap-3">
          {[
            { value: 'internship', label: '💼 Internship experience' },
            { value: 'research', label: '🔬 Research opportunities' },
            { value: 'masters', label: '🎓 Master\'s degree' },
            { value: 'phd', label: '👨‍🔬 PhD program' },
            { value: 'PE_license', label: '⚖️ Professional license' },
            { value: 'startup', label: '🚀 Start my own business' }
          ].map((goal) => (
            <label
              key={goal.value}
              className={`cursor-pointer flex items-center gap-3 p-4 rounded-xl border-2 transition-all hover:scale-105 ${
                formData.goals.includes(goal.value)
                  ? 'border-purple-500 bg-gradient-to-br from-purple-700 to-pink-800 shadow-lg shadow-purple-500/30'
                  : 'border-gray-600 bg-gray-700/30 hover:border-purple-400 shadow-sm backdrop-blur-sm'
              }`}
            >
              <input
                type="checkbox"
                checked={formData.goals.includes(goal.value)}
                onChange={() => handleGoalToggle(goal.value)}
                className="w-5 h-5 text-purple-500 rounded border-gray-500 bg-gray-700 focus:ring-purple-500 focus:ring-offset-gray-800"
              />
              <span className="font-medium text-white">{goal.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        className="w-full bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-500 text-white font-bold text-xl px-8 py-5 rounded-xl shadow-xl shadow-cyan-500/30 hover:shadow-2xl hover:shadow-cyan-500/50 transition-all duration-200 hover:scale-105 flex items-center justify-center gap-3 group relative overflow-hidden"
      >
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <span className="relative z-10">Generate My Roadmap</span>
        <ChevronRight className="w-6 h-6 group-hover:translate-x-1 transition-transform relative z-10" />
      </button>

      <p className="text-center text-sm text-gray-400">
        This usually takes 10-30 seconds ⏱️
      </p>
    </form>
  )
}
