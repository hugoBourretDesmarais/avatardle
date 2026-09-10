<script setup>
import { SKILL_ICONS } from '../game/compare.js'
import { fitMetrics, fontsReady } from '../game/textfit.js'

const props = defineProps({
  guess: { type: Object, required: true },
  base: { type: String, required: true },
})
const emit = defineEmits(['revealed'])

const order = ['portrait', 'gender', 'nation', 'bending', 'skills', 'affiliation', 'age', 'hair', 'firstEpisode']

function cellClass(key) {
  const c = props.guess.cells[key]
  return [c.result, { animate: props.guess.animate }]
}

// Size each label so its longest word fits the tile on one line, and so the
// stacked words still fit the tile's height.
function fitStyle(text) {
  void fontsReady.value // re-evaluate once the webfont's real metrics land
  const { widest, lines } = fitMetrics(text)
  return {
    '--fit-w': widest.toFixed(3),
    '--fit-l': (lines * 1.15).toFixed(3),
  }
}
</script>

<template>
  <div class="row">
    <div
      v-for="(key, i) in order" :key="key"
      class="tile" :class="cellClass(key)" :style="{ '--d': i * 0.28 + 's' }"
      @animationend="i === order.length - 1 && emit('revealed')">
      <template v-if="key === 'portrait'">
        <img
          class="portrait" :src="base + 'portraits/' + guess.char.portrait"
          :alt="guess.char.name" :title="guess.char.name" />
      </template>
      <template v-else-if="key === 'skills'">
        <span v-if="!guess.cells.skills.skills.length" class="txt lg">✖</span>
        <span v-else class="skill-icons" :class="{ many: guess.cells.skills.skills.length > 2 }">
          <span v-for="s in guess.cells.skills.skills" :key="s" :title="s">{{ SKILL_ICONS[s] }}</span>
        </span>
      </template>
      <template v-else>
        <span v-if="guess.cells[key].arrow === 'up'" class="arrow" aria-hidden="true">▲</span>
        <span v-if="guess.cells[key].arrow === 'down'" class="arrow" aria-hidden="true">▼</span>
        <span class="txt" :style="fitStyle(guess.cells[key].text)">{{ guess.cells[key].text }}</span>
      </template>
    </div>
  </div>
</template>

<style scoped>
.row {
  display: flex;
  gap: var(--tile-gap);
}

.tile {
  position: relative;
  width: var(--tile-size);
  height: var(--tile-size);
  border-radius: 8px;
  border: var(--tile-border) solid rgba(0, 0, 0, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #fff;
  font-weight: 700;
  overflow: hidden;
  padding: var(--tile-pad);
}
.tile.exact { background: var(--green); }
.tile.partial { background: var(--yellow); }
.tile.wrong { background: var(--red); }
.tile.neutral { background: #2f2a22; padding: 0; }

.tile.animate {
  animation: flip .5s ease both;
  animation-delay: var(--d);
}
@keyframes flip {
  0% { transform: rotateY(90deg); opacity: .2; }
  100% { transform: rotateY(0); opacity: 1; }
}

@media (prefers-reduced-motion: reduce) {
  .tile.animate { animation: none; }
}

.portrait {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top;
}

.txt {
  position: relative;
  z-index: 1;
  line-height: 1.1;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.45);
  /* break-word only splits a word that cannot fit on a line of its own */
  overflow-wrap: break-word;
  font-size: max(6px, min(
    calc(var(--tile-size) * 0.26),
    calc((var(--tile-size) - var(--tile-inset)) / var(--fit-w, 3)),
    calc((var(--tile-size) - var(--tile-inset)) / var(--fit-l, 1.15))
  ));
}
.txt.lg { font-size: calc(var(--tile-size) * 0.34); }

.arrow {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: calc(var(--tile-size) * 0.92);
  line-height: 1;
  color: rgba(0, 0, 0, 0.34);
  z-index: 0;
}

.skill-icons {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1px;
  font-size: clamp(11px, calc(var(--tile-size) * 0.26), 20px);
  z-index: 1;
}
.skill-icons.many { font-size: clamp(9px, calc(var(--tile-size) * 0.2), 16px); }
</style>
