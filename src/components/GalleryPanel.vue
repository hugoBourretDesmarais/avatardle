<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  characters: { type: Array, required: true },
  excluded: { type: Set, required: true },
  bookLimit: { type: String, default: null },
})
const emit = defineEmits(['open', 'toggle', 'set-all'])

const base = import.meta.env.BASE_URL
const query = ref('')
const sort = ref('name')

function norm(s) {
  return String(s ?? '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
}

// Searching affiliation/nation/bending as well as the name makes the gallery
// browsable by concept ("firebender", "dai li", "spirit"), not just by name.
function haystack(c) {
  return norm([
    c.name, ...(c.aliases || []), c.affiliation, c.nation, c.origin, c.bending,
    ...c.skills, c.hair,
  ].filter(Boolean).join(' '))
}

const includedCount = computed(
  () => props.characters.filter(c => !props.excluded.has(c.name)).length)

const indexed = computed(() => props.characters.map(c => ({ c, hay: haystack(c) })))

const results = computed(() => {
  const q = norm(query.value.trim())
  let list = indexed.value
  if (q) {
    const terms = q.split(/\s+/)
    list = list.filter(({ hay }) => terms.every(t => hay.includes(t)))
  }
  const out = list.map(x => x.c)
  const key = sort.value
  return [...out].sort((a, b) => {
    if (key === 'name') return a.name.localeCompare(b.name)
    if (key === 'debut') return (a.firstEpisode ?? 0) - (b.firstEpisode ?? 0)
    if (key === 'age') return (b.age ?? -1) - (a.age ?? -1)
    return 0
  })
})
</script>

<template>
  <section class="gallery">
    <div class="controls panel">
      <input
        v-model="query" type="search" class="search"
        placeholder="Search name, nation, bending, affiliation..."
        autocomplete="off" spellcheck="false" />
      <div class="controls-row">
        <label class="sort">
          Sort
          <select v-model="sort">
            <option value="name">Name (A–Z)</option>
            <option value="debut">First appearance</option>
            <option value="bounty">Highest bounty</option>
            <option value="height">Tallest</option>
          </select>
        </label>
        <span class="count">
          {{ results.length }} of {{ characters.length }}<span v-if="bookLimit"> (up to Book {{ bookLimit }})</span>
        </span>
      </div>

      <div class="pool-row">
        <span class="pool-count">
          🎲 <b>{{ includedCount }}</b> of {{ characters.length }} in the practice pool
        </span>
        <span class="pool-actions">
          <button @click="emit('set-all', { chars: results, included: true })">
            Include{{ query ? ' shown' : ' all' }}
          </button>
          <button @click="emit('set-all', { chars: results, included: false })">
            Exclude{{ query ? ' shown' : ' all' }}
          </button>
        </span>
      </div>
    </div>

    <div v-if="results.length" class="cards">
      <div
        v-for="c in results" :key="c.name" class="card"
        :class="{ dimmed: excluded.has(c.name) }">
        <label
          class="pick" :title="excluded.has(c.name)
            ? `${c.name} is excluded from practice — click to include`
            : `${c.name} is in the practice pool — click to exclude`"
          @click.stop>
          <input
            type="checkbox" :checked="!excluded.has(c.name)"
            @change="emit('toggle', c)" />
        </label>
        <button class="card-open" :title="c.name" @click="emit('open', c)">
          <img :src="base + 'portraits/' + c.portrait" :alt="c.name" loading="lazy" decoding="async" />
          <span class="card-name">{{ c.name }}</span>
        </button>
      </div>
    </div>
    <p v-else class="empty panel">
      No character matches “{{ query }}”.
    </p>
  </section>
</template>

<style scoped>
.gallery {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 14px;
  align-items: center;
}

.controls {
  width: min(560px, 100%);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.search {
  width: 100%;
  font-family: inherit;
  font-size: 17px;
  padding: 10px 14px;
  border-radius: 8px;
  border: 2px solid var(--tan);
  background: #fffdf5;
  color: var(--ink);
  outline: none;
}
.search::placeholder { color: #a08c66; }

.controls-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.sort {
  font-size: 13px;
  font-weight: 700;
  color: var(--brown-dark);
  display: flex;
  align-items: center;
  gap: 6px;
}
.sort select {
  font-family: inherit;
  font-size: 13px;
  padding: 4px 6px;
  border-radius: 6px;
  border: 2px solid var(--tan);
  background: var(--parchment-dark);
  color: var(--brown-dark);
  font-weight: 700;
}
.count { font-size: 13px; color: var(--brown); font-weight: 600; }

.cards {
  width: 100%;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(104px, 1fr));
  gap: 10px;
}

.pool-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  border-top: 1px solid var(--tan);
  padding-top: 9px;
}
.pool-count { font-size: 13px; color: var(--brown); }
.pool-count b { color: var(--brown-dark); }
.pool-actions { display: flex; gap: 6px; }
.pool-actions button {
  font-family: inherit;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 9px;
  border-radius: 6px;
  border: 2px solid var(--tan);
  background: var(--parchment-dark);
  color: var(--brown-dark);
}
.pool-actions button:hover { filter: brightness(.96); }

.card {
  position: relative;
  border-radius: 10px;
  border: 3px solid var(--tan);
  background: var(--parchment);
  transition: transform .12s, box-shadow .12s, opacity .12s;
}
.card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.3);
  border-color: var(--brown);
}
.card.dimmed { opacity: .45; }
.card.dimmed:hover { opacity: .75; }

.card-open {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 6px 4px 8px;
  background: none;
  border: none;
  border-radius: 8px;
}
.card-open:focus-visible { outline: 2px solid var(--brown); }

.pick {
  position: absolute;
  top: 3px;
  right: 3px;
  z-index: 2;
  background: rgba(255, 253, 245, 0.92);
  border-radius: 5px;
  padding: 1px 2px;
  line-height: 0;
  cursor: pointer;
}
.pick input {
  width: 16px;
  height: 16px;
  accent-color: var(--green);
  cursor: pointer;
  margin: 0;
}

.card img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  object-position: top;
  border-radius: 6px;
  background: #fff;
}
.card-name {
  font-size: 12px;
  font-weight: 700;
  color: var(--brown-dark);
  line-height: 1.15;
  text-align: center;
  overflow-wrap: anywhere;
}
.card-codename {
  font-size: 10px;
  font-style: italic;
  color: var(--brown);
  line-height: 1.1;
  text-align: center;
  overflow-wrap: anywhere;
}

.empty {
  padding: 20px;
  font-style: italic;
  color: var(--brown);
}

@media (max-width: 760px) {
  .cards { grid-template-columns: repeat(auto-fill, minmax(88px, 1fr)); gap: 8px; }
  .card-name { font-size: 11px; }
}
</style>
