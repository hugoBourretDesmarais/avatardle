import { NAMES, DEBUT, ARCS } from './data.js'

// Must stay byte-identical to the client's hash in src/game/state.js —
// the worker recomputes the day's answer to verify a claimed solve.
function hashString(s) {
  let h = 2166136261
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return h >>> 0
}

// "arc" throughout is the spoiler limit; here it is a book name (Water, Earth).
function poolFor(arcLimit) {
  if (!arcLimit) return NAMES
  const book = ARCS.find(([name]) => name === arcLimit)
  if (!book) return NAMES
  const end = book[1]
  return NAMES.filter((_, i) => DEBUT[i] <= end)
}

function answerFor(day, arcLimit) {
  const pool = poolFor(arcLimit)
  return pool[hashString('avdle:' + day) % pool.length]
}

const DAY_RE = /^\d{4}-\d{2}-\d{2}$/

// The client's day is its own local date, so accept a small window around UTC
// rather than trusting or rejecting it outright.
function dayIsPlausible(day) {
  if (!DAY_RE.test(day)) return false
  const t = Date.parse(day + 'T00:00:00Z')
  if (Number.isNaN(t)) return false
  const drift = Math.abs(Date.now() - t)
  return drift < 3 * 86400000
}

function cors(origin, env) {
  const allowed = (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean)
  const ok = allowed.includes('*') || (origin && allowed.includes(origin))
  return {
    'Access-Control-Allow-Origin': ok ? origin || '*' : allowed[0] || '*',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    Vary: 'Origin',
  }
}

function json(body, status, headers) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store', ...headers },
  })
}

async function sha256Hex(s) {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s))
  return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join('')
}

const NAME_RE = /^[A-Za-z0-9][A-Za-z0-9 _-]{1,19}$/

function cleanName(raw) {
  const name = String(raw || '').trim().replace(/\s+/g, ' ')
  return NAME_RE.test(name) ? name : null
}

// poolFor() falls back to the full roster for a name it doesn't know, so an
// unrecognised limit would pass the answer check and then be stored and shown.
const isKnownArc = a => !a || ARCS.some(([name]) => name === a)

function previousDay(day) {
  const t = Date.parse(day + 'T00:00:00Z')
  return new Date(t - 86400000).toISOString().slice(0, 10)
}

function randomHex(bytes) {
  return [...crypto.getRandomValues(new Uint8Array(bytes))]
    .map(b => b.toString(16).padStart(2, '0')).join('')
}

// The client sends a PBKDF2-derived key, never the password. Hashing it again
// with a per-user salt keeps a leaked row from being replayed as a login.
const hashKey = (salt, key) => sha256Hex(`${salt}:${key}`)

async function newSession(env, playerId) {
  const token = randomHex(32)
  await env.DB.prepare(
    'INSERT INTO sessions (token_hash, player_id, created_at) VALUES (?, ?, ?)'
  ).bind(await sha256Hex(token), playerId, new Date().toISOString()).run()
  return token
}

async function authenticate(env, token) {
  if (!token) return null
  const row = await env.DB.prepare(
    `SELECT p.id, p.name FROM sessions s JOIN players p ON p.id = s.player_id
     WHERE s.token_hash = ?`
  ).bind(await sha256Hex(String(token))).first()
  return row || null
}

async function ipHash(request, env) {
  const ip = request.headers.get('CF-Connecting-IP') || '0.0.0.0'
  const data = new TextEncoder().encode(`${env.IP_SALT || 'avdle'}:${ip}`)
  const digest = await crypto.subtle.digest('SHA-256', data)
  return [...new Uint8Array(digest)].slice(0, 16).map(b => b.toString(16).padStart(2, '0')).join('')
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url)
    const headers = cors(request.headers.get('Origin'), env)

    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers })

    // GET /count?day=YYYY-MM-DD&arc=<arc name> -> how many solved that day
    if (request.method === 'GET' && url.pathname === '/count') {
      const day = url.searchParams.get('day') || ''
      const arcLimit = url.searchParams.get('arc') || ''
      if (!DAY_RE.test(day)) return json({ error: 'bad day' }, 400, headers)
      const row = await env.DB.prepare(
        'SELECT count FROM solves WHERE day = ? AND arc_limit = ?'
      ).bind(day, arcLimit).first()
      return json({ day, arcLimit, count: row?.count ?? 0 }, 200, headers)
    }

    // POST /solve { day, arcLimit, name } -> verifies, counts once per address
    if (request.method === 'POST' && url.pathname === '/solve') {
      let body
      try {
        body = await request.json()
      } catch {
        return json({ error: 'bad json' }, 400, headers)
      }
      const day = String(body.day || '')
      const arcLimit = String(body.arcLimit || '')
      const name = String(body.name || '')
      if (!dayIsPlausible(day)) return json({ error: 'bad day' }, 400, headers)
      if (!isKnownArc(arcLimit)) return json({ error: 'bad arc' }, 400, headers)
      // Only a correct answer counts, so the tally can't be inflated by
      // anyone who hasn't actually solved it.
      if (name !== answerFor(day, arcLimit)) {
        return json({ error: 'wrong answer', counted: false }, 403, headers)
      }
      const hash = await ipHash(request, env)
      const first = await env.DB.prepare(
        'INSERT OR IGNORE INTO counted (day, arc_limit, ip_hash) VALUES (?, ?, ?)'
      ).bind(day, arcLimit, hash).run()
      const isNew = (first.meta?.changes ?? 0) > 0
      if (isNew) {
        await env.DB.prepare(
          `INSERT INTO solves (day, arc_limit, count) VALUES (?, ?, 1)
           ON CONFLICT(day, arc_limit) DO UPDATE SET count = count + 1`
        ).bind(day, arcLimit).run()
      }
      const row = await env.DB.prepare(
        'SELECT count FROM solves WHERE day = ? AND arc_limit = ?'
      ).bind(day, arcLimit).first()
      return json({ day, arcLimit, count: row?.count ?? 0, counted: isNew }, 200, headers)
    }

    // POST /register { name, key } -> claims a pseudonym, returns a session token
    if (request.method === 'POST' && url.pathname === '/register') {
      let body
      try {
        body = await request.json()
      } catch {
        return json({ error: 'bad json' }, 400, headers)
      }
      const name = cleanName(body.name)
      if (!name) {
        return json({ error: 'Names are 2\u201320 characters: letters, digits, spaces, - and _.' }, 400, headers)
      }
      const key = String(body.key || '')
      if (!/^[a-f0-9]{64}$/.test(key)) return json({ error: 'bad key' }, 400, headers)

      const nameKey = name.toLowerCase()
      const taken = await env.DB.prepare('SELECT 1 FROM players WHERE name_key = ?')
        .bind(nameKey).first()
      if (taken) return json({ error: 'That name is already taken.' }, 409, headers)

      const id = crypto.randomUUID()
      const salt = randomHex(16)
      const now = new Date().toISOString()
      try {
        await env.DB.batch([
          env.DB.prepare(
            `INSERT INTO players (id, name, name_key, password_salt, password_hash, created_at, last_seen)
             VALUES (?, ?, ?, ?, ?, ?, ?)`
          ).bind(id, name, nameKey, salt, await hashKey(salt, key), now, now),
          env.DB.prepare('INSERT INTO standings (player_id) VALUES (?)').bind(id),
        ])
      } catch (err) {
        // Only the name_key collision means the name is taken; reporting every
        // failure that way hides schema and database errors behind it.
        if (/UNIQUE/i.test(String(err?.message || err))) {
          return json({ error: 'That name is already taken.' }, 409, headers)
        }
        return json({ error: 'Could not create that account. Please try again.' }, 500, headers)
      }
      return json({ id, name, token: await newSession(env, id) }, 200, headers)
    }

    // POST /login { name, key } -> signs in on any device
    if (request.method === 'POST' && url.pathname === '/login') {
      let body
      try {
        body = await request.json()
      } catch {
        return json({ error: 'bad json' }, 400, headers)
      }
      const nameKey = String(body.name || '').trim().replace(/\s+/g, ' ').toLowerCase()
      const key = String(body.key || '')
      const row = await env.DB.prepare(
        'SELECT id, name, password_salt, password_hash FROM players WHERE name_key = ?'
      ).bind(nameKey).first()
      // Same message either way, so the endpoint doesn't confirm which names exist.
      const bad = json({ error: 'Wrong name or password.' }, 401, headers)
      if (!row || !/^[a-f0-9]{64}$/.test(key)) return bad
      if (await hashKey(row.password_salt, key) !== row.password_hash) return bad

      await env.DB.prepare('UPDATE players SET last_seen = ? WHERE id = ?')
        .bind(new Date().toISOString(), row.id).run()
      return json({ id: row.id, name: row.name, token: await newSession(env, row.id) }, 200, headers)
    }

    // POST /logout { token }
    if (request.method === 'POST' && url.pathname === '/logout') {
      let body
      try {
        body = await request.json()
      } catch {
        return json({ error: 'bad json' }, 400, headers)
      }
      if (body.token) {
        await env.DB.prepare('DELETE FROM sessions WHERE token_hash = ?')
          .bind(await sha256Hex(String(body.token))).run()
      }
      return json({ ok: true }, 200, headers)
    }

    // POST /result { token, day, arcLimit, guesses, name } -> records a solve
    if (request.method === 'POST' && url.pathname === '/result') {
      let body
      try {
        body = await request.json()
      } catch {
        return json({ error: 'bad json' }, 400, headers)
      }
      const player = await authenticate(env, body.token)
      if (!player) return json({ error: 'not signed in' }, 401, headers)

      const day = String(body.day || '')
      const arcLimit = String(body.arcLimit || '')
      const guesses = Number(body.guesses)
      const name = String(body.name || '')
      if (!dayIsPlausible(day)) return json({ error: 'bad day' }, 400, headers)
      if (!Number.isInteger(guesses) || guesses < 1 || guesses > 500) {
        return json({ error: 'bad guesses' }, 400, headers)
      }
      if (!isKnownArc(arcLimit)) return json({ error: 'bad arc' }, 400, headers)
      if (name !== answerFor(day, arcLimit)) return json({ error: 'wrong answer' }, 403, headers)

      const existing = await env.DB.prepare(
        'SELECT day FROM results WHERE player_id = ? AND day = ?'
      ).bind(player.id, day).first()
      if (existing) return json({ ranked: false, reason: 'already recorded for that day' }, 200, headers)

      const st = await env.DB.prepare(
        'SELECT wins, total_guesses, max_streak FROM standings WHERE player_id = ?'
      ).bind(player.id).first() || { wins: 0, total_guesses: 0, max_streak: 0 }

      await env.DB.prepare(
        `INSERT INTO results (player_id, day, arc_limit, guesses, solved_at)
         VALUES (?, ?, ?, ?, ?)`
      ).bind(player.id, day, arcLimit, guesses, new Date().toISOString()).run()

      // Derive the streak from the stored days rather than incrementing a
      // counter, so a result that arrives out of order still lands correctly.
      const recent = await env.DB.prepare(
        'SELECT day, arc_limit FROM results WHERE player_id = ? ORDER BY day DESC LIMIT 90'
      ).bind(player.id).all()
      const days = (recent.results || []).map(r => r.day)
      const latest = days[0]
      // Belongs to the newest day, not to this request — a backfilled older
      // result must not relabel the board.
      const latestArc = recent.results?.[0]?.arc_limit ?? ''
      let streak = 0
      let cursor = latest
      for (const d of days) {
        if (d !== cursor) break
        streak++
        cursor = previousDay(cursor)
      }
      const maxStreak = Math.max(st.max_streak || 0, streak)

      await env.DB.prepare(
        `UPDATE standings SET wins = wins + 1, total_guesses = total_guesses + ?,
           streak = ?, max_streak = ?, last_win_day = ?, last_arc_limit = ?
         WHERE player_id = ?`
      ).bind(guesses, streak, maxStreak, latest, latestArc, player.id).run()
      return json(
        { ranked: true, wins: (st.wins || 0) + 1, streak, maxStreak, arcLimit: latestArc || null },
        200, headers)
    }

    // GET /leaderboard?sort=streak|wins|avg&day=YYYY-MM-DD
    if (request.method === 'GET' && url.pathname === '/leaderboard') {
      const sort = url.searchParams.get('sort') || 'streak'
      const day = url.searchParams.get('day') || ''
      const order = {
        streak: 'st.max_streak DESC, st.wins DESC',
        wins: 'st.wins DESC, st.max_streak DESC',
        avg: '(CAST(st.total_guesses AS REAL) / st.wins) ASC, st.wins DESC',
      }[sort]
      if (!order) return json({ error: 'bad sort' }, 400, headers)
      // Averages need a floor of games to be meaningful.
      const having = sort === 'avg' ? 'AND st.wins >= 3' : ''
      const rows = await env.DB.prepare(
        `SELECT p.name, st.wins, st.total_guesses, st.streak, st.max_streak, st.last_win_day,
                st.last_arc_limit
         FROM standings st JOIN players p ON p.id = st.player_id
         WHERE st.wins > 0 ${having}
         ORDER BY ${order} LIMIT 50`
      ).all()
      const today = DAY_RE.test(day) ? day : null
      const yesterday = today ? previousDay(today) : null
      const entries = (rows.results || []).map((r, i) => ({
        rank: i + 1,
        name: r.name,
        wins: r.wins,
        avg: r.wins ? +(r.total_guesses / r.wins).toFixed(2) : null,
        maxStreak: r.max_streak,
        arcLimit: r.last_arc_limit || null,
        // A stored streak is only live if the last win was today or yesterday.
        streak: today && (r.last_win_day === today || r.last_win_day === yesterday) ? r.streak : 0,
      }))
      return json({ sort, entries }, 200, headers)
    }

    // GET /me?token= -> that player's own standing
    if (request.method === 'GET' && url.pathname === '/me') {
      const player = await authenticate(env, url.searchParams.get('token'))
      if (!player) return json({ error: 'not signed in' }, 401, headers)
      const st = await env.DB.prepare(
        'SELECT wins, total_guesses, streak, max_streak, last_win_day FROM standings WHERE player_id = ?'
      ).bind(player.id).first()
      return json({
        id: player.id,
        name: player.name,
        wins: st?.wins ?? 0,
        avg: st?.wins ? +(st.total_guesses / st.wins).toFixed(2) : null,
        streak: st?.streak ?? 0,
        maxStreak: st?.max_streak ?? 0,
        lastWinDay: st?.last_win_day ?? null,
      }, 200, headers)
    }

    if (url.pathname === '/health') return json({ ok: true }, 200, headers)

    return json({ error: 'not found' }, 404, headers)
  },
}
