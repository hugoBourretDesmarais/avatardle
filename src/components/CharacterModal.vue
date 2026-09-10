<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import episodes from '../data/episodes.json'
import { BOOK_NAMES, SKILL_ICONS, episodeParts } from '../game/compare.js'

const props = defineProps({
  character: { type: Object, required: true },
  // The book the player has watched up to, or null for the whole series.
  limitBook: { type: Object, default: null },
})
const emit = defineEmits(['close'])

const base = import.meta.env.BASE_URL

const c = computed(() => props.character)

const bendingText = computed(() => {
  const x = c.value
  if (x.bending === 'Avatar' && x.elements?.length) return `Avatar — ${x.elements.join(', ')}`
  return x.bending
})

const skillsText = computed(() => {
  const s = c.value.skills
  return s.length ? s.map(t => `${SKILL_ICONS[t] ?? ''} ${t}`).join(', ') : 'None'
})

const ageText = computed(() => {
  const x = c.value
  if (x.age == null) return 'Unknown'
  return x.trueAge ? `${x.age} (biologically; ${x.trueAge} years old)` : String(x.age)
})

// True when the card is showing an older value than the series' last, so only
// the rows that actually moved get flagged rather than every row on the card.
function rewound(field) {
  const cap = props.limitBook?.endEpisode
  if (cap == null) return false
  return (c.value.history?.[field] ?? []).some(e => e.episode == null || e.episode > cap)
}

const debut = computed(() => {
  const x = c.value
  const p = episodeParts(x.firstEpisode)
  if (!p) return 'Unknown'
  const ep = episodes.find(e => e.n === x.firstEpisode)
  const note = x.firstEpisodeNote ? ` (${x.firstEpisodeNote})` : ''
  return `Book ${p.book}: ${BOOK_NAMES[p.book]} · Episode ${p.ep} “${ep?.title ?? '?'}”${note}`
})

const wikiUrl = computed(
  () => 'https://avatar.fandom.com/wiki/' + encodeURIComponent(c.value.wikiPage.replace(/ /g, '_')))

function onKey(e) {
  if (e.key === 'Escape') emit('close')
}
onMounted(() => window.addEventListener('keydown', onKey))
onUnmounted(() => window.removeEventListener('keydown', onKey))
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal panel char-modal">
      <button class="modal-close" @click="emit('close')">×</button>

      <div class="char-head">
        <img class="char-portrait" :src="base + 'portraits/' + c.portrait" :alt="c.name" />
        <div class="char-id">
          <h2>{{ c.name }}</h2>
          <p v-if="c.aliases.length" class="aliases">{{ c.aliases.join(' · ') }}</p>
        </div>
      </div>

      <p v-if="limitBook" class="as-of">
        Shown as known by the end of <b>Book {{ limitBook.number }}: {{ limitBook.name }}</b>. Rows marked
        <span class="flag">then</span> changed later in the series.
      </p>

      <table class="details">
        <tbody>
          <tr><td>Gender</td><td>{{ c.gender }}</td></tr>
          <tr><td>Nation</td><td>{{ c.nation }}</td></tr>
          <tr v-if="c.origin"><td>Origin</td><td>{{ c.origin }}</td></tr>
          <tr><td>Bending</td><td>{{ bendingText }}</td></tr>
          <tr>
            <td>Skills</td>
            <td>{{ skillsText }}<span v-if="rewound('skills')" class="flag">then</span></td>
          </tr>
          <tr>
            <td>Affiliation</td>
            <td>{{ c.affiliation }}<span v-if="rewound('affiliation')" class="flag">then</span></td>
          </tr>
          <tr><td>Age</td><td>{{ ageText }}</td></tr>
          <tr><td>Hair</td><td>{{ c.hair }}</td></tr>
          <tr v-if="c.eyes"><td>Eyes</td><td>{{ c.eyes }}</td></tr>
          <tr><td>First seen</td><td>{{ debut }}</td></tr>
        </tbody>
      </table>

      <a class="wiki-link" :href="wikiUrl" target="_blank" rel="noreferrer">
        Read more on the Avatar Wiki ↗
      </a>
    </div>
  </div>
</template>

<style scoped>
.char-modal { max-width: 480px; }

.char-head {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 16px;
}
.char-portrait {
  width: 108px;
  height: 108px;
  flex: none;
  object-fit: cover;
  object-position: top;
  border-radius: 10px;
  border: 3px solid var(--tan);
  background: #fff;
}
.char-id { min-width: 0; }
.char-id h2 {
  text-align: left;
  margin: 0 0 4px;
  font-size: 24px;
  line-height: 1.1;
}
.aliases {
  margin: 0;
  font-size: 13px;
  font-style: italic;
  color: var(--brown);
  overflow-wrap: anywhere;
}

.details {
  width: 100%;
  border-collapse: collapse;
  font-size: 15px;
}
.details td {
  border-top: 1px solid var(--tan);
  padding: 7px 8px 7px 0;
  vertical-align: top;
}
.details td:first-child {
  font-weight: 700;
  white-space: nowrap;
  color: var(--brown-dark);
  width: 38%;
}

.as-of {
  margin: 0 0 10px;
  font-size: 12.5px;
  color: var(--brown);
  background: var(--parchment-dark);
  border-radius: 8px;
  padding: 6px 10px;
}
.flag {
  display: inline-block;
  margin-left: 6px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .04em;
  color: #6b4f27;
  background: var(--parchment-dark);
  border: 1px solid var(--tan);
  border-radius: 6px;
  padding: 0 5px;
  vertical-align: 1px;
}

.wiki-link {
  display: inline-block;
  margin-top: 16px;
  font-weight: 700;
  color: var(--brown-dark);
}

@media (max-width: 480px) {
  .char-head { flex-direction: column; text-align: center; gap: 10px; }
  .char-id h2 { text-align: center; }
}
</style>
