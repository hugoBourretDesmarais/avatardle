<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import characters from './data/characters.json'
import books from './data/books.json'
import { COLUMNS, atEpisode, compareGuess } from './game/compare.js'
import {
  dailyIndex, dailyNumber, loadDailyState, loadBookLimit, loadExcluded, localDateString,
  loadAccount, msUntilMidnight, randomIndex, recordGuess, recordPracticeStart, recordWin,
  saveAccount, saveBookLimit, saveDailyState, saveExcluded, currentStreak,
  loadPromptedDay, savePromptedDay,
} from './game/state.js'
import GuessInput from './components/GuessInput.vue'
import GuessRow from './components/GuessRow.vue'
import WinPanel from './components/WinPanel.vue'
import HelpModal from './components/HelpModal.vue'
import StatsModal from './components/StatsModal.vue'
import CluesPanel from './components/CluesPanel.vue'
import { apiEnabled, fetchCount, reportSolve, submitResult } from './game/api.js'
import GalleryPanel from './components/GalleryPanel.vue'
import LeaderboardModal from './components/LeaderboardModal.vue'
import WinPrompt from './components/WinPrompt.vue'
import Confetti from './components/Confetti.vue'
import ArtBackground from './components/ArtBackground.vue'
import GameLogo from './components/GameLogo.vue'
import StreakFlame from './components/StreakFlame.vue'
import Icon from './components/Icon.vue'
import CharacterModal from './components/CharacterModal.vue'
import SettingsModal from './components/SettingsModal.vue'

const mode = ref('daily') // 'daily' | 'practice' | 'gallery'
const showHelp = ref(false)
const showStats = ref(false)
const showSettings = ref(false)
const galleryPick = ref(null)
const showBoard = ref(false)
const showWinPrompt = ref(false)
const account = ref(loadAccount())
const streak = ref(currentStreak())
const bookLimit = ref(loadBookLimit())
const excluded = ref(loadExcluded())
const solveCount = ref(null)

// The winning row flips one tile at a time; hold the result back until the
// last one has landed so the reveal isn't spoiled by the panel appearing.
const TILE_STAGGER_MS = 280
const TILE_FLIP_MS = 500
const REVEAL_MS = COLUMNS.length * TILE_STAGGER_MS + TILE_FLIP_MS
const revealing = ref(false)
const celebrating = ref(false)
let revealTimer = null

function finishReveal() {
  if (!revealing.value) return
  clearTimeout(revealTimer)
  revealing.value = false
  celebrating.value = true
  setTimeout(() => (celebrating.value = false), 3000)
  maybePromptSignIn()
}

function startCelebration() {
  // Nothing to wait for when the flip is suppressed, so don't stall the panel.
  if (window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) {
    revealing.value = false
    celebrating.value = false
    maybePromptSignIn()
    return
  }
  revealing.value = true
  celebrating.value = false
  clearTimeout(revealTimer)
  // A backgrounded tab pauses CSS animations, so animationend can't be the
  // only trigger — the row's 'revealed' event just gets there first when the
  // tab is actually painting.
  revealTimer = setTimeout(finishReveal, REVEAL_MS)
}

async function refreshCount() {
  if (!apiEnabled) return
  const r = await fetchCount(localDateString(), bookLimit.value)
  if (r) solveCount.value = r.count
}

const limitBook = computed(
  () => (bookLimit.value ? books.find(b => b.name === bookLimit.value) ?? null : null))

// Everything the player can meet — answers, suggestions, gallery — comes from
// here, and each card is rewound to how the character was known at the limit,
// so a skill learned later in the series doesn't leak onto an early board.
const pool = computed(() => {
  const book = limitBook.value
  if (!book) return characters
  return characters
    .filter(c => c.firstEpisode <= book.endEpisode)
    .map(c => atEpisode(c, book.endEpisode))
})

const byName = computed(() => new Map(pool.value.map(c => [c.name, c])))

// Exclusions only narrow practice; the daily stays shared between players.
const practicePool = computed(() => pool.value.filter(c => !excluded.value.has(c.name)))

function toggleExcluded(c) {
  const next = new Set(excluded.value)
  if (next.has(c.name)) next.delete(c.name)
  else next.add(c.name)
  excluded.value = next
  saveExcluded(next)
}

function setAllExcluded({ chars, included }) {
  const next = new Set(excluded.value)
  for (const c of chars) {
    if (included) next.delete(c.name)
    else next.add(c.name)
  }
  excluded.value = next
  saveExcluded(next)
}

const daily = reactive({
  number: dailyNumber(),
  answer: null,
  guesses: [], // {char, cells}
  won: false,
  triesAtWin: 0,
})
const practice = reactive({ answer: null, guesses: [], won: false, counted: false })

const yesterdayAnswer = computed(
  () => pool.value[dailyIndex(pool.value.length, localDateString(-1))])

const game = computed(() => (mode.value === 'practice' ? practice : daily))
const guessedNames = computed(() => new Set(game.value.guesses.map(g => g.char.name)))

// The daily can only be won once, and the win is reported as it lands, so
// signing in afterwards would otherwise leave that day unranked forever.
const pendingWin = computed(() => (daily.won && daily.answer
  ? {
    day: localDateString(),
    arcLimit: bookLimit.value,
    guesses: daily.triesAtWin || daily.guesses.length,
    name: daily.answer.name,
  }
  : null))

function recordDailyWin(acct) {
  const w = pendingWin.value
  if (!acct || !w) return null
  return submitResult(acct, w.day, w.arcLimit, w.guesses, w.name)
}

// Invite a signed-out winner to save the day's result. Held until the reveal
// has finished so the pop-up doesn't land on top of the flipping row.
function maybePromptSignIn() {
  if (!apiEnabled || account.value || mode.value !== 'daily' || !daily.won) return
  const today = localDateString()
  if (loadPromptedDay() === today) return
  savePromptedDay(today)
  setTimeout(() => { showWinPrompt.value = true }, 900)
}

function restoreDaily() {
  revealing.value = false
  celebrating.value = false
  daily.answer = pool.value[dailyIndex(pool.value.length)]
  daily.guesses = []
  daily.won = false
  const s = loadDailyState(bookLimit.value)
  for (const name of s.guesses) {
    const char = byName.value.get(name)
    if (char) daily.guesses.unshift({ char, cells: compareGuess(char, daily.answer), animate: false })
  }
  daily.won = s.won
  daily.triesAtWin = s.guesses.length
}

function persistDaily() {
  saveDailyState({
    date: localDateString(),
    bookLimit: bookLimit.value,
    guesses: [...daily.guesses].reverse().map(g => g.char.name),
    won: daily.won,
  })
}

function setAccount(next) {
  account.value = next
  saveAccount(next)
}

function onPromptAccount(next) {
  setAccount(next)
  showWinPrompt.value = false
}

function applyBookLimit(next) {
  bookLimit.value = next
  saveBookLimit(next)
  restoreDaily()
  newPractice()
  galleryPick.value = null
  solveCount.value = null
  refreshCount()
}

function submitGuess(char) {
  const g = game.value
  if (g.won || guessedNames.value.has(char.name)) return
  const isDaily = mode.value === 'daily'
  const statMode = isDaily ? 'classic' : 'practice'

  if (!isDaily && !practice.counted) {
    practice.counted = true
    recordPracticeStart()
  }
  const cells = compareGuess(char, g.answer)
  g.guesses.unshift({ char, cells, animate: true })
  recordGuess(statMode, char.name)

  if (char.name === g.answer.name) {
    g.won = true
    startCelebration()
    if (isDaily) daily.triesAtWin = daily.guesses.length
    recordWin(statMode, g.guesses.length)
    if (isDaily) {
      streak.value = currentStreak()
      reportSolve(localDateString(), bookLimit.value, char.name).then(r => {
        if (r) solveCount.value = r.count
      })
      recordDailyWin(account.value)
    }
  }
  if (isDaily) persistDaily()
}

// Opens a round for you. Practice honours the gallery selection; the daily
// doesn't, since exclusions are a practice-only preference.
function randomStarter() {
  const src = mode.value === 'practice' && practicePool.value.length
    ? practicePool.value
    : pool.value
  const candidates = src.filter(c => !guessedNames.value.has(c.name))
  if (!candidates.length) return
  submitGuess(candidates[randomIndex(candidates.length)])
}

function newPractice() {
  revealing.value = false
  celebrating.value = false
  clearTimeout(revealTimer)
  const src = practicePool.value.length ? practicePool.value : pool.value
  practice.answer = src[randomIndex(src.length)]
  practice.guesses = []
  practice.won = false
  practice.counted = false
}

// countdown to next daily
const countdown = ref('')
let timer = null
function tick() {
  const ms = msUntilMidnight()
  const h = String(Math.floor(ms / 3600000)).padStart(2, '0')
  const m = String(Math.floor((ms % 3600000) / 60000)).padStart(2, '0')
  const s = String(Math.floor((ms % 60000) / 1000)).padStart(2, '0')
  countdown.value = `${h}:${m}:${s}`
}

onMounted(() => {
  restoreDaily()
  newPractice()
  refreshCount()
  // Retries a win the server never got; /result ignores a day it already has.
  recordDailyWin(account.value)
  tick()
  timer = setInterval(tick, 1000)
  if (!localStorage.getItem('avdle:visited')) {
    showHelp.value = true
    localStorage.setItem('avdle:visited', '1')
  }
})
onUnmounted(() => {
  clearInterval(timer)
  clearTimeout(revealTimer)
})

// Rotates the backdrop once a day so the page doesn't look static day to day.
const bgSeed = computed(() => {
  // ?bg=0..4 forces a palette, for previewing the other times of day
  const forced = Number(new URLSearchParams(location.search).get('bg'))
  if (Number.isInteger(forced)) return forced
  const d = localDateString()
  return (Number(d.slice(0, 4)) * 372 + Number(d.slice(5, 7)) * 31 + Number(d.slice(8, 10)))
})

const base = import.meta.env.BASE_URL
</script>

<template>
  <div class="page">
    <ArtBackground :seed="bgSeed" />
    <header class="header">
      <GameLogo />

      <div class="modes">
        <button class="mode-btn" :class="{ active: mode === 'daily' }" title="Classic (daily)"
          @click="mode = 'daily'">
          <span class="mode-ico">🌀</span>
          <span v-if="daily.won" class="mode-check">✔</span>
        </button>
        <button class="mode-btn" :class="{ active: mode === 'practice' }" title="Practice (unlimited)"
          @click="mode = 'practice'">
          <span class="mode-ico">🎲</span>
          <span v-if="practice.won" class="mode-check">✔</span>
        </button>
        <button class="mode-btn" :class="{ active: mode === 'gallery' }" title="Character gallery"
          @click="mode = 'gallery'">
          <span class="mode-ico">📖</span>
        </button>
      </div>

      <div class="toolbar panel">
        <button class="tool" title="Statistics" @click="showStats = true"><Icon name="chart" :size="23" /></button>
        <StreakFlame class="tool" :count="streak" />
        <span class="tool daily-num" :title="`Daily character #${daily.number}`">#{{ daily.number }}</span>
        <button
          class="tool" :class="{ 'tool-on': bookLimit }"
          :title="bookLimit ? `Spoiler limit: up to Book ${limitBook.number}: ${bookLimit}` : 'Settings'"
          @click="showSettings = true"><Icon name="lotus" :size="23" /></button>
        <button
          class="tool" :class="{ 'tool-on': account }"
          :title="account ? `Leaderboard — playing as ${account.name}` : 'Leaderboard'"
          @click="showBoard = true"><Icon name="trophy" :size="23" /></button>
        <button class="tool" title="How to play" @click="showHelp = true"><Icon name="help" :size="23" /></button>
      </div>

      <p v-if="limitBook" class="arc-banner" :class="'book-' + limitBook.name.toLowerCase()">
        <Icon name="book" :size="15" /> Spoiler-safe up to <b>Book {{ limitBook.number }}: {{ limitBook.name }}</b> — {{ pool.length }} of {{ characters.length }} characters
        <button class="arc-clear" @click="applyBookLimit(null)">clear</button>
      </p>
    </header>

    <main class="game">
      <template v-if="mode === 'gallery'">
        <section class="panel intro">
          <h2>CHARACTER GALLERY</h2>
          <p class="gallery-hint">
            {{ limitBook ? `The ${pool.length} characters seen up to Book ${limitBook.number}: ${limitBook.name}` : `All ${characters.length} characters in the game` }}.
            Search by name, nation, bending, skills or affiliation — then tap a card for the full details.
          </p>
        </section>
        <GalleryPanel
          :characters="pool" :excluded="excluded"
          :book-limit="limitBook ? `${limitBook.number}: ${limitBook.name}` : null"
          @open="galleryPick = $event" @toggle="toggleExcluded" @set-all="setAllExcluded" />
      </template>

      <template v-else>
        <section class="panel intro">
          <h2 v-if="mode === 'daily'">GUESS TODAY'S AVATAR CHARACTER!</h2>
          <h2 v-else>PRACTICE MODE — GUESS THE CHARACTER!</h2>
          <CluesPanel :answer="game.answer" :tries="game.guesses.length" :won="game.won" />
          <button v-if="mode === 'practice'" class="reset-btn" @click="newPractice">
            <Icon name="dice" :size="18" />
            New character
          </button>
          <p v-if="mode === 'daily' && solveCount !== null" class="solve-count">
            <b>{{ solveCount.toLocaleString() }}</b>
            {{ solveCount === 1 ? 'person' : 'people' }} already found out!
          </p>
          <p v-if="mode === 'practice' && excluded.size" class="practice-pool">
            Drawing from <b>{{ practicePool.length }}</b> of {{ pool.length }} characters
            <template v-if="!practicePool.length">— none selected, using all</template>
            <span class="pool-hint">· change this in the gallery</span>
          </p>
        </section>

        <WinPanel
          v-if="game.won && !revealing" :answer="game.answer" :tries="game.guesses.length" :mode="mode"
          :countdown="countdown" :guesses="game.guesses" :daily-number="daily.number"
          @practice="mode = 'practice'"
          @replay="newPractice" />

        <GuessInput
          v-if="!game.won" :characters="pool" :guessed="guessedNames"
          @guess="submitGuess" />

        <button
          v-if="!game.won && !game.guesses.length"
          class="starter-btn" @click="randomStarter">
          🎯 Random starting character
        </button>

        <section v-if="game.guesses.length" class="grid-wrap">
          <div class="grid">
            <div class="grid-head">
              <div v-for="col in COLUMNS" :key="col.key" class="head-cell">{{ col.label }}</div>
            </div>
            <GuessRow
            v-for="g in game.guesses" :key="g.char.name" :guess="g" :base="base"
            @revealed="finishReveal" />
          </div>
        </section>

        <p class="yesterday" v-if="mode === 'daily' && daily.number > 1">
          Yesterday's character #{{ daily.number - 1 }} was <b>{{ yesterdayAnswer.name }}</b>
        </p>
      </template>

      <footer class="footer">
        Fan-made game in the spirit of <a href="https://onepiecedle.net" target="_blank" rel="noreferrer">onepiecedle.net</a>
        · data from the <a href="https://avatar.fandom.com" target="_blank" rel="noreferrer">Avatar Wiki</a>
        · Avatar: The Last Airbender © Nickelodeon / Paramount
      </footer>
    </main>

    <Confetti v-if="celebrating" />
    <HelpModal v-if="showHelp" @close="showHelp = false" />
    <StatsModal v-if="showStats" :characters="characters" @close="showStats = false" />
    <CharacterModal
      v-if="galleryPick" :character="galleryPick" :limit-book="limitBook"
      @close="galleryPick = null" />
    <WinPrompt
      v-if="showWinPrompt && daily.answer" :answer="daily.answer.name"
      :tries="daily.triesAtWin || daily.guesses.length" :pending-win="pendingWin"
      @account="onPromptAccount" @close="showWinPrompt = false" />
    <LeaderboardModal
      v-if="showBoard" :account="account" :day="localDateString()" :pending-win="pendingWin"
      @account="setAccount" @close="showBoard = false" />
    <SettingsModal
      v-if="showSettings" :books="books" :characters="characters" :book-limit="bookLimit"
      @update:book-limit="applyBookLimit" @close="showSettings = false" />
  </div>
</template>

<style scoped>
.page {
  max-width: 860px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  width: 100%;
}

@keyframes logo-drop {
  from { transform: translateY(-18px) rotate(-6deg); opacity: 0; }
  to { transform: none; opacity: 1; }
}
@keyframes banner-in {
  from { transform: translateY(-6px); opacity: 0; }
  to { transform: none; opacity: 1; }
}

.modes { display: flex; gap: 16px; }
.mode-btn {
  position: relative;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: 3px solid #1c1712;
  background: radial-gradient(circle at 35% 30%, #4a3b28, #211a12 70%);
  font-size: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  filter: grayscale(.7) brightness(.85);
  transition: transform .12s, filter .12s;
}
.mode-btn.active {
  filter: none;
  transform: scale(1.09);
  border-color: #caa96b;
  box-shadow: 0 0 0 3px rgba(202, 169, 107, .35), 0 6px 16px rgba(0, 0, 0, .35);
}
.mode-btn:hover { filter: none; transform: translateY(-2px) scale(1.05); }
.mode-btn:active { transform: translateY(0) scale(.98); }
.mode-ico { pointer-events: none; }
.mode-check {
  position: absolute;
  bottom: -6px;
  right: -6px;
  background: var(--green);
  color: #fff;
  border-radius: 50%;
  width: 22px;
  height: 22px;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #fff;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
}
.tool {
  color: #6b4f27;
  display: inline-flex;
  align-items: center;
  gap: 3px;
  background: none;
  border: none;
  font-size: 20px;
  padding: 5px 8px;
  border-radius: 10px;
  color: var(--brown-dark);
}
button.tool:hover { background: rgba(140, 105, 55, .14); }
.daily-num {
  font-weight: 700;
  font-size: 15px;
  color: var(--brown-dark);
  background: var(--parchment-dark);
  border-radius: 12px;
  padding: 4px 10px;
}

.game {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 18px;
  gap: 16px;
}

.intro {
  width: min(560px, 100%);
  padding: 18px 22px;
  text-align: center;
}
.intro h2 {
  font-family: 'Lilita One', cursive;
  color: var(--brown-dark);
  letter-spacing: 1px;
  font-size: 22px;
  margin: 0 0 14px;
}

.reset-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-top: 14px;
  border: 2px solid var(--tan);
  background: var(--parchment-dark);
  color: var(--brown-dark);
  font-weight: 700;
  border-radius: 8px;
  padding: 9px 16px;
  font-size: 15px;
}
.reset-btn:hover { filter: brightness(.96); }

.gallery-hint {
  margin: 0;
  font-size: 14px;
  color: var(--brown);
}

.practice-pool {
  margin: 10px 0 0;
  font-size: 13px;
  color: var(--brown);
}

.solve-count {
  margin: 14px 0 0;
  font-size: 15px;
  color: var(--brown-dark);
}
.solve-count b { color: #c0392b; font-size: 17px; }

.starter-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: 2px solid var(--tan);
  background: var(--parchment);
  color: var(--brown-dark);
  font-weight: 700;
  font-size: 14px;
  border-radius: 8px;
  padding: 9px 16px;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
}
.starter-btn:hover { background: var(--parchment-dark); }
.pool-hint { opacity: .8; }

.tool-on {
  background: var(--parchment-dark);
  border-radius: 12px;
}

.arc-banner {
  margin: 0;
  animation: banner-in .3s ease both;
  padding: 6px 12px;
  border-radius: 14px;
  background: rgba(0, 0, 0, 0.28);
  border: 1px solid transparent;
}
.arc-banner.book-water { background: rgba(28, 84, 140, .55); border-color: rgba(120, 190, 240, .5); }
.arc-banner.book-earth { background: rgba(58, 98, 40, .55); border-color: rgba(150, 200, 110, .5); }
.arc-banner.book-fire { background: rgba(140, 40, 30, .55); border-color: rgba(240, 150, 110, .5); }
.arc-banner-unused {
  color: #fff;
  font-size: 13px;
  text-align: center;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: center;
}
.arc-clear {
  background: none;
  border: 1px solid rgba(255, 255, 255, 0.6);
  color: #fff;
  border-radius: 10px;
  font-size: 11px;
  padding: 2px 8px;
}
.arc-clear:hover { background: rgba(255, 255, 255, 0.15); }

.grid-wrap {
  width: 100%;
  overflow-x: auto;
  padding-bottom: 6px;
}
.grid {
  display: flex;
  flex-direction: column;
  gap: var(--tile-gap);
  width: max-content;
  margin: 0 auto;
}
/* A solid bar rather than per-cell tints: small white labels vanish against
   bright artwork otherwise. */
.grid-head {
  display: flex;
  gap: var(--tile-gap);
  background: rgba(10, 16, 30, .88);
  border-radius: 8px;
  padding: 5px var(--tile-gap);
  margin: 0 calc(var(--tile-gap) * -1) 2px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, .35);
}
.head-cell {
  width: var(--tile-size);
  font-weight: 700;
  font-size: clamp(9px, calc(var(--tile-size) * 0.16), 13px);
  text-transform: uppercase;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, .8);
  text-align: center;
  padding-bottom: 1px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  line-height: 1.15;
}

.yesterday {
  color: #fff;
  text-shadow: 0 1px 3px rgba(0, 0, 0, .9);
  font-size: 15px;
  margin: 4px 0 0;
  background: rgba(12, 18, 34, .68);
  padding: 6px 14px;
  border-radius: 14px;
}

.footer {
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 1px 3px rgba(0, 0, 0, .9);
  background: rgba(12, 18, 34, .6);
  padding: 8px 14px;
  border-radius: 12px;
  font-size: 12px;
  text-align: center;
  margin-top: 26px;
}
.footer a { color: #ffe9a8; }
</style>
