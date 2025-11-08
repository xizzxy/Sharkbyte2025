/**
 * CareerPilot AI - Cloudflare Worker (BFF API)
 *
 * Features:
 * - Proxies requests to Python agent service
 * - Caches roadmaps in KV for 7 days
 * - Rate limiting
 * - CORS handling
 */

interface Env {
  PYTHON_AGENT_API_URL: string;
  ROADMAP_CACHE: KVNamespace;
  RATE_LIMIT: KVNamespace;
}

interface QuizData {
  career: string;
  current_education: string;
  gpa: number;
  budget: string;
  timeline: string;
  location: string;
  goals: string[];
  has_transfer_credits: boolean;
  veteran_status: boolean;
  work_schedule: string;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    // CORS preflight
    if (request.method === 'OPTIONS') {
      return handleCORS();
    }

    const url = new URL(request.url);

    // Route: POST /api/plan
    if (request.method === 'POST' && url.pathname === '/api/plan') {
      return handlePlanRequest(request, env, ctx);
    }

    // Route: POST /api/chatbot
    if (request.method === 'POST' && url.pathname === '/api/chatbot') {
      return handleChatbotRequest(request, env, ctx);
    }

    // Route: GET /api/careers
    if (request.method === 'GET' && url.pathname === '/api/careers') {
      return handleCareersRequest();
    }

    // Route: GET /health
    if (request.method === 'GET' && url.pathname === '/health') {
      return new Response(JSON.stringify({ status: 'healthy', version: '1.0.0' }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }

    return new Response('Not Found', { status: 404 });
  }
};

/**
 * Handle /api/plan - Generate roadmap
 */
async function handlePlanRequest(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
  try {
    // Get client IP for rate limiting
    const clientIP = request.headers.get('CF-Connecting-IP') || 'unknown';

    // Check rate limit (10 requests per hour per IP)
    const isRateLimited = await checkRateLimit(env.RATE_LIMIT, clientIP);
    if (isRateLimited) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Rate limit exceeded. Please try again later.'
      }), {
        status: 429,
        headers: corsHeaders({ 'Content-Type': 'application/json' })
      });
    }

    // Parse request body
    const body = await request.json() as { quiz_data: QuizData };
    const quizData = body.quiz_data;

    // Validate quiz data
    if (!quizData?.career || !quizData?.budget) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Invalid quiz data'
      }), {
        status: 400,
        headers: corsHeaders({ 'Content-Type': 'application/json' })
      });
    }

    // Create cache key (hash of quiz data)
    const cacheKey = `roadmap:${await hashQuizData(quizData)}`;

    // Check cache first
    const cached = await env.ROADMAP_CACHE.get(cacheKey, 'json');
    if (cached) {
      console.log('[Cache HIT] Returning cached roadmap');
      return new Response(JSON.stringify({
        success: true,
        roadmap: cached,
        cached: true
      }), {
        headers: corsHeaders({ 'Content-Type': 'application/json' })
      });
    }

    console.log('[Cache MISS] Calling Python agents...');

    // Call Python agent service
    const agentUrl = env.PYTHON_AGENT_API_URL || 'http://localhost:8000/api/plan';
    const agentResponse = await fetch(agentUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ quiz_data: quizData })
    });

    if (!agentResponse.ok) {
      const errorText = await agentResponse.text();
      console.error('[Agent Error]', errorText);
      return new Response(JSON.stringify({
        success: false,
        error: 'Failed to generate roadmap. Please try again.'
      }), {
        status: 500,
        headers: corsHeaders({ 'Content-Type': 'application/json' })
      });
    }

    const agentData = await agentResponse.json();
    const roadmap = agentData.roadmap;

    // Cache the roadmap for 7 days
    ctx.waitUntil(
      env.ROADMAP_CACHE.put(cacheKey, JSON.stringify(roadmap), {
        expirationTtl: 604800 // 7 days
      })
    );

    // Increment rate limit counter
    ctx.waitUntil(incrementRateLimit(env.RATE_LIMIT, clientIP));

    return new Response(JSON.stringify({
      success: true,
      roadmap,
      cached: false
    }), {
      headers: corsHeaders({ 'Content-Type': 'application/json' })
    });

  } catch (error) {
    console.error('[Worker Error]', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Internal server error'
    }), {
      status: 500,
      headers: corsHeaders({ 'Content-Type': 'application/json' })
    });
  }
}

/**
 * Handle /api/careers - List supported careers
 */
function handleCareersRequest(): Response {
  const careers = [
    { name: 'Mechanical Engineer', category: 'STEM-Engineering', icon: '⚙️' },
    { name: 'Electrical Engineer', category: 'STEM-Engineering', icon: '⚡' },
    { name: 'Civil Engineer', category: 'STEM-Engineering', icon: '🏗️' },
    { name: 'Software Developer', category: 'STEM-Technology', icon: '💻' },
    { name: 'Registered Nurse', category: 'Healthcare', icon: '🏥' },
    { name: 'Architect', category: 'STEM-Architecture', icon: '🏛️' },
    { name: 'Accountant', category: 'Business', icon: '💼' },
    { name: 'Data Scientist', category: 'STEM-Technology', icon: '📊' },
  ];

  return new Response(JSON.stringify({ careers }), {
    headers: corsHeaders({ 'Content-Type': 'application/json' })
  });
}

/**
 * Hash quiz data for cache key
 */
async function hashQuizData(quizData: QuizData): Promise<string> {
  const data = JSON.stringify(quizData);
  const hashBuffer = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(data));
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Check rate limit (10 requests per hour per IP)
 */
async function checkRateLimit(kv: KVNamespace, clientIP: string): Promise<boolean> {
  const key = `ratelimit:${clientIP}`;
  const current = await kv.get(key);

  if (!current) {
    return false; // No limit yet
  }

  const count = parseInt(current);
  return count >= 10; // Max 10 requests per hour
}

/**
 * Increment rate limit counter
 */
async function incrementRateLimit(kv: KVNamespace, clientIP: string): Promise<void> {
  const key = `ratelimit:${clientIP}`;
  const current = await kv.get(key);
  const count = current ? parseInt(current) + 1 : 1;

  await kv.put(key, count.toString(), {
    expirationTtl: 3600 // 1 hour
  });
}

/**
 * CORS headers
 */
function corsHeaders(additional: Record<string, string> = {}): Record<string, string> {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    ...additional
  };
}

/**
 * Handle CORS preflight
 */
function handleCORS(): Response {
  return new Response(null, {
    status: 204,
    headers: corsHeaders()
  });
}

/**
 * Handle /api/chatbot - AI chatbot responses
 */
async function handleChatbotRequest(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
  try {
    // Parse request body
    const body = await request.json() as { question: string; career?: string; path?: string };
    const { question, career, path } = body;

    // Validate input
    if (!question || question.trim().length === 0) {
      return new Response(JSON.stringify({
        success: false,
        error: 'Question is required'
      }), {
        status: 400,
        headers: corsHeaders({ 'Content-Type': 'application/json' })
      });
    }

    // Create cache key
    const cacheKey = `chatbot:${await hashString(question + (career || '') + (path || ''))}`;

    // Check cache first (1 hour TTL)
    const cached = await env.ROADMAP_CACHE.get(cacheKey);
    if (cached) {
      console.log('[Chatbot Cache HIT]');
      return new Response(JSON.stringify({
        success: true,
        answer: cached,
        cached: true
      }), {
        headers: corsHeaders({ 'Content-Type': 'application/json' })
      });
    }

    console.log('[Chatbot Cache MISS] Calling backend...');

    // Call Python backend chatbot endpoint
    const agentUrl = env.PYTHON_AGENT_API_URL || 'http://localhost:8000/api';
    const backendUrl = agentUrl.replace('/api/plan', '/api/chatbot');

    const backendResponse = await fetch(backendUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, career, path })
    });

    if (!backendResponse.ok) {
      const errorText = await backendResponse.text();
      console.error('[Chatbot Backend Error]', errorText);
      return new Response(JSON.stringify({
        success: false,
        error: 'Failed to generate response'
      }), {
        status: 500,
        headers: corsHeaders({ 'Content-Type': 'application/json' })
      });
    }

    const data = await backendResponse.json();
    const answer = data.answer || data.response;

    // Cache response for 1 hour
    ctx.waitUntil(
      env.ROADMAP_CACHE.put(cacheKey, answer, {
        expirationTtl: 3600 // 1 hour
      })
    );

    return new Response(JSON.stringify({
      success: true,
      answer,
      cached: false
    }), {
      headers: corsHeaders({ 'Content-Type': 'application/json' })
    });

  } catch (error) {
    console.error('[Chatbot Worker Error]', error);
    return new Response(JSON.stringify({
      success: false,
      error: 'Internal server error'
    }), {
      status: 500,
      headers: corsHeaders({ 'Content-Type': 'application/json' })
    });
  }
}

/**
 * Hash a string for cache key
 */
async function hashString(str: string): Promise<string> {
  const hashBuffer = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}
