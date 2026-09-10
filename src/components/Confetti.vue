<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  duration: { type: Number, default: 2600 },
  count: { type: Number, default: 140 },
})

const canvas = ref(null)
let raf = null
let stopped = false

const COLORS = ['#479f4b', '#d9a51f', '#b23c39', '#3f6fd2', '#f6eed7', '#c9a86a']

onMounted(() => {
  const reduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  if (reduced) return

  const el = canvas.value
  const ctx = el.getContext('2d')
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  const w = window.innerWidth || document.documentElement.clientWidth
  const h = window.innerHeight || document.documentElement.clientHeight
  // A hidden or collapsed viewport reports 0; drawing into a zero-size canvas
  // throws on read-back and shows nothing, so just skip it.
  if (!w || !h) return
  el.width = w * dpr
  el.height = h * dpr
  el.style.width = `${w}px`
  el.style.height = `${h}px`
  ctx.scale(dpr, dpr)

  // Launched from two lower corners so the burst crosses the middle of the
  // screen, where the win panel appears.
  const parts = Array.from({ length: props.count }, (_, i) => {
    const fromLeft = i % 2 === 0
    const angle = (fromLeft ? -60 : -120) + (Math.random() - 0.5) * 55
    const speed = 12 + Math.random() * 14
    return {
      x: fromLeft ? 0 : w,
      y: h * 0.85,
      vx: Math.cos((angle * Math.PI) / 180) * speed,
      vy: Math.sin((angle * Math.PI) / 180) * speed,
      size: 5 + Math.random() * 7,
      color: COLORS[(Math.random() * COLORS.length) | 0],
      spin: (Math.random() - 0.5) * 0.35,
      rot: Math.random() * Math.PI,
    }
  })

  const start = performance.now()
  function frame(now) {
    if (stopped) return
    const elapsed = now - start
    const fade = Math.max(0, 1 - Math.max(0, elapsed - props.duration * 0.55) / (props.duration * 0.45))
    ctx.clearRect(0, 0, w, h)
    for (const p of parts) {
      p.vy += 0.42          // gravity
      p.vx *= 0.995         // drag
      p.x += p.vx
      p.y += p.vy
      p.rot += p.spin
      if (p.y > h + 40) continue
      ctx.save()
      ctx.globalAlpha = fade
      ctx.translate(p.x, p.y)
      ctx.rotate(p.rot)
      ctx.fillStyle = p.color
      ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6)
      ctx.restore()
    }
    if (elapsed < props.duration) raf = requestAnimationFrame(frame)
    else ctx.clearRect(0, 0, w, h)
  }
  raf = requestAnimationFrame(frame)
})

onUnmounted(() => {
  stopped = true
  if (raf) cancelAnimationFrame(raf)
})
</script>

<template>
  <canvas ref="canvas" class="confetti" aria-hidden="true"></canvas>
</template>

<style scoped>
.confetti {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 60;
}
</style>
