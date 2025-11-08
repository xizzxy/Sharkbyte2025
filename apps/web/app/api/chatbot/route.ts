import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { question, career, path } = await request.json()

    if (!question || !career) {
      return NextResponse.json(
        { error: 'Missing required fields: question and career' },
        { status: 400 }
      )
    }

    // Create context-aware system prompt
    const systemPrompt = `You are CareerPilot AI, a helpful career guidance assistant. You are helping a student pursuing a career as a ${career}. ${
      path ? `They are currently viewing the ${path} path (${path === 'cheapest' ? 'most affordable' : path === 'fastest' ? 'fastest completion time' : 'highest prestige universities'}).` : ''
    }

Your role is to:
- Answer questions about their career path, education requirements, and university choices
- Provide guidance on costs, timelines, and educational decisions
- Help them understand the differences between the three path options (cheapest, fastest, prestige)
- Offer advice on scholarships, financial aid, and cost-saving strategies
- Explain what specific certifications or degrees they'll need
- Be encouraging and supportive

Keep your responses concise (2-4 sentences), friendly, and actionable. Focus on the specific career path: ${career}.`

    // Call Python agent server with Vertex AI
    const agentServerUrl = process.env.PYTHON_AGENT_API_URL || 'http://localhost:8000'
    const response = await fetch(`${agentServerUrl}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: question,
        system_prompt: systemPrompt
      })
    })

    if (!response.ok) {
      throw new Error(`Agent server returned ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json({ answer: data.response })

  } catch (error: any) {
    console.error('[Chatbot API] Error:', error)
    return NextResponse.json(
      { error: 'Failed to generate response', details: error.message },
      { status: 500 }
    )
  }
}
