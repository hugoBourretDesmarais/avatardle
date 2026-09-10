// Asserts that a book-limited card shows what a viewer at that point knows.
// Run with: node tools/check_spoilers.mjs
import { readFileSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const src = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'src')
const chars = JSON.parse(readFileSync(resolve(src, 'data/characters.json'), 'utf8'))
const books = JSON.parse(readFileSync(resolve(src, 'data/books.json'), 'utf8'))
const compare = await import('data:text/javascript;base64,' +
  Buffer.from(readFileSync(resolve(src, 'game/compare.js'), 'utf8')).toString('base64'))

const byName = Object.fromEntries(chars.map(c => [c.name, c]))
const endOf = name => {
  if (name === null) return null
  const b = books.find(x => x.name === name)
  if (!b) throw new Error(`no such book: ${name}`)
  return b.endEpisode
}

// [character, book limit (null = whole series), expected fields]
const CASES = [
  ['Zuko', 'Water', { affiliation: 'Fire Nation Royal Family', skills: ['Swords'] }],
  ['Zuko', 'Earth', { affiliation: 'Fire Nation Royal Family', skills: ['Lightning redirection', 'Swords'] }],
  ['Zuko', null, { affiliation: 'Team Avatar' }],
  ['Katara', 'Water', { skills: ['Healing'] }],
  ['Katara', 'Earth', { skills: ['Healing'] }],
  ['Katara', null, { skills: ['Healing', 'Bloodbending'] }],
  ['Toph Beifong', 'Earth', { affiliation: 'Team Avatar', skills: ['Metalbending', 'Seismic sense'] }],
  ['Iroh', 'Earth', { affiliation: 'Fire Nation Royal Family' }],
  ['Iroh', null, { affiliation: 'Order of the White Lotus' }],
  ['Suki', 'Earth', { affiliation: 'Kyoshi Warriors' }],
  ['Suki', null, { affiliation: 'Team Avatar' }],
  ['Aang', 'Earth', { skills: [] }],
  ['Aang', null, { skills: ['Energybending'] }],
  ['Ozai', 'Earth', { skills: [] }],
]

let failed = 0
for (const [name, book, expected] of CASES) {
  const c = byName[name]
  if (!c) { console.log(`MISSING ${name}`); failed++; continue }
  const got = compare.atEpisode(c, endOf(book))
  for (const [k, want] of Object.entries(expected)) {
    const have = Array.isArray(got[k]) ? [...got[k]].sort() : got[k]
    const w = Array.isArray(want) ? [...want].sort() : want
    if (JSON.stringify(have) !== JSON.stringify(w)) {
      console.log(`FAIL ${name} @ ${book ?? 'no limit'}: ${k} = ` +
        `${JSON.stringify(have)}, expected ${JSON.stringify(w)}`)
      failed++
    }
  }
}

// Toph must be absent from a Book 1 board, and present from Book 2 on.
const water = books.find(b => b.name === 'Water').endEpisode
if (byName['Toph Beifong'].firstEpisode <= water) { console.log('FAIL Toph in Book 1'); failed++ }

// Invariants that must hold for every character at every book.
for (const c of chars) {
  for (const b of books) {
    if (c.firstEpisode > b.endEpisode) continue
    const got = compare.atEpisode(c, b.endEpisode)
    if (!got.affiliation) { console.log(`FAIL ${c.name} @ ${b.name}: no affiliation`); failed++ }
    if (got.skills.some(s => !c.skills.includes(s))) {
      console.log(`FAIL ${c.name} @ ${b.name}: skills not a subset of the latest`); failed++
    }
  }
  if (!(c.firstEpisode >= 1 && c.firstEpisode <= 61)) { console.log(`FAIL ${c.name}: episode ${c.firstEpisode}`); failed++ }
  for (const field of ['affiliation', 'skills']) {
    for (const e of c.history?.[field] ?? []) {
      if (e.episode < c.firstEpisode || e.episode > 61) {
        console.log(`FAIL ${c.name}: ${field} history episode ${e.episode} out of range`); failed++
      }
    }
  }
}

console.log(failed ? `\n${failed} failures` : `\nall ${CASES.length} cases + invariants pass`)
process.exit(failed ? 1 : 0)
