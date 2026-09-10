<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  characters: { type: Array, required: true },
  guessed: { type: Set, required: true },
})
const emit = defineEmits(['guess'])

const query = ref('')
const selected = ref(0)
const inputEl = ref(null)
const base = import.meta.env.BASE_URL

function norm(s) {
  return s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
}

const matches = computed(() => {
  const q = norm(query.value.trim())
  if (!q) return []
  const scored = []
  for (const c of props.characters) {
    if (props.guessed.has(c.name)) continue
    const names = [c.name, ...(c.aliases || [])].filter(Boolean)
    let best = -1
    for (const n of names) {
      const nn = norm(n)
      if (nn.startsWith(q)) best = Math.max(best, 2)
      else if (nn.split(/\s+/).some(w => w.startsWith(q))) best = Math.max(best, 1)
      else if (nn.includes(q)) best = Math.max(best, 0)
    }
    if (best >= 0) scored.push([best, c])
  }
  scored.sort((a, b) => b[0] - a[0] || a[1].name.localeCompare(b[1].name))
  return scored.slice(0, 8).map(x => x[1])
})

function pick(c) {
  emit('guess', c)
  query.value = ''
  selected.value = 0
  inputEl.value?.focus()
}

function onKey(e) {
  if (!matches.value.length) return
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    selected.value = (selected.value + 1) % matches.value.length
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    selected.value = (selected.value - 1 + matches.value.length) % matches.value.length
  } else if (e.key === 'Enter') {
    e.preventDefault()
    pick(matches.value[selected.value])
  } else if (e.key === 'Escape') {
    query.value = ''
  }
}
</script>

<template>
  <div class="guess-input">
    <div class="input-row">
      <input
        ref="inputEl" v-model="query" type="text" placeholder="Type character name..."
        autocomplete="off" autocapitalize="off" spellcheck="false"
        @keydown="onKey" @input="selected = 0" />
      <button
        class="submit" title="Submit guess" :disabled="!matches.length"
        @click="matches.length && pick(matches[selected])">➤</button>
    </div>
    <ul v-if="matches.length" class="dropdown panel">
      <li
        v-for="(c, i) in matches" :key="c.name" :class="{ sel: i === selected }"
        @mousedown.prevent="pick(c)" @mousemove="selected = i">
        <img :src="base + 'portraits/' + c.portrait" :alt="c.name" loading="lazy" />
        <span>{{ c.name }}</span>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.guess-input {
  position: relative;
  width: min(440px, 92vw);
}
.input-row {
  display: flex;
  gap: 8px;
  align-items: center;
}
input {
  flex: 1;
  font-family: inherit;
  font-size: 18px;
  padding: 12px 16px;
  border-radius: 10px;
  border: 3px solid var(--tan);
  background: var(--parchment);
  color: var(--ink);
  outline: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}
input::placeholder { color: #a08c66; }

.submit {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: 3px solid #1c1712;
  background: radial-gradient(circle at 35% 30%, #4a3b28, #211a12 70%);
  color: #f2d996;
  font-size: 20px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}
.submit:disabled { opacity: .55; cursor: default; }

.dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 60px;
  margin: 0;
  padding: 4px;
  list-style: none;
  z-index: 20;
  max-height: 330px;
  overflow-y: auto;
}
.dropdown li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 5px 8px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}
.dropdown li.sel { background: var(--parchment-dark); }
.dropdown img {
  width: 34px;
  height: 34px;
  object-fit: cover;
  object-position: top;
  border-radius: 6px;
  border: 1px solid var(--tan);
  background: #fff;
}
</style>
