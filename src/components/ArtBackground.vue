<script setup>
import { computed, onMounted, ref } from 'vue'
import backgrounds from '../data/backgrounds.json'

const props = defineProps({
  // caller ties this to the date so the artwork changes daily
  seed: { type: Number, default: 0 },
})

const base = import.meta.env.BASE_URL
const loaded = ref(false)

const art = computed(() => {
  const i = ((props.seed % backgrounds.length) + backgrounds.length) % backgrounds.length
  return backgrounds[i]
})

// Alternating pan direction stops consecutive days feeling identical.
const drift = computed(() => (props.seed % 2 === 0 ? 'pan-a' : 'pan-b'))

// image-set() picks WebP where supported and falls back to JPEG, so we keep the
// format negotiation without needing a <picture> element.
const layer = computed(() => {
  const webp = `${base}backgrounds/${art.value.slug}.webp`
  const jpg = `${base}backgrounds/${art.value.slug}.jpg`
  return `image-set(url("${webp}") type("image/webp"), url("${jpg}") type("image/jpeg"))`
})

onMounted(() => {
  // Fade in only once the bitmap is actually decoded.
  const probe = new Image()
  probe.onload = probe.onerror = () => (loaded.value = true)
  probe.src = `${base}backgrounds/${art.value.slug}.jpg`
})
</script>

<template>
  <div class="art-bg" aria-hidden="true">
    <div
      class="art" :class="[drift, { in: loaded }]"
      :style="{ backgroundImage: layer }"></div>
    <div class="tint"></div>
    <div class="vignette"></div>
    <span class="credit">{{ art.label }}</span>
  </div>
</template>

<style scoped>
.art-bg {
  position: fixed;
  inset: 0;
  /* Behind everything in #app's stacking context. At z-index 0 it painted over
     every non-positioned sibling — the column headers, the yesterday line and
     the footer all disappeared under the artwork. */
  z-index: -1;
  overflow: hidden;
  background: #10243d;
}

/* Panned via background-position rather than a transform: a transformed layer
   can sit un-rasterised in a throttled tab, and this always paints. */
.art {
  position: absolute;
  inset: 0;
  background-repeat: no-repeat;
  /* cover guarantees the viewport is filled at any aspect ratio; the pan then
     moves within whatever slack that leaves. */
  background-size: cover;
  background-position: 50% 42%;
  opacity: 0;
  transition: opacity 1s ease;
}
.art.in { opacity: 1; }
.art.pan-a { animation: pan-a 70s ease-in-out infinite alternate; }
.art.pan-b { animation: pan-b 78s ease-in-out infinite alternate; }

@keyframes pan-a {
  from { background-position: 38% 34%; }
  to   { background-position: 62% 54%; }
}
@keyframes pan-b {
  from { background-position: 62% 52%; }
  to   { background-position: 38% 32%; }
}

/* Artwork this busy would swallow the UI, so knock it back and darken the
   column the panels sit in. */
.tint {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(180deg, rgba(8, 16, 36, .52) 0%, rgba(8, 16, 36, .26) 34%, rgba(8, 16, 36, .40) 100%),
    linear-gradient(90deg, transparent 0%, rgba(6, 12, 30, .30) 26%, rgba(6, 12, 30, .30) 74%, transparent 100%);
}
.vignette {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 50% 45%, transparent 46%, rgba(0, 0, 0, .40) 100%);
}

.credit {
  position: absolute;
  right: 10px;
  bottom: 8px;
  font-size: 10px;
  letter-spacing: .5px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, .38);
  text-shadow: 0 1px 2px rgba(0, 0, 0, .6);
  pointer-events: none;
}

@media (prefers-reduced-motion: reduce) {
  .art { animation: none; transition: none; opacity: 1; }
}
</style>
