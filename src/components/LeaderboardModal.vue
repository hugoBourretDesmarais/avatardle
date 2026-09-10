<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { fetchLeaderboard, fetchMe, logoutPlayer } from '../game/api.js'
import AccountForm from './AccountForm.vue'

const props = defineProps({
  account: { type: Object, default: null },
  day: { type: String, required: true },
  // Today's daily win, if it was solved before this account existed.
  pendingWin: { type: Object, default: null },
})
const emit = defineEmits(['close', 'account'])

const sort = ref('streak')
const entries = ref([])
const loading = ref(true)
const me = ref(null)

const SORTS = [
  { key: 'streak', label: 'Streak' },
  { key: 'wins', label: 'Wins' },
  { key: 'avg', label: 'Avg guesses' },
]

async function load() {
  loading.value = true
  const r = await fetchLeaderboard(sort.value, props.day)
  entries.value = r?.entries ?? []
  loading.value = false
  if (props.account) me.value = await fetchMe(props.account)
}

watch(sort, load)
onMounted(load)

const myRank = computed(() => {
  if (!props.account) return null
  const hit = entries.value.find(e => e.name === props.account.name)
  return hit?.rank ?? null
})

function onAccount(account) {
  emit('account', account)
  load()
}

function signOut() {
  logoutPlayer(props.account)
  emit('account', null)
  me.value = null
}
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal panel">
      <button class="modal-close" @click="emit('close')">×</button>
      <h2>Leaderboard</h2>

      <!-- Signed out: create an account or sign in -->
      <AccountForm v-if="!account" :pending-win="pendingWin" @account="onAccount" />

      <!-- Signed in -->
      <div v-else class="signed-in">
        <span class="who">Playing as <b>{{ account.name }}</b></span>
        <span class="who-actions">
          <button @click="signOut">Sign out</button>
        </span>
      </div>
      <p v-if="account && me" class="my-line">
        {{ me.wins }} ranked {{ me.wins === 1 ? 'win' : 'wins' }} ·
        streak {{ me.streak }} (best {{ me.maxStreak }}) ·
        avg {{ me.avg ?? '—' }}
        <template v-if="myRank"> · rank #{{ myRank }}</template>
      </p>

      <div class="tabs sort-tabs">
        <button
          v-for="s in SORTS" :key="s.key" :class="{ on: sort === s.key }"
          @click="sort = s.key">{{ s.label }}</button>
      </div>

      <p v-if="loading" class="empty">Loading…</p>
      <table v-else-if="entries.length" class="board">
        <thead>
          <tr><th>#</th><th>Player</th><th>Arc</th><th>Streak</th><th>Wins</th><th>Avg</th></tr>
        </thead>
        <tbody>
          <tr v-for="e in entries" :key="e.name" :class="{ mine: account && e.name === account.name }">
            <td>{{ e.rank }}</td>
            <td class="p-name">{{ e.name }}</td>
            <td class="p-arc" :title="e.arcLimit ? `Spoiler limit: ${e.arcLimit}` : 'No spoiler limit'">
              <span>{{ e.arcLimit ?? '—' }}</span>
            </td>
            <td>{{ e.streak }}<span class="best"> / {{ e.maxStreak }}</span></td>
            <td>{{ e.wins }}</td>
            <td>{{ e.avg ?? '—' }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty">
        Nobody's on the board yet — win today's character to be first.
      </p>

    </div>
  </div>
</template>

<style scoped>
h2 { margin-bottom: 12px; }

.tabs { display: flex; gap: 8px; margin-bottom: 10px; }
.tabs button {
  flex: 1;
  font-family: inherit;
  font-weight: 700;
  font-size: 13px;
  padding: 7px;
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
.sort-tabs { margin-top: 14px; }

.who-actions button {
  font-family: inherit;
  font-weight: 700;
  font-size: 12px;
  padding: 6px 10px;
  border-radius: 6px;
  border: 2px solid var(--tan);
  background: var(--parchment);
  color: var(--brown-dark);
}

.signed-in {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  font-size: 14px;
  color: var(--brown);
}
.who-actions { display: flex; gap: 6px; }
.my-line {
  margin: 8px 0 0;
  font-size: 13px;
  color: var(--brown-dark);
  font-weight: 700;
}

.board { width: 100%; border-collapse: collapse; font-size: 14px; }
.board th {
  text-align: left;
  font-size: 11px;
  text-transform: uppercase;
  color: var(--brown);
  border-bottom: 2px solid var(--tan);
  padding: 4px 6px;
}
.board td { padding: 6px; border-top: 1px solid var(--tan); }
.board tr.mine { background: var(--parchment-dark); }
.p-name { font-weight: 700; color: var(--brown-dark); overflow-wrap: anywhere; }
.p-arc { font-size: 12px; color: var(--brown); }
/* Auto table layout ignores max-width on a cell, so the clamp lives on a
   block inside it. */
.p-arc span {
  display: block;
  max-width: 90px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Six columns don't fit a phone at the default padding; trimming the gutters
   keeps every value readable rather than truncating the arc to nothing. */
@media (max-width: 480px) {
  .board { font-size: 13px; }
  .board th { padding: 4px 3px; }
  .board td { padding: 6px 3px; }
  .p-arc span { max-width: 74px; }
}
.best { color: var(--brown); font-size: 12px; }

.empty { text-align: center; font-style: italic; color: var(--brown); margin: 18px 0; }
</style>
