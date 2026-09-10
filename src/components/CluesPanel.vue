<script setup>
import { computed, ref, watch } from 'vue'
import Icon from './Icon.vue'
import episodes from '../data/episodes.json'
import { BOOK_NAMES, episodeParts } from '../game/compare.js'

const props = defineProps({
  answer: { type: Object, required: true },
  tries: { type: Number, required: true },
  won: { type: Boolean, required: true },
})

const FIRST_AT = 5
const BENDING_AT = 8
const AFF_AT = 10

const showFirst = ref(false)
const showBending = ref(false)
const showAff = ref(false)
watch(() => props.answer, () => {
  showFirst.value = false
  showBending.value = false
  showAff.value = false
})

const firstUnlocked = computed(() => props.won || props.tries >= FIRST_AT)
const bendingUnlocked = computed(() => props.won || props.tries >= BENDING_AT)
const affUnlocked = computed(() => props.won || props.tries >= AFF_AT)
const firstLeft = computed(() => Math.max(0, FIRST_AT - props.tries))
const bendingLeft = computed(() => Math.max(0, BENDING_AT - props.tries))
const affLeft = computed(() => Math.max(0, AFF_AT - props.tries))

const firstText = computed(() => {
  const n = props.answer.firstEpisode
  const p = episodeParts(n)
  if (!p) return 'Unknown episode'
  const ep = episodes.find(e => e.n === n)
  return `Book ${p.book}: ${BOOK_NAMES[p.book]} · Episode ${p.ep} “${ep?.title ?? '?'}”`
})

const bendingText = computed(() => {
  const a = props.answer
  const skills = a.skills?.length ? ` — ${a.skills.join(', ').toLowerCase()}` : ''
  return `${a.bending}${skills}`
})
</script>

<template>
  <div class="clues">
    <div class="clue">
      <button class="clue-btn" :disabled="!firstUnlocked" @click="showFirst = !showFirst">
        <Icon class="clue-ico" name="scroll" :size="30" />
        <span class="clue-label">First Appearance Clue</span>
        <span v-if="!firstUnlocked" class="clue-lock">in {{ firstLeft }} {{ firstLeft === 1 ? 'try' : 'tries' }}</span>
      </button>
      <p v-if="showFirst && firstUnlocked" class="clue-value">{{ firstText }}</p>
    </div>
    <div class="clue">
      <button class="clue-btn" :disabled="!bendingUnlocked" @click="showBending = !showBending">
        <Icon class="clue-ico" name="elements" :size="30" />
        <span class="clue-label">Bending Clue</span>
        <span v-if="!bendingUnlocked" class="clue-lock">in {{ bendingLeft }} {{ bendingLeft === 1 ? 'try' : 'tries' }}</span>
      </button>
      <p v-if="showBending && bendingUnlocked" class="clue-value">{{ bendingText }}</p>
    </div>
    <div class="clue">
      <button class="clue-btn" :disabled="!affUnlocked" @click="showAff = !showAff">
        <Icon class="clue-ico" name="banner" :size="30" />
        <span class="clue-label">Affiliation Clue</span>
        <span v-if="!affUnlocked" class="clue-lock">in {{ affLeft }} {{ affLeft === 1 ? 'try' : 'tries' }}</span>
      </button>
      <p v-if="showAff && affUnlocked" class="clue-value">{{ answer.affiliation || 'Unknown affiliation' }}</p>
    </div>
  </div>
</template>

<style scoped>
.clues {
  display: flex;
  gap: 14px;
  justify-content: center;
  flex-wrap: wrap;
}
.clue {
  flex: 1;
  min-width: 160px;
  max-width: 220px;
}
.clue-btn {
  width: 100%;
  min-height: 108px;
  border: 2px solid var(--tan);
  border-radius: 8px;
  background: var(--parchment);
  color: var(--brown);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px;
}
.clue-btn:not(:disabled):hover {
  background: var(--parchment-dark);
  transform: translateY(-2px);
  box-shadow: 0 6px 14px rgba(0, 0, 0, .18);
}
.clue-value { animation: clue-in .25s ease both; }
@keyframes clue-in {
  from { transform: translateY(-4px); opacity: 0; }
  to { transform: none; opacity: 1; }
}
.clue-btn:disabled { opacity: .6; cursor: default; }
.clue-ico { color: var(--brown); }
.clue-label {
  font-weight: 700;
  text-transform: uppercase;
  font-size: 13px;
  letter-spacing: .5px;
}
.clue-lock { font-size: 12px; font-style: italic; }
.clue-value {
  margin: 8px 0 0;
  font-weight: 700;
  color: var(--brown-dark);
}
</style>
