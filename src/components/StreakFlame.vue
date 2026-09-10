<script setup>
// Three nested tongues on offset cycles read as fire; a single flickering
// shape just reads as a wobbling blob.
defineProps({
  count: { type: Number, default: 0 },
})
</script>

<template>
  <span class="streak" :class="{ lit: count > 0 }" :title="`${count} day streak`">
    <span class="flame">
      <svg viewBox="0 0 32 40">
        <defs>
          <radialGradient id="fOuter" cx="50%" cy="72%" r="62%">
            <stop offset="0%" stop-color="#ffb225" />
            <stop offset="60%" stop-color="#f4741f" />
            <stop offset="100%" stop-color="#d9391d" />
          </radialGradient>
          <radialGradient id="fInner" cx="50%" cy="76%" r="60%">
            <stop offset="0%" stop-color="#fff6c4" />
            <stop offset="70%" stop-color="#ffd23f" />
            <stop offset="100%" stop-color="#ff9c22" />
          </radialGradient>
        </defs>
        <path class="t t-outer" fill="url(#fOuter)"
          d="M16 1c1.6 6.2-2 8.8-5.2 12.2C7.4 16.8 4 20.2 4 25.6A12 12 0 0 0 28 25.6c0-4.6-2-7.4-4.6-10.6-1.5 1.6-3 2.2-4.2 1.6 2.2-4.6 1-11-3.2-15.6z" />
        <path class="t t-mid" fill="url(#fInner)" opacity=".95"
          d="M16 12c1 3.4-1.2 5-3 7-1.9 2-3.6 4-3.6 7a6.9 6.9 0 0 0 13.8 0c0-2.8-1.4-4.6-3-6.4-1 .9-2 1.2-2.8.8 1.4-2.6.8-6-1.4-8.4z" />
        <ellipse class="t t-core" cx="16" cy="29.5" rx="3.1" ry="4.6" fill="#fffbe6" opacity=".9" />
      </svg>
    </span>
    <b>{{ count }}</b>
  </span>
</template>

<style scoped>
.streak {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  padding: 4px 6px;
}
.flame {
  width: 20px;
  height: 25px;
  display: block;
  filter: grayscale(1) opacity(.45);
  transition: filter .3s ease;
}
.streak.lit .flame {
  filter: none;
  animation: rise 2.6s ease-in-out infinite;
}
.streak.lit { filter: drop-shadow(0 0 6px rgba(255, 150, 40, .55)); }
.flame svg { width: 100%; height: 100%; display: block; }

.streak.lit .t { transform-origin: 50% 88%; }
.streak.lit .t-outer { animation: lick 1.15s ease-in-out infinite; }
.streak.lit .t-mid { animation: lick 0.83s ease-in-out infinite reverse; }
.streak.lit .t-core { animation: pulse 0.62s ease-in-out infinite; }

@keyframes lick {
  0%, 100% { transform: scale(1, 1) skewX(0deg); }
  30% { transform: scale(.94, 1.09) skewX(3.5deg); }
  65% { transform: scale(1.06, .95) skewX(-3deg); }
}
@keyframes pulse {
  0%, 100% { transform: scaleY(1); opacity: .9; }
  50% { transform: scaleY(1.24); opacity: 1; }
}
@keyframes rise {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-1.5px); }
}

b { font-size: 15px; }

@media (prefers-reduced-motion: reduce) {
  .streak.lit .flame, .streak.lit .t { animation: none; }
}
</style>
