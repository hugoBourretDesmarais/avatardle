import { ref } from 'vue'

// Character widths in this font run from 0.44 to 0.63 em, so sizing text by
// character count mis-fits badly. Measure the real thing instead.
const FONT = '700 100px "Source Sans 3", "Source Sans Pro", sans-serif'

const cache = new Map()
let ctx = null

export const fontsReady = ref(false)
if (typeof document !== 'undefined' && document.fonts) {
  document.fonts.ready.then(() => {
    cache.clear()
    fontsReady.value = true
  })
}

/**
 * Width of the widest word in `text` (in em) and the word count. Both are
 * unitless so the caller can express the size as a CSS calc() against
 * --tile-size, which stays responsive with no resize listener.
 */
export function fitMetrics(text) {
  const key = String(text ?? '')
  const hit = cache.get(key)
  if (hit) return hit
  if (!ctx) {
    ctx = document.createElement('canvas').getContext('2d')
    ctx.font = FONT
  }
  const words = key.split(/\s+/).filter(Boolean)
  const widest = words.length
    ? Math.max(...words.map(w => ctx.measureText(w).width / 100))
    : 1
  const m = { widest: Math.max(widest, 0.5), lines: Math.max(words.length, 1) }
  cache.set(key, m)
  return m
}
