'use client'

import { Suspense, useState, useEffect } from 'react'
import { useSearchParams } from 'next/navigation'
import { DollarSign, Clock, TrendingUp, Download, Share2, BookOpen, Sparkles, ArrowLeft, CheckCircle2, PiggyBank, Zap, Trophy, BarChart3 } from 'lucide-react'
import RoadmapGraph from '@/components/RoadmapGraph'
import FloatingChatButton from '@/components/FloatingChatButton'
import ChatWidget from '@/components/ChatWidget'
import Link from 'next/link'

function RoadmapContent() {
  const [roadmapData, setRoadmapData] = useState<any>(null)
  const [selectedPath, setSelectedPath] = useState<'cheapest' | 'fastest' | 'prestige'>('cheapest')
  const [isLoading, setIsLoading] = useState(true)
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [sidebarWidth, setSidebarWidth] = useState(384) // 96 * 4 = 384px (w-96)
  const [isResizing, setIsResizing] = useState(false)
  const [chatButtonPosition, setChatButtonPosition] = useState({ x: 0, y: 0 })

  // Handle sidebar resize
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isResizing) {
        const newWidth = e.clientX
        setSidebarWidth(Math.max(280, Math.min(newWidth, 600)))
      }
    }

    const handleMouseUp = () => {
      setIsResizing(false)
    }

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
      return () => {
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isResizing])

  // Load roadmap data from sessionStorage on mount
  useEffect(() => {
    setIsLoading(true)
    console.log('[Roadmap] useEffect triggered')

    try {
      // Get data from sessionStorage ONLY
      const storedData = sessionStorage.getItem('careerpilot_roadmap')
      console.log('[Roadmap] sessionStorage check:', storedData ? `Found ${storedData.length} chars` : 'NOT FOUND')

      if (storedData) {
        console.log('[Roadmap] Loading from sessionStorage')
        const data = JSON.parse(storedData)
        console.log('[Roadmap] Parsed roadmap data:', data)
        console.log('[Roadmap] Keys:', Object.keys(data))
        console.log('[Roadmap] metadata:', data.metadata)
        console.log('[Roadmap] nodes:', data.nodes?.length || 0)
        console.log('[Roadmap] edges:', data.edges?.length || 0)
        console.log('[Roadmap] paths:', Object.keys(data.paths || {}))
        setRoadmapData(data)
      } else {
        console.log('[Roadmap] NO DATA IN sessionStorage - showing error')
        setRoadmapData({})
      }
    } catch (e) {
      console.error('[Roadmap] Failed to parse roadmap data', e)
      setRoadmapData({})
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Show loading while fetching data
  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-slate-900 to-black">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-lg text-gray-300 font-semibold">Loading your roadmap...</p>
        </div>
      </div>
    )
  }

  const nodes = roadmapData?.nodes || []
  const edges = roadmapData?.edges || []
  const paths = roadmapData?.paths || {}
  const metadata = roadmapData?.metadata || {}
  const salaryOutlook = metadata.salary_outlook || {}
  const currentPath = paths[selectedPath] || {}

  // Fallback UI if no data
  if (!metadata.career && !roadmapData?.career) {
    console.log('[Roadmap] NO CAREER FOUND - showing fallback UI')
    console.log('[Roadmap] roadmapData:', roadmapData)
    return (
      <div className="h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-slate-900 to-black">
        <div className="text-center max-w-md bg-gray-800 p-12 rounded-3xl shadow-2xl border border-gray-700">
          <div className="text-6xl mb-4">😕</div>
          <h2 className="text-2xl font-bold mb-4 text-white">No roadmap data found</h2>
          <p className="text-gray-400 mb-6">Please complete the quiz to generate your roadmap</p>
          <Link href="/" className="btn-primary inline-block bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-all">
            <ArrowLeft className="w-5 h-5 inline mr-2" />
            Back to Quiz
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-gradient-to-br from-gray-900 via-slate-900 to-black">
      {/* Header */}
      <div className="border-b border-gray-800 bg-gradient-to-r from-cyan-600 via-blue-600 to-purple-600 text-white shadow-xl">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-white/80 hover:text-white transition-colors">
                <ArrowLeft className="w-6 h-6" />
              </Link>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Sparkles className="w-5 h-5" />
                  <span className="text-sm font-semibold opacity-90">Your Personalized Roadmap</span>
                </div>
                <h1 className="text-3xl font-black">{metadata.career}</h1>
                <p className="text-sm text-cyan-100 mt-1">
                  Generated {new Date(metadata.generated_at).toLocaleDateString()}
                </p>
              </div>
            </div>
            <div className="flex gap-3">
              <button className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg flex items-center gap-2 transition-all">
                <Download className="w-4 h-4" />
                <span className="hidden md:inline">Export PDF</span>
              </button>
              <button className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg flex items-center gap-2 transition-all">
                <Share2 className="w-4 h-4" />
                <span className="hidden md:inline">Share</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <div
          className="border-r border-gray-800 bg-gray-900/95 backdrop-blur-sm overflow-y-hidden hover:overflow-y-auto relative"
          style={{ width: `${sidebarWidth}px`, minWidth: '280px', maxWidth: '600px' }}
        >
          <div className="p-6 space-y-6">
            {/* Path Tabs */}
            <div>
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-white">
                <TrendingUp className="w-5 h-5 text-cyan-400" />
                Choose Your Path
              </h2>
              <div className="space-y-3">
                <PathCard
                  id="cheapest"
                  icon={<PiggyBank className="w-5 h-5" />}
                  title="Most Affordable"
                  cost={paths.cheapest?.total_cost || 0}
                  duration={paths.cheapest?.duration || '4 years'}
                  roi={paths.cheapest?.roi || 0}
                  selected={selectedPath === 'cheapest'}
                  onClick={() => setSelectedPath('cheapest')}
                />
                <PathCard
                  id="fastest"
                  icon={<Zap className="w-5 h-5" />}
                  title="Fastest Path"
                  cost={paths.fastest?.total_cost || 0}
                  duration={paths.fastest?.duration || '3 years'}
                  roi={paths.fastest?.roi || 0}
                  selected={selectedPath === 'fastest'}
                  onClick={() => setSelectedPath('fastest')}
                />
                <PathCard
                  id="prestige"
                  icon={<Trophy className="w-5 h-5" />}
                  title="Prestige Path"
                  cost={paths.prestige?.total_cost || 0}
                  duration={paths.prestige?.duration || '4 years'}
                  roi={paths.prestige?.roi || 0}
                  selected={selectedPath === 'prestige'}
                  onClick={() => setSelectedPath('prestige')}
                />
              </div>
            </div>

            {/* Salary Outlook */}
            <div className="bg-gradient-to-br from-green-900/50 to-emerald-900/50 border-2 border-green-700 rounded-2xl p-5 shadow-lg backdrop-blur-sm">
              <h3 className="font-bold text-lg mb-3 flex items-center gap-2 text-white">
                <TrendingUp className="w-5 h-5 text-green-400" />
                Career Outlook
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400 text-sm">Median Salary</span>
                  <span className="font-bold text-xl text-green-400">
                    ${salaryOutlook.median_salary?.toLocaleString() || 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400 text-sm">Job Growth</span>
                  <span className="font-semibold text-green-300">{salaryOutlook.growth_rate || 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400 text-sm">Outlook</span>
                  <span className="font-semibold text-gray-200">{salaryOutlook.job_outlook || 'N/A'}</span>
                </div>
              </div>
            </div>

            {/* Path Steps */}
            <div className="bg-gray-800/80 border-2 border-gray-700 rounded-2xl p-5 shadow-lg backdrop-blur-sm">
              <h3 className="font-bold text-lg mb-4 flex items-center gap-2 text-white">
                <CheckCircle2 className="w-5 h-5 text-cyan-400" />
                Steps in {selectedPath === 'cheapest' ? 'Affordable' : selectedPath === 'fastest' ? 'Fast' : 'Prestige'} Path
              </h3>
              <div className="space-y-4">
                {(currentPath.steps || []).map((step: any, index: number) => (
                  <div
                    key={index}
                    className="relative pl-6 pb-4 border-l-4 border-cyan-600 last:border-transparent last:pb-0"
                  >
                    <div className="absolute -left-[9px] top-0 w-4 h-4 rounded-full bg-cyan-500 border-2 border-gray-800 shadow"></div>
                    <div className="font-semibold text-white">{step.description}</div>
                    <div className="text-sm text-gray-400 mt-1">{step.institution}</div>
                    <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {step.duration}
                      </span>
                      <span className="flex items-center gap-1">
                        <DollarSign className="w-3 h-3" />
                        ${step.cost?.toLocaleString()}
                      </span>
                    </div>
                    {step.url && (
                      <a
                        href={step.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-cyan-400 hover:text-cyan-300 hover:underline text-xs mt-1 inline-block"
                      >
                        Learn More →
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Citations */}
            {roadmapData.citations && roadmapData.citations.length > 0 && (
              <div className="bg-blue-50 border-2 border-blue-200 rounded-2xl p-5 shadow-lg">
                <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-blue-600" />
                  Sources
                </h3>
                <div className="space-y-2">
                  {roadmapData.citations.slice(0, 5).map((citation: any, index: number) => (
                    <a
                      key={index}
                      href={citation.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block text-sm text-blue-600 hover:text-blue-800 hover:underline truncate"
                    >
                      • {citation.title || citation.url}
                    </a>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Resize Handle */}
          <div
            className={`absolute right-0 top-0 bottom-0 w-1 bg-transparent hover:bg-cyan-500 transition-colors ${
              isResizing ? 'bg-cyan-500 cursor-col-resize' : 'cursor-col-resize'
            }`}
            onMouseDown={() => setIsResizing(true)}
            style={{ cursor: 'col-resize' }}
          />
        </div>

        {/* Right Side - Graph */}
        <div className="flex-1 relative">
          {nodes.length > 0 ? (
            <RoadmapGraph nodes={nodes} edges={edges} />
          ) : (
            <div className="flex items-center justify-center h-full bg-white/50 backdrop-blur-sm">
              <div className="text-center max-w-md p-8">
                <BarChart3 className="w-24 h-24 mx-auto mb-4 text-gray-400 animate-pulse" />
                <h3 className="text-xl font-bold mb-2 text-gray-700">Roadmap Graph Coming Soon</h3>
                <p className="text-gray-600">
                  The visual graph will be generated once we have complete pathway data from our agents.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Floating Chatbot */}
      <FloatingChatButton
        onClick={() => setIsChatOpen(!isChatOpen)}
        isOpen={isChatOpen}
        onPositionChange={setChatButtonPosition}
      />
      <ChatWidget
        isOpen={isChatOpen}
        career={metadata.career}
        selectedPath={selectedPath}
        buttonPosition={chatButtonPosition}
      />
    </div>
  )
}

function PathCard({
  id,
  icon,
  title,
  cost,
  duration,
  roi,
  selected,
  onClick
}: {
  id: string
  icon: React.ReactNode
  title: string
  cost: number
  duration: string
  roi: number
  selected: boolean
  onClick: () => void
}) {
  const gradients = {
    cheapest: 'from-green-700 to-emerald-800 border-green-500 shadow-green-500/50',
    fastest: 'from-blue-700 to-cyan-800 border-blue-500 shadow-blue-500/50',
    prestige: 'from-purple-700 to-pink-800 border-purple-500 shadow-purple-500/50'
  }

  const iconColors = {
    cheapest: 'text-green-300',
    fastest: 'text-blue-300',
    prestige: 'text-purple-300'
  }

  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-5 rounded-2xl border-2 cursor-pointer transition-all duration-300 group ${
        selected
          ? `bg-gradient-to-br ${gradients[id as keyof typeof gradients]} shadow-2xl scale-105 animate-in`
          : 'bg-gray-800/60 border-gray-700 hover:border-cyan-600 shadow-sm hover:shadow-lg hover:bg-gray-800 hover:scale-102'
      }`}
    >
      <div className="flex items-center gap-2 font-bold text-lg mb-3 text-white">
        <span className={`${selected ? iconColors[id as keyof typeof iconColors] : 'text-gray-400'} transition-all duration-300 ${selected ? 'animate-pulse' : 'group-hover:scale-110'}`}>
          {icon}
        </span>
        {title}
      </div>
      <div className="space-y-2 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-gray-400 flex items-center gap-1">
            <DollarSign className="w-4 h-4" />
            Total Cost
          </span>
          <span className="font-bold text-white">${cost?.toLocaleString() || 0}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400 flex items-center gap-1">
            <Clock className="w-4 h-4" />
            Duration
          </span>
          <span className="font-semibold text-white">{duration}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-gray-400 flex items-center gap-1">
            <TrendingUp className="w-4 h-4" />
            ROI
          </span>
          <span className="font-semibold text-white">{roi?.toFixed(1) || 0} years</span>
        </div>
      </div>
    </button>
  )
}

export default function RoadmapPage() {
  return (
    <Suspense fallback={
      <div className="h-screen flex items-center justify-center bg-gradient-to-br from-cyan-50 to-purple-100">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-cyan-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-lg text-gray-700 font-semibold">Loading your roadmap...</p>
        </div>
      </div>
    }>
      <RoadmapContent />
    </Suspense>
  )
}
