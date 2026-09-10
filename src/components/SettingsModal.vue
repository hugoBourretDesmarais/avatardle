<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  books: { type: Array, required: true },
  characters: { type: Array, required: true },
  bookLimit: { type: String, default: null },
})
const emit = defineEmits(['close', 'update:bookLimit'])

const pending = ref(props.bookLimit ?? '')

// The last book is the whole series, so it isn't offered as a limit.
const choices = computed(() => props.books.slice(0, -1))

function countUpTo(bookName) {
  if (!bookName) return props.characters.length
  const book = props.books.find(b => b.name === bookName)
  if (!book) return props.characters.length
  return props.characters.filter(c => c.firstEpisode <= book.endEpisode).length
}

const pendingCount = computed(() => countUpTo(pending.value || null))
const changed = computed(() => (pending.value || null) !== (props.bookLimit ?? null))

function apply() {
  emit('update:bookLimit', pending.value || null)
  emit('close')
}
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal panel">
      <button class="modal-close" @click="emit('close')">×</button>
      <h2>Settings</h2>

      <h3>Spoiler limit</h3>
      <p>
        How far are you in the series? Only characters who have already appeared by the end of that
        book can show up — as the answer, in the guess suggestions, or in the gallery.
      </p>

      <label class="arc-field">
        I've watched up to and including
        <select v-model="pending">
          <option value="">Everything (all three books)</option>
          <option v-for="b in choices" :key="b.name" :value="b.name">Book {{ b.number }}: {{ b.name }}</option>
        </select>
      </label>

      <p class="pool">
        <b>{{ pendingCount }}</b> of {{ characters.length }} characters would be in play.
      </p>

      <div class="warn">
        Cards rewind with the limit: affiliation and skills show what was known by the end of that
        book rather than the character's final state. With a Book 1 limit, Zuko is still hunting the
        Avatar and Katara has not learned bloodbending.
      </div>

      <p class="note">
        Players using the same limit share the same daily character. Changing this starts today's
        character over.
      </p>

      <button class="apply" :disabled="!changed" @click="apply">
        {{ changed ? 'Apply' : 'No changes' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
p { font-size: 15px; }
h3 {
  font-family: 'Lilita One', cursive;
  color: var(--brown-dark);
  margin-bottom: 4px;
}
.arc-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-weight: 700;
  color: var(--brown-dark);
  font-size: 14px;
  margin: 14px 0 8px;
}
.arc-field select {
  font-family: inherit;
  font-size: 16px;
  padding: 9px 10px;
  border-radius: 8px;
  border: 2px solid var(--tan);
  background: #fffdf5;
  color: var(--ink);
  font-weight: 600;
}
.pool { margin: 6px 0 14px; color: var(--brown); }
.warn {
  border-left: 4px solid var(--yellow);
  background: var(--parchment-dark);
  border-radius: 6px;
  padding: 10px 12px;
  font-size: 14px;
  line-height: 1.4;
}
.note { font-style: italic; color: var(--brown); font-size: 14px; }
.apply {
  width: 100%;
  border: 2px solid var(--tan);
  background: var(--parchment-dark);
  color: var(--brown-dark);
  font-weight: 700;
  font-size: 16px;
  border-radius: 8px;
  padding: 11px;
  margin-top: 4px;
}
.apply:disabled { opacity: .55; cursor: default; }
.apply:not(:disabled):hover { filter: brightness(.96); }
</style>
