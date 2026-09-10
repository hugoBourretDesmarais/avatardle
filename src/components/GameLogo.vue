<script setup>
import { onMounted, ref, watch } from 'vue'
import { fontsReady } from '../game/textfit.js'
// Drawn as SVG rather than styled HTML: the wordmark needs three stacked
// strokes, a per-letter gradient, a gloss sweep and a grain wash, which
// text-shadow stacking can't express cleanly.
const WORD = 'AVATARDLE'
const LETTERS = [...WORD]
const base = import.meta.env.BASE_URL

// Lilita One at 118px has an 83-unit cap height and a 6-unit left bearing;
// the seal is scaled to that height and the text starts just past its ring.
const TX = 134
// Room for the word to the right of the seal. Browsers disagree on how wide
// Lilita One renders (and Safari mangles textLength), so the size is measured
// once the font is in and scaled down to fit rather than pinned.
const MAX_W = 612
const BASE_SIZE = 118
const probe = ref(null)
const size = ref(BASE_SIZE)
// Splitting the word into one tspan per letter loses the kerning the stroked
// copies keep, so each fill letter is pinned to where the unsplit run puts it.
const xs = ref(null)

function fit() {
  const el = probe.value
  const w = el?.getComputedTextLength?.()
  if (!w) return
  size.value = Math.min(BASE_SIZE, Math.floor(BASE_SIZE * MAX_W / w * 100) / 100)
  const k = size.value / BASE_SIZE
  const x0 = el.getStartPositionOfChar(0).x
  xs.value = LETTERS.map((_, i) => TX + (el.getStartPositionOfChar(i).x - x0) * k)
}
onMounted(() => {
  fit()
  document.fonts?.ready.then(fit)
})
watch(fontsReady, fit)

// Water, earth, fire, air in the order the Avatar learns them.
const CYCLE = ['url(#gWater)', 'url(#gEarth)', 'url(#gFire)', 'url(#gAir)']
const fillFor = i => CYCLE[i % CYCLE.length]
</script>

<template>
  <h1 class="logo" aria-label="AvatarDle">
    <svg class="word" viewBox="0 0 784 150" aria-hidden="true" :style="{ '--t-size': size + 'px' }">
      <text ref="probe" class="probe" x="0" y="-500">{{ WORD }}</text>
      <defs>
        <radialGradient id="markDisc" cx="38%" cy="30%" r="78%">
          <stop offset="0%" stop-color="#4a4a52" />
          <stop offset="55%" stop-color="#1d1d24" />
          <stop offset="100%" stop-color="#0b0b10" />
        </radialGradient>
        <linearGradient id="ringG" x1="0" y1="0" x2="0.4" y2="1">
          <stop offset="0%" stop-color="#fffdf4" />
          <stop offset="100%" stop-color="#d9c69a" />
        </linearGradient>
        <linearGradient id="gWater" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#7cc4f2" />
          <stop offset="38%" stop-color="#2f7fc4" />
          <stop offset="78%" stop-color="#1b4f8f" />
          <stop offset="100%" stop-color="#0f2a55" />
        </linearGradient>
        <linearGradient id="gEarth" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#b6d77a" />
          <stop offset="38%" stop-color="#5f8f3a" />
          <stop offset="78%" stop-color="#3b6124" />
          <stop offset="100%" stop-color="#1f3a12" />
        </linearGradient>
        <linearGradient id="gFire" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#ff9a5c" />
          <stop offset="38%" stop-color="#d8442f" />
          <stop offset="78%" stop-color="#9e1f22" />
          <stop offset="100%" stop-color="#5c0d18" />
        </linearGradient>
        <linearGradient id="gAir" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#ffe6a0" />
          <stop offset="38%" stop-color="#e3a83b" />
          <stop offset="78%" stop-color="#b6761c" />
          <stop offset="100%" stop-color="#6e4310" />
        </linearGradient>
        <radialGradient id="sealSheen" cx="35%" cy="28%" r="80%">
          <stop offset="0%" stop-color="#fff" stop-opacity=".28" />
          <stop offset="60%" stop-color="#fff" stop-opacity="0" />
        </radialGradient>

        <!-- generated wear map, tiled across the wordmark -->
        <pattern id="wear" patternUnits="userSpaceOnUse" width="260" height="260">
          <image :href="base + 'textures/wear.png'" width="260" height="260"
            preserveAspectRatio="xMidYMid slice" />
        </pattern>

        <linearGradient id="depth" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#2a0d16" stop-opacity="0" />
          <stop offset="66%" stop-color="#2a0d16" stop-opacity="0" />
          <stop offset="100%" stop-color="#2a0d16" stop-opacity=".42" />
        </linearGradient>
        <linearGradient id="topLight" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#fff" stop-opacity=".55" />
          <stop offset="16%" stop-color="#fff" stop-opacity=".10" />
          <stop offset="26%" stop-color="#fff" stop-opacity="0" />
        </linearGradient>

        <filter id="cast" x="-15%" y="-30%" width="130%" height="170%">
          <feDropShadow dx="0" dy="7" stdDeviation="5" flood-color="#000" flood-opacity=".5" />
          <feDropShadow dx="0" dy="2" stdDeviation="1" flood-color="#000" flood-opacity=".4" />
        </filter>

        <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stop-color="#fff" stop-opacity="0" />
          <stop offset=".42" stop-color="#fff" stop-opacity=".35" />
          <stop offset=".5" stop-color="#fff" stop-opacity=".9" />
          <stop offset=".58" stop-color="#fff" stop-opacity=".35" />
          <stop offset="1" stop-color="#fff" stop-opacity="0" />
        </linearGradient>

        <mask id="wordMask">
          <text class="t" :x="TX" y="112" fill="#fff">{{ WORD }}</text>
        </mask>
        <mask id="shineMask">
          <circle cx="70" cy="70.6" r="48" fill="#fff" />
          <text class="t" :x="TX" y="112" fill="#fff">{{ WORD }}</text>
        </mask>
      </defs>

      <!-- the seal: positioned by the outer group so the CSS animation on the
           inner one doesn't override the placement transform -->
      <g transform="translate(13.75 14.35) scale(1.125)" filter="url(#cast)">
        <g class="mark">
          <circle cx="50" cy="50" r="50" fill="#101828" />
          <circle cx="50" cy="50" r="48" fill="url(#ringG)" />
          <circle cx="50" cy="50" r="43" fill="url(#markDisc)" />

          <!-- four nations, clockwise from the top: fire, earth, water, air -->
          <path d="M50 10a40 40 0 0 1 40 40H50z" fill="url(#gFire)" />
          <path d="M90 50a40 40 0 0 1-40 40V50z" fill="url(#gEarth)" />
          <path d="M50 90A40 40 0 0 1 10 50h40z" fill="url(#gWater)" />
          <path d="M10 50A40 40 0 0 1 50 10v40z" fill="url(#gAir)" />
          <path d="M50 10v80M10 50h80" stroke="#101828" stroke-width="2.4" opacity=".7" />

          <!-- element glyphs, one per quadrant -->
          <g fill="none" stroke="#fdfaf0" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" opacity=".92">
            <!-- fire -->
            <path d="M70 22c1 4-1.4 5.6-3 7.4-1.8 2-3.6 3.8-3.6 7a6.6 6.6 0 0 0 13.2 0c0-3.8-2.2-5.6-3.6-7.4-.9-1.2-1.4-2.4-1-4.4" />
            <!-- earth -->
            <path d="M62 66h16M64 72h12M66 78h8" />
            <!-- water -->
            <path d="M22 64c3-3 6-3 9 0s6 3 9 0M22 72c3-3 6-3 9 0s6 3 9 0" />
            <!-- air -->
            <path d="M30 40c-4 0-6.8-2.6-6.8-6 0-3 2.4-5.2 5.4-5.2 2.6 0 4.4 1.8 4.4 4.1 0 1.9-1.4 3.3-3.2 3.3-1.4 0-2.4-1-2.4-2.3" />
          </g>

          <circle cx="50" cy="50" r="43" fill="url(#sealSheen)" />
          <circle cx="50" cy="50" r="40" fill="none" stroke="#101828" stroke-width="1.5" opacity=".5" />
        </g>
      </g>

      <g class="letters">
        <g filter="url(#cast)">
          <text class="t" :x="TX" y="112"
            fill="none" stroke="#101828" stroke-width="23" stroke-linejoin="round">{{ WORD }}</text>
          <text class="t" :x="TX" y="112"
            fill="none" stroke="#fdf3dc" stroke-width="13" stroke-linejoin="round">{{ WORD }}</text>
          <text class="t" :x="TX" y="112">
            <tspan v-for="(ch, i) in LETTERS" :key="i" :x="xs?.[i]" :fill="fillFor(i)">{{ ch }}</tspan>
          </text>
        </g>

        <g mask="url(#wordMask)">
          <!-- straight alpha, no blend modes: the group is isolated, so overlay
               and soft-light would blend against nothing and grey the letters -->
          <g class="grain">
            <rect x="-260" y="-260" width="1304" height="670" fill="url(#wear)" opacity=".55" />
          </g>
          <!-- thickness: shadow pooling toward the base of each glyph -->
          <rect width="784" height="150" fill="url(#depth)" />
          <!-- a narrow lit edge along the top, not a full plastic gloss -->
          <rect width="784" height="150" fill="url(#topLight)" />
        </g>
      </g>

      <g mask="url(#shineMask)">
        <g class="shine">
          <rect x="-90" y="-40" width="180" height="230" fill="url(#shine)" transform="skewX(-20)" />
        </g>
      </g>
    </svg>

    <span class="sr">AvatarDle</span>
  </h1>
</template>

<style scoped>
.logo {
  position: relative;
  margin: 4px 0 0;
  width: min(600px, calc(100% - 14px));
  max-width: 100%;
  user-select: none;
}

.word {
  display: block;
  width: 100%;
  height: auto;
  overflow: visible;
}

.mark, .letters {
  transform-box: fill-box;
  transform-origin: center;
}
.mark {
  animation: mark-in .6s cubic-bezier(.2, .9, .3, 1.5) both, sway 6s ease-in-out 1.1s infinite;
}
.letters {
  animation: word-in .55s cubic-bezier(.2, .85, .3, 1.35) both .1s, float 6s ease-in-out 1.1s infinite;
}
.grain {
  animation: drift 32s linear infinite;
}
.shine {
  animation: sweep 7s ease-in 1.8s infinite;
}
.probe {
  font-family: 'Lilita One', cursive;
  font-size: 118px;
  letter-spacing: 1px;
  visibility: hidden;
}
.t {
  font-family: 'Lilita One', cursive;
  font-size: var(--t-size, 118px);
  letter-spacing: 1px;
  paint-order: stroke fill;
}

.sr {
  position: absolute;
  width: 1px; height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
}

@keyframes mark-in {
  from { transform: scale(.35) rotate(-45deg); opacity: 0; }
  to { transform: none; opacity: 1; }
}
@keyframes word-in {
  from { transform: translateY(-14px) scale(.94); opacity: 0; }
  to { transform: none; opacity: 1; }
}
@keyframes sway {
  0%, 100% { transform: rotate(-3deg); }
  50% { transform: rotate(3deg); }
}
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
/* one pattern tile per loop in each axis, so the wrap is seamless */
@keyframes drift {
  from { transform: translate(0, 0); }
  to { transform: translate(260px, 260px); }
}
@keyframes sweep {
  0% { transform: translateX(-160px); }
  22%, 100% { transform: translateX(900px); }
}

@media (prefers-reduced-motion: reduce) {
  .mark, .letters, .grain { animation: none; }
  .shine { display: none; }
}
</style>
