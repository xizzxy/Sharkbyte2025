'use client'

import { useCallback, useState } from 'react'
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
import { ExternalLink, Info } from 'lucide-react'

// Custom Node Component
function CustomNode({ data }: { data: any }) {
  const [showTooltip, setShowTooltip] = useState(false)

  const getNodeStyle = () => {
    switch (data.type) {
      case 'mdc':
        return 'bg-gradient-to-br from-cyan-100 to-blue-100 border-cyan-400 hover:shadow-cyan-300'
      case 'university':
        return 'bg-gradient-to-br from-purple-100 to-pink-100 border-purple-400 hover:shadow-purple-300'
      case 'cert':
        return 'bg-gradient-to-br from-green-100 to-emerald-100 border-green-400 hover:shadow-green-300'
      case 'license':
        return 'bg-gradient-to-br from-yellow-100 to-orange-100 border-yellow-400 hover:shadow-yellow-300'
      default:
        return 'bg-gradient-to-br from-gray-100 to-gray-200 border-gray-400'
    }
  }

  return (
    <div
      className={`px-6 py-4 shadow-lg rounded-2xl border-2 min-w-[200px] ${getNodeStyle()} hover:shadow-xl transition-all duration-200 cursor-pointer relative group`}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div className="font-bold text-gray-900 mb-1 text-center text-sm">
        {data.label}
      </div>
      {data.cost && (
        <div className="text-xs text-gray-700 text-center font-semibold">
          ${data.cost?.toLocaleString()}
        </div>
      )}
      {data.duration && (
        <div className="text-xs text-gray-600 text-center">
          {data.duration}
        </div>
      )}

      {/* Tooltip */}
      {showTooltip && (
        <div className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-4 py-3 bg-gray-900 text-white text-xs rounded-lg shadow-xl min-w-[220px] animate-fade-in">
          <div className="font-bold mb-1">{data.label}</div>
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
    <div className="w-full h-full rounded-2xl overflow-hidden shadow-2xl border-2 border-gray-200 bg-white">
      <ReactFlow
        nodes={nodesState}
        edges={edgesState}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
        className="bg-gradient-to-br from-gray-50 to-blue-50"
      >
        <Background color="#94a3b8" gap={16} />
        <Controls className="bg-white shadow-lg rounded-lg border border-gray-200" />
        <MiniMap
          className="bg-white shadow-lg rounded-lg border border-gray-200"
          nodeColor={(node) => {
            const type = node.data?.type
            switch (type) {
              case 'mdc': return '#93c5fd'
              case 'university': return '#c4b5fd'
              case 'cert': return '#86efac'
              case 'license': return '#fde047'
              default: return '#e5e7eb'
            }
          }}
        />
      </ReactFlow>

      {/* Legend */}
      <div className="absolute bottom-20 right-6 bg-white/95 backdrop-blur-sm rounded-xl shadow-xl p-4 border border-gray-200">
        <div className="text-sm font-bold mb-3 text-gray-900">Legend</div>
        <div className="space-y-2 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-gradient-to-br from-cyan-200 to-blue-200 border-2 border-cyan-400 rounded"></div>
            <span className="text-gray-700">MDC Program</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-gradient-to-br from-purple-200 to-pink-200 border-2 border-purple-400 rounded"></div>
            <span className="text-gray-700">University</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-gradient-to-br from-green-200 to-emerald-200 border-2 border-green-400 rounded"></div>
            <span className="text-gray-700">Certification</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-gradient-to-br from-yellow-200 to-orange-200 border-2 border-yellow-400 rounded"></div>
            <span className="text-gray-700">License</span>
          </div>
        </div>
      </div>
    </div>
  )
}
