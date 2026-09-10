export const COLUMNS = [
  { key: 'portrait', label: 'Character' },
  { key: 'gender', label: 'Gender' },
  { key: 'nation', label: 'Nation' },
  { key: 'bending', label: 'Bending' },
  { key: 'skills', label: 'Skills' },
  { key: 'affiliation', label: 'Affiliation' },
  { key: 'age', label: 'Age' },
  { key: 'hair', label: 'Hair' },
  { key: 'firstEpisode', label: 'First Seen' },
]

export const SKILL_ICONS = {
  Healing: '💧', Bloodbending: '🩸', Metalbending: '⛓️', Sandbending: '🏜️', Plantbending: '🌿',
  Lavabending: '🌋', Energybending: '✨', Lightning: '⚡', 'Lightning redirection': '↩️',
  Combustion: '💥', 'Chi-blocking': '🤜', 'Seismic sense': '👣', Swords: '⚔️', Archery: '🏹',
  Boomerang: '🪃', 'War fans': '🪭', Knives: '🔪',
}

const BENDERS = new Set(['Waterbender', 'Earthbender', 'Firebender', 'Airbender'])

function setResult(guessArr, answerArr) {
  const g = new Set(guessArr)
  const a = new Set(answerArr)
  if (g.size === a.size && [...g].every(x => a.has(x))) return 'exact'
  if ([...g].some(x => a.has(x))) return 'partial'
  return 'wrong'
}

// The Avatar bends every element, so a single-element bender shares that
// element with them without being one.
function bendingResult(guess, answer) {
  if (guess === answer) return 'exact'
  if ((guess === 'Avatar' && BENDERS.has(answer)) || (answer === 'Avatar' && BENDERS.has(guess))) return 'partial'
  return 'wrong'
}

function numResult(guess, answer) {
  if (guess == null && answer == null) return { result: 'exact', arrow: null }
  if (guess == null || answer == null) return { result: 'wrong', arrow: null }
  if (guess === answer) return { result: 'exact', arrow: null }
  return { result: 'wrong', arrow: answer > guess ? 'up' : 'down' }
}

export function compareGuess(guess, answer) {
  const cells = {}
  cells.portrait = { result: guess.name === answer.name ? 'exact' : 'neutral' }
  cells.gender = { result: guess.gender === answer.gender ? 'exact' : 'wrong', text: guess.gender }
  cells.nation = { result: guess.nation === answer.nation ? 'exact' : 'wrong', text: guess.nation }
  cells.bending = { result: bendingResult(guess.bending, answer.bending), text: guess.bending }
  cells.skills = { result: setResult(guess.skills, answer.skills), skills: guess.skills }
  cells.affiliation = {
    result: guess.affiliation === answer.affiliation ? 'exact' : 'wrong',
    text: guess.affiliation,
  }
  cells.age = { ...numResult(guess.age, answer.age), text: formatAge(guess.age) }
  cells.hair = { result: guess.hair === answer.hair ? 'exact' : 'wrong', text: guess.hair }
  cells.firstEpisode = {
    ...numResult(guess.firstEpisode, answer.firstEpisode),
    text: formatEpisode(guess.firstEpisode),
  }
  return cells
}

// `history` lists are newest-first; scan top-down for the first entry the
// viewer has reached.
function at(list, maxEpisode) {
  if (!list?.length) return null
  for (const e of list) {
    if (e.episode != null && e.episode <= maxEpisode) return e
  }
  return null
}

// A character as they were known at `maxEpisode`, so a book-limited board never
// shows anything from further ahead than the player has watched. A skill not yet
// shown reads as none; an affiliation with no dated entry keeps the oldest one.
export function atEpisode(c, maxEpisode) {
  if (maxEpisode == null) return c
  const h = c.history
  if (!h) return c
  const out = { ...c }
  const aff = at(h.affiliation, maxEpisode)
  if (aff) out.affiliation = aff.value
  if (h.skills) {
    out.skills = h.skills
      .filter(e => e.episode != null && e.episode <= maxEpisode)
      .map(e => e.value)
  }
  return out
}

export function formatAge(age) {
  return age == null ? '?' : String(age)
}

// 1..61 -> "B2 E06": book number then episode within the book
export function episodeParts(n) {
  if (n == null) return null
  const book = n <= 20 ? 1 : n <= 40 ? 2 : 3
  const ep = n - (book === 1 ? 0 : book === 2 ? 20 : 40)
  return { book, ep }
}

export function formatEpisode(n) {
  const p = episodeParts(n)
  if (!p) return '?'
  return `B${p.book} E${String(p.ep).padStart(2, '0')}`
}

export const BOOK_NAMES = { 1: 'Water', 2: 'Earth', 3: 'Fire' }

export function bookLabel(book) {
  return book ? `Book ${book.number}: ${book.name}` : null
}

export function displayName(c) {
  return c.name
}
