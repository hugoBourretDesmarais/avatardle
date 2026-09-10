// Solve counter backed by the Cloudflare Worker in api/. Every call fails
// soft: the counter is a nicety, so a backend outage must never block play.
const BASE = import.meta.env.VITE_API_URL || ''

export const apiEnabled = Boolean(BASE)

async function call(path, options, timeoutMs = 6000) {
  if (!BASE) return null
  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), timeoutMs)
  try {
    const res = await fetch(BASE + path, { ...options, signal: ctrl.signal })
    if (!res.ok) return null
    return await res.json()
  } catch {
    return null
  } finally {
    clearTimeout(timer)
  }
}

export function fetchCount(day, arcLimit) {
  const q = new URLSearchParams({ day, arc: arcLimit || '' })
  return call(`/count?${q}`, { method: 'GET' })
}

export function reportSolve(day, arcLimit, name) {
  return call('/solve', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ day, arcLimit: arcLimit || '', name }),
  })
}

const post = (path, body) => call(path, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
})

// Register and login surface their error text, so they bypass the soft-fail
// wrapper — a taken name has to be shown to the player, not swallowed.
async function postStrict(path, body) {
  if (!BASE) return { error: 'Leaderboard is unavailable.' }
  try {
    const res = await fetch(BASE + path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    const data = await res.json().catch(() => null)
    if (!res.ok) return { error: data?.error || `Request failed (${res.status}).` }
    return data
  } catch {
    return { error: 'Could not reach the leaderboard. Check your connection.' }
  }
}

// Workers Free caps CPU at 10ms per request, nowhere near enough for a real
// password KDF, so the work factor lives here instead. The password never
// leaves the browser — only this derived key does.
const PBKDF2_ITERATIONS = 600_000

async function deriveKey(name, password) {
  const enc = new TextEncoder()
  // The salt must be derivable before authenticating, so it comes from the
  // (unique) name rather than being random per account.
  const saltBits = await crypto.subtle.digest(
    'SHA-256', enc.encode(`avatardle:${name.trim().toLowerCase()}`))
  const material = await crypto.subtle.importKey(
    'raw', enc.encode(password), 'PBKDF2', false, ['deriveBits'])
  const bits = await crypto.subtle.deriveBits(
    { name: 'PBKDF2', hash: 'SHA-256', salt: new Uint8Array(saltBits), iterations: PBKDF2_ITERATIONS },
    material, 256)
  return [...new Uint8Array(bits)].map(b => b.toString(16).padStart(2, '0')).join('')
}

export const MIN_PASSWORD = 8

export async function registerPlayer(name, password) {
  if (!crypto?.subtle) return { error: 'This browser cannot sign in securely (needs HTTPS).' }
  return postStrict('/register', { name, key: await deriveKey(name, password) })
}

export async function loginPlayer(name, password) {
  if (!crypto?.subtle) return { error: 'This browser cannot sign in securely (needs HTTPS).' }
  return postStrict('/login', { name, key: await deriveKey(name, password) })
}

export function logoutPlayer(account) {
  if (!account?.token) return Promise.resolve(null)
  return post('/logout', { token: account.token })
}

export function submitResult(account, day, arcLimit, guesses, name) {
  if (!account?.token) return Promise.resolve(null)
  return post('/result', { token: account.token, day, arcLimit: arcLimit || '', guesses, name })
}

export function fetchLeaderboard(sort, day) {
  return call(`/leaderboard?${new URLSearchParams({ sort, day })}`, { method: 'GET' })
}

export function fetchMe(account) {
  if (!account?.token) return Promise.resolve(null)
  return call(`/me?${new URLSearchParams({ token: account.token })}`, { method: 'GET' })
}
