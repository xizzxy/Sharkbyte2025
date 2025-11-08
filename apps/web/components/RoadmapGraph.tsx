'use client'

import { useCallback, useState, useEffect } from 'react'
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  NodeTypes,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { ExternalLink, GraduationCap, School, BookOpen, Award, FileCheck, Briefcase, FlaskConical, Zap, PiggyBank, Trophy } from 'lucide-react'

// Custom Node Component with Dark Mode and Animations
function CustomNode({ data }: { data: any }) {
  const [showTooltip, setShowTooltip] = useState(false)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Animate in on mount
    const timer = setTimeout(() => setIsVisible(true), 100)
    return () => clearTimeout(timer)
  }, [])

  const getNodeStyle = () => {
    const baseStyle = 'transition-all duration-500'
    const pathGlow = data.path_type === 'cheapest' ? 'shadow-green-500/40' :
                     data.path_type === 'fastest' ? 'shadow-blue-500/40' :
                     data.path_type === 'prestige' ? 'shadow-purple-500/40' : ''

    switch (data.type) {
      case 'mdc':
        return `bg-gradient-to-br from-cyan-600 to-blue-700 border-cyan-400 hover:shadow-cyan-500/50 ${pathGlow} text-white ${baseStyle}`
      case 'university':
        return `bg-gradient-to-br from-purple-600 to-pink-700 border-purple-400 hover:shadow-purple-500/50 ${pathGlow} text-white ${baseStyle}`
      case 'masters':
        return `bg-gradient-to-br from-indigo-600 to-violet-700 border-indigo-400 hover:shadow-indigo-500/50 ${pathGlow} text-white ${baseStyle}`
      case 'phd':
        return `bg-gradient-to-br from-amber-600 to-yellow-700 border-amber-400 hover:shadow-amber-500/50 ${pathGlow} text-white ${baseStyle}`
      case 'cert':
        return `bg-gradient-to-br from-green-600 to-emerald-700 border-green-400 hover:shadow-green-500/50 ${pathGlow} text-white ${baseStyle}`
      case 'license':
        return `bg-gradient-to-br from-yellow-600 to-orange-700 border-yellow-400 hover:shadow-yellow-500/50 ${pathGlow} text-white ${baseStyle}`
      case 'internship':
        return `bg-gradient-to-br from-teal-600 to-cyan-700 border-teal-400 hover:shadow-teal-500/50 ${pathGlow} text-white ${baseStyle}`
      case 'research':
        return `bg-gradient-to-br from-rose-600 to-pink-700 border-rose-400 hover:shadow-rose-500/50 ${pathGlow} text-white ${baseStyle}`
      default:
        return `bg-gradient-to-br from-gray-700 to-gray-800 border-gray-500 text-white ${baseStyle}`
    }
  }

  const getPathIcon = () => {
    if (!data.path_type) return null
    switch (data.path_type) {
      case 'cheapest':
        return <PiggyBank className="w-3 h-3" />
      case 'fastest':
        return <Zap className="w-3 h-3" />
      case 'prestige':
        return <Trophy className="w-3 h-3" />
      default:
        return null
    }
  }

  return (
    <div
      className={`px-6 py-4 shadow-lg rounded-2xl border-2 min-w-[200px] ${getNodeStyle()} hover:shadow-2xl hover:scale-105 cursor-pointer relative group ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      }`}
      style={{ transition: 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)' }}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      {/* Tier Badge for Universities */}
      {data.tier && (data.type === 'university' || data.type === 'masters' || data.type === 'phd') && (
        <div className="absolute -top-2 -right-2 bg-gradient-to-r from-yellow-400 to-amber-500 text-white text-xs px-2 py-1 rounded-full font-bold shadow-lg border-2 border-white">
          {data.tier}
        </div>
      )}

      {/* Degree Badge */}
      {data.degree && (
        <div className="absolute -top-2 -left-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white text-xs px-2 py-1 rounded-full font-bold shadow-lg border-2 border-white">
          {data.degree}
        </div>
      )}

      <div className="font-bold mb-1 text-center text-sm drop-shadow-sm">
        {data.label}
      </div>

      {/* Ranking Label */}
      {data.ranking_label && (
        <div className="text-xs text-center font-semibold mb-1 text-white/90 drop-shadow-sm">
          {data.ranking_label}
        </div>
      )}

      {data.cost && (
        <div className="text-xs text-center font-semibold text-white/95 drop-shadow-sm">
          ${data.cost?.toLocaleString()}
        </div>
      )}
      {data.duration && (
        <div className="text-xs text-center text-white/80">
          {data.duration}
        </div>
      )}

      {/* Path Type Badge with Icon */}
      {data.path_type && (
        <div className={`absolute -bottom-2 left-1/2 transform -translate-x-1/2 text-xs px-3 py-1 rounded-full font-bold shadow-lg border-2 border-white whitespace-nowrap flex items-center gap-1 ${
          data.path_type === 'cheapest' ? 'bg-gradient-to-r from-green-500 to-emerald-600 animate-pulse' :
          data.path_type === 'fastest' ? 'bg-gradient-to-r from-orange-500 to-red-600 animate-pulse' :
          data.path_type === 'prestige' ? 'bg-gradient-to-r from-purple-500 to-pink-600 animate-pulse' :
          'bg-gradient-to-r from-gray-500 to-gray-600'
        }`}>
          {getPathIcon()}
          {data.path_type === 'cheapest' ? 'Cheapest' :
           data.path_type === 'fastest' ? 'Fastest' :
           data.path_type === 'prestige' ? 'Prestige' :
           data.path_type}
        </div>
      )}

      {/* Tooltip */}
      {showTooltip && (
        <div className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-4 py-3 bg-gray-900 text-white text-xs rounded-lg shadow-xl min-w-[220px] animate-fade-in">
          <div className="font-bold mb-1">{data.label}</div>

          {/* Path Type in Tooltip */}
          {data.path_type && (
            <div className={`inline-block px-2 py-1 rounded-md text-xs font-semibold mb-2 ${
              data.path_type === 'cheapest' ? 'bg-green-600/30 text-green-300' :
              data.path_type === 'fastest' ? 'bg-orange-600/30 text-orange-300' :
              data.path_type === 'prestige' ? 'bg-purple-600/30 text-purple-300' :
              'bg-gray-600/30 text-gray-300'
            }`}>
              {data.path_type === 'cheapest' ? 'Cheapest Path' :
               data.path_type === 'fastest' ? 'Fastest Path' :
               data.path_type === 'prestige' ? 'Prestige Path' :
               data.path_type}
            </div>
          )}

          {data.cost && <div>Cost: ${data.cost.toLocaleString()}</div>}
          {data.duration && <div>Duration: {data.duration}</div>}
          {data.url && (
            <a
              href={data.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-cyan-300 hover:underline flex items-center gap-1 mt-2"
              onClick={(e) => e.stopPropagation()}
            >
              <ExternalLink className="w-3 h-3" />
              Learn more
            </a>
          )}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
        </div>
      )}
    </div>
  )
}

const nodeTypes: NodeTypes = {
  custom: CustomNode,
}

interface RoadmapGraphProps {
  nodes: Node[]
  edges: Edge[]
}

export default function RoadmapGraph({ nodes, edges }: RoadmapGraphProps) {
  const [nodesState, , onNodesChange] = useNodesState(
    nodes.map(node => ({ ...node, type: 'custom' }))
  )
  const [edgesState, , onEdgesChange] = useEdgesState(
    edges.map(edge => ({
      ...edge,
      style: { stroke: '#3b82f6', strokeWidth: 2 },
      animated: true,
    }))
  )

  const onNodeClick = useCallback((event: any, node: Node) => {
    console.log('Node clicked:', node)
    // Could open modal with more details
  }, [])

  return (
    <div className="w-full h-full rounded-2xl overflow-hidden shadow-2xl border-2 border-gray-700 bg-gray-900">
      <ReactFlow
        nodes={nodesState}
        edges={edgesState}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
        className="bg-gradient-to-br from-gray-900 via-slate-900 to-gray-950"
      >
        <Background color="#374151" gap={16} />
        <Controls className="bg-gray-800 shadow-lg rounded-lg border border-gray-700" />
        <MiniMap
          className="bg-gray-800 shadow-lg rounded-lg border border-gray-700"
          nodeColor={(node) => {
            const type = node.data?.type
            switch (type) {
              case 'mdc': return '#0891b2'
              case 'university': return '#9333ea'
              case 'masters': return '#6366f1'
              case 'phd': return '#f59e0b'
              case 'cert': return '#10b981'
              case 'license': return '#eab308'
              case 'internship': return '#14b8a6'
              case 'research': return '#f43f5e'
              default: return '#6b7280'
            }
          }}
        />
      </ReactFlow>

      {/* Legend with Icons */}
      <div className="absolute bottom-20 right-6 bg-gray-800/95 backdrop-blur-sm rounded-xl shadow-xl p-4 border border-gray-700 animate-in">
        <div className="text-sm font-bold mb-3 text-white flex items-center gap-2">
          <BookOpen className="w-4 h-4 text-cyan-400" />
          Legend
        </div>
        <div className="space-y-2 text-xs">
          <div className="flex items-center gap-2 hover:bg-gray-700/50 p-1 rounded transition-colors">
            <School className="w-4 h-4 text-cyan-400" />
            <span className="text-gray-300">MDC (AA)</span>
          </div>
          <div className="flex items-center gap-2 hover:bg-gray-700/50 p-1 rounded transition-colors">
            <GraduationCap className="w-4 h-4 text-purple-400" />
            <span className="text-gray-300">University (BS)</span>
          </div>
          <div className="flex items-center gap-2 hover:bg-gray-700/50 p-1 rounded transition-colors">
            <BookOpen className="w-4 h-4 text-indigo-400" />
            <span className="text-gray-300">Masters (MS)</span>
          </div>
          <div className="flex items-center gap-2 hover:bg-gray-700/50 p-1 rounded transition-colors">
            <FlaskConical className="w-4 h-4 text-amber-400" />
            <span className="text-gray-300">PhD</span>
          </div>
          <div className="flex items-center gap-2 hover:bg-gray-700/50 p-1 rounded transition-colors">
            <Award className="w-4 h-4 text-green-400" />
            <span className="text-gray-300">Certification</span>
          </div>
          <div className="flex items-center gap-2 hover:bg-gray-700/50 p-1 rounded transition-colors">
            <FileCheck className="w-4 h-4 text-yellow-400" />
            <span className="text-gray-300">License</span>
          </div>
          <div className="flex items-center gap-2 hover:bg-gray-700/50 p-1 rounded transition-colors">
            <Briefcase className="w-4 h-4 text-teal-400" />
            <span className="text-gray-300">Internship</span>
          </div>
        </div>
      </div>
    </div>
  )
}
