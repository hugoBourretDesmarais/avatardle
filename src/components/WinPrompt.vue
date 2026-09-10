<script setup>
import AccountForm from './AccountForm.vue'

defineProps({
  answer: { type: String, required: true },
  tries: { type: Number, required: true },
  pendingWin: { type: Object, default: null },
})
const emit = defineEmits(['close', 'account'])
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal panel prompt">
      <button class="modal-close" @click="emit('close')">×</button>
      <h2>Keep this win 🏆</h2>
      <p class="line">
        You found <b>{{ answer }}</b> in <b>{{ tries }}</b> {{ tries === 1 ? 'try' : 'tries' }}.
        Create an account and it goes on the leaderboard — this one included.
      </p>
      <AccountForm :pending-win="pendingWin" @account="emit('account', $event)" />
      <button class="later" @click="emit('close')">Not now</button>
    </div>
  </div>
</template>

<style scoped>
.prompt { max-width: 420px; }
h2 { margin-bottom: 10px; }
.line {
  margin: 0 0 12px;
  font-size: 14px;
  color: var(--brown-dark);
  line-height: 1.45;
}
.later {
  margin-top: 12px;
  width: 100%;
  font-family: inherit;
  font-weight: 700;
  font-size: 13px;
  padding: 9px;
  border-radius: 8px;
  border: 2px solid var(--tan);
  background: var(--parchment);
  color: var(--brown);
}
</style>
