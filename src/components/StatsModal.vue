<script setup>
import { computed, ref } from 'vue'
import { loadStats, currentStreak } from '../game/state.js'

const props = defineProps({
  characters: { type: Array, required: true },
})
const emit = defineEmits(['close'])

const base = import.meta.env.BASE_URL
const stats = loadStats()
const liveStreak = currentStreak()
const tab = ref('classic')

const byName = new Map(props.characters.map(c => [c.name, c]))
const m = computed(() => stats[tab.value])

const winRate = computed(() => (m.value.played ? Math.round((m.value.wins / m.value.played) * 100) : 0))

const avgGuesses = computed(() => {
  const entries = Object.entries(m.value.tries)
  const games = entries.reduce((a, [, n]) => a + n, 0)
  if (!games) return null
  const total = entries.reduce((a, [k, n]) => a + Number(k) * n, 0)
  return (total / games).toFixed(1)
})

const bestGame = computed(() => {
  const keys = Object.keys(m.value.tries).map(Number)
  return keys.length ? Math.min(...keys) : null
})

const distribution = computed(() => {
  const entries = Object.entries(m.value.tries)
    .map(([k, v]) => [Number(k), v])
    .sort((a, b) => a[0] - b[0])
  const max = Math.max(1, ...entries.map(e => e[1]))
  return entries.map(([tries, count]) => ({ tries, count, pct: (count / max) * 100 }))
})

const topGuessed = computed(() => {
  const entries = Object.entries(m.value.guessed)
  const max = Math.max(1, ...entries.map(e => e[1]))
  return entries
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, 5)
    .map(([name, count]) => ({ name, count, pct: (count / max) * 100, char: byName.get(name) }))
})

const hasData = computed(() => m.value.played > 0 || m.value.guesses > 0)
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal panel">
      <button class="modal-close" @click="emit('close')">×</button>
      <h2>Statistics</h2>

      <div class="tabs">
        <button :class="{ on: tab === 'classic' }" @click="tab = 'classic'">🌀 Classic</button>
        <button :class="{ on: tab === 'practice' }" @click="tab = 'practice'">🎲 Practice</button>
      </div>

      <div class="stat-row">
        <div class="stat"><b>{{ m.played }}</b><span>Played</span></div>
        <div class="stat"><b>{{ m.wins }}</b><span>Won</span></div>
        <div class="stat"><b>{{ winRate }}%</b><span>Win rate</span></div>
      </div>

      <div class="stat-row">
        <div class="stat"><b>{{ m.guesses }}</b><span>Guesses</span></div>
        <div class="stat"><b>{{ avgGuesses ?? '—' }}</b><span>Avg to win</span></div>
        <div class="stat"><b>{{ bestGame ?? '—' }}</b><span>Best game</span></div>
      </div>

      <div v-if="tab === 'classic'" class="stat-row streaks">
        <div class="stat"><b>🔥 {{ liveStreak }}</b><span>Current streak</span></div>
        <div class="stat"><b>{{ m.maxStreak }}</b><span>Best streak</span></div>
      </div>
      <p v-if="tab === 'classic'" class="streak-note">
        A streak counts consecutive days won — miss a day and it resets to zero.
      </p>

      <template v-if="hasData">
        <h3 v-if="distribution.length">Guesses per win</h3>
        <div class="dist">
          <div v-for="d in distribution" :key="d.tries" class="dist-row">
            <span class="dist-label">{{ d.tries }}</span>
            <div class="dist-bar" :style="{ width: Math.max(d.pct, 8) + '%' }">{{ d.count }}</div>
          </div>
        </div>

        <h3 v-if="topGuessed.length">Most guessed characters</h3>
        <ol class="top">
          <li v-for="t in topGuessed" :key="t.name">
            <img
              v-if="t.char" :src="base + 'portraits/' + t.char.portrait" :alt="t.name"
              loading="lazy" />
            <span class="top-name">{{ t.name }}</span>
            <span class="top-track"><span class="top-fill" :style="{ width: t.pct + '%' }"></span></span>
            <span class="top-count">{{ t.count }}×</span>
          </li>
        </ol>
      </template>
      <p v-else class="empty">
        {{ tab === 'classic'
          ? 'Play today\'s character to start your classic stats.'
          : 'Play a practice round to start your practice stats.' }}
      </p>
    </div>
  </div>
</template>

<style scoped>
.tabs {
  display: flex;
  gap: 8px;
  margin: 14px 0 6px;
}
.tabs button {
  flex: 1;
  font-family: inherit;
  font-weight: 700;
  font-size: 14px;
  padding: 8px;
  border-radius: 8px;
  border: 2px solid var(--tan);
  background: var(--parchment);
  color: var(--brown);
}
.tabs button.on {
  background: var(--parchment-dark);
  color: var(--brown-dark);
  border-color: var(--brown);
}

.stat-row {
  display: flex;
  justify-content: space-around;
  margin: 12px 0;
  gap: 8px;
}
.streaks { justify-content: center; gap: 42px; }
.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 0;
}
.stat b { font-size: 24px; color: var(--brown-dark); line-height: 1.1; }
.stat span {
  font-size: 11px;
  text-transform: uppercase;
  color: var(--brown);
  text-align: center;
  letter-spacing: .3px;
}
.streak-note {
  margin: 0 0 6px;
  font-size: 12px;
  font-style: italic;
  color: var(--brown);
  text-align: center;
}

h3 {
  font-family: 'Lilita One', cursive;
  color: var(--brown-dark);
  margin: 16px 0 6px;
  font-size: 17px;
}
.dist { display: flex; flex-direction: column; gap: 4px; }
.dist-row { display: flex; align-items: center; gap: 8px; }
.dist-label { width: 20px; text-align: right; font-weight: 700; font-size: 13px; }
.dist-bar {
  background: var(--green);
  color: #fff;
  font-weight: 700;
  font-size: 12px;
  border-radius: 4px;
  padding: 2px 6px;
  text-align: right;
}

.top {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  counter-reset: rank;
}
.top li {
  display: flex;
  align-items: center;
  gap: 8px;
}
.top img {
  width: 30px;
  height: 30px;
  object-fit: cover;
  object-position: top;
  border-radius: 5px;
  border: 1px solid var(--tan);
  background: #fff;
  flex: none;
}
.top-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--brown-dark);
  width: 34%;
  overflow-wrap: anywhere;
  line-height: 1.15;
}
.top-track {
  flex: 1;
  height: 9px;
  background: var(--parchment-dark);
  border-radius: 5px;
  overflow: hidden;
}
.top-fill {
  display: block;
  height: 100%;
  background: var(--yellow);
}
.top-count {
  font-size: 12px;
  font-weight: 700;
  color: var(--brown);
  min-width: 26px;
  text-align: right;
}

.empty { text-align: center; font-style: italic; color: var(--brown); margin-top: 18px; }
</style>
