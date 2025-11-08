'use client'

import { useState, useRef, useEffect } from 'react'
import { MessageCircle, X } from 'lucide-react'

interface FloatingChatButtonProps {
  onClick: () => void
  isOpen: boolean
  onPositionChange?: (position: { x: number; y: number }) => void
}

export default function FloatingChatButton({ onClick, isOpen, onPositionChange }: FloatingChatButtonProps) {
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const buttonRef = useRef<HTMLDivElement>(null)

  // Initialize position to bottom-right
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const initialPosition = {
        x: window.innerWidth - 100,
        y: window.innerHeight - 100
      }
      setPosition(initialPosition)
      onPositionChange?.(initialPosition)
    }
  }, [])

  const handleMouseDown = (e: React.MouseEvent) => {
    // Allow dragging when chat is open or closed
    setIsDragging(true)
    setDragStart({
      x: e.clientX - position.x,
      y: e.clientY - position.y
    })
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (isDragging) {
      const newX = e.clientX - dragStart.x
      const newY = e.clientY - dragStart.y

      // Keep within viewport bounds
      const maxX = window.innerWidth - 70
      const maxY = window.innerHeight - 70

      const newPosition = {
        x: Math.max(0, Math.min(newX, maxX)),
        y: Math.max(0, Math.min(newY, maxY))
      }
      setPosition(newPosition)
      onPositionChange?.(newPosition)
    }
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove)
      window.addEventListener('mouseup', handleMouseUp)
      return () => {
        window.removeEventListener('mousemove', handleMouseMove)
        window.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isDragging, dragStart])

  return (
    <div
      ref={buttonRef}
      className={`fixed ${isDragging ? 'cursor-grabbing' : 'cursor-grab'} transition-transform hover:scale-110`}
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        zIndex: 9999
      }}
      onMouseDown={handleMouseDown}
      onClick={(e) => {
        if (!isDragging) {
          onClick()
        }
      }}
    >
      <div className="relative group">
        {/* Pulsing ring animation */}
        {!isOpen && (
          <div className="absolute inset-0 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 opacity-75 animate-ping"></div>
        )}

        {/* Main button */}
        <button
          className={`relative w-16 h-16 rounded-full shadow-2xl transition-all duration-300 flex items-center justify-center ${
            isOpen
              ? 'bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700'
              : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700'
          }`}
          aria-label={isOpen ? 'Close chat' : 'Open chat'}
        >
          {isOpen ? (
            <X className="w-7 h-7 text-white" />
          ) : (
            <MessageCircle className="w-7 h-7 text-white" />
          )}
        </button>

        {/* Tooltip */}
        {!isOpen && !isDragging && (
          <div className="absolute right-full mr-3 top-1/2 transform -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap">
            <div className="bg-gray-900 text-white text-sm px-3 py-2 rounded-lg shadow-xl">
              Ask me anything!
              <div className="absolute left-full top-1/2 transform -translate-y-1/2 w-0 h-0 border-t-4 border-b-4 border-l-4 border-transparent border-l-gray-900"></div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
