<script setup>
import { computed, ref } from 'vue'
import { MIN_PASSWORD, loginPlayer, registerPlayer, submitResult } from '../game/api.js'

const props = defineProps({
  // Today's daily win, if it was solved before this account existed.
  pendingWin: { type: Object, default: null },
})
const emit = defineEmits(['account'])

const mode = ref('join') // 'join' | 'restore'
const nameInput = ref('')
const passwordInput = ref('')
const busy = ref(false)
const error = ref('')

const canSubmit = computed(
  () => nameInput.value.trim().length >= 2 && passwordInput.value.length >= MIN_PASSWORD)

async function submit() {
  error.value = ''
  busy.value = true
  const fn = mode.value === 'join' ? registerPlayer : loginPlayer
  const r = await fn(nameInput.value, passwordInput.value)
  busy.value = false
  if (r?.error) {
    error.value = r.error
    return
  }
  passwordInput.value = ''
  const account = { id: r.id, name: r.name, token: r.token }
  // The win has to land before anyone reacts to the new account, or a board
  // rendered on the way out shows the player with nothing on it.
  if (props.pendingWin) {
    const w = props.pendingWin
    await submitResult(account, w.day, w.arcLimit, w.guesses, w.name)
  }
  emit('account', account)
}
</script>

<template>
  <div class="join">
    <div class="tabs">
      <button :class="{ on: mode === 'join' }" @click="mode = 'join'; error = ''">Create account</button>
      <button :class="{ on: mode === 'restore' }" @click="mode = 'restore'; error = ''">Sign in</button>
    </div>
    <p class="join-note">
      A pseudonym and a password — no email needed. Sign in with the same two on any device
      and your record follows you.
    </p>
    <form @submit.prevent="canSubmit && submit()">
      <input
        v-model="nameInput" placeholder="Pseudonym" maxlength="20"
        autocomplete="username" autocapitalize="off" />
      <input
        v-model="passwordInput" type="password" :placeholder="`Password (${MIN_PASSWORD}+ characters)`"
        :autocomplete="mode === 'join' ? 'new-password' : 'current-password'" />
      <p v-if="error" class="error">{{ error }}</p>
      <button class="primary" type="submit" :disabled="busy || !canSubmit">
        {{ busy ? 'Working…' : mode === 'join' ? 'Create account' : 'Sign in' }}
      </button>
    </form>
    <p v-if="mode === 'join'" class="warn">
      There is no password reset yet — if you forget it the account can't be recovered.
      Please don't reuse an important password.
    </p>
  </div>
</template>

<style scoped>
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

.join { display: flex; flex-direction: column; gap: 8px; }
.join-note { margin: 0; font-size: 13px; color: var(--brown); }
.join input {
  font-family: inherit;
  font-size: 16px;
  padding: 10px 12px;
  border-radius: 8px;
  border: 2px solid var(--tan);
  background: #fffdf5;
  color: var(--ink);
  outline: none;
}
.join form { display: flex; flex-direction: column; gap: 8px; }
.primary {
  font-family: inherit;
  font-weight: 700;
  font-size: 15px;
  padding: 11px;
  border-radius: 8px;
  border: 2px solid var(--brown);
  background: var(--parchment-dark);
  color: var(--brown-dark);
}
.primary:disabled { opacity: .55; cursor: default; }
.error { margin: 0; color: var(--red); font-size: 13px; font-weight: 700; }
.warn {
  margin: 0;
  font-size: 12px;
  color: var(--brown);
  font-style: italic;
  line-height: 1.4;
}
</style>
