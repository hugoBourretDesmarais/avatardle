<script setup>
// Emoji render differently on every platform and can't be styled; these are
// drawn so the toolbar and mode wheel look the same everywhere.
defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 24 },
})
</script>

<template>
  <svg
    class="icon" :width="size" :height="size" viewBox="0 0 24 24"
    fill="none" stroke="currentColor" stroke-width="1.7"
    stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">

    <!-- Skull (legacy, unused) -->
    <g v-if="name === 'skull'">
      <path d="M12 3c-3.9 0-6.6 2.6-6.6 6.1 0 2 .8 3.2 1.7 4 .5.5.8 1 .8 1.7v1c0 .7.6 1.2 1.3 1.2h5.6c.7 0 1.3-.5 1.3-1.2v-1c0-.7.3-1.2.8-1.7.9-.8 1.7-2 1.7-4C18.6 5.6 15.9 3 12 3z" fill="currentColor" stroke="none" opacity=".18" />
      <path d="M12 3c-3.9 0-6.6 2.6-6.6 6.1 0 2 .8 3.2 1.7 4 .5.5.8 1 .8 1.7v1c0 .7.6 1.2 1.3 1.2h5.6c.7 0 1.3-.5 1.3-1.2v-1c0-.7.3-1.2.8-1.7.9-.8 1.7-2 1.7-4C18.6 5.6 15.9 3 12 3z" />
      <circle cx="9.4" cy="10" r="1.6" fill="currentColor" stroke="none" />
      <circle cx="14.6" cy="10" r="1.6" fill="currentColor" stroke="none" />
      <path d="M11 13.6h2" />
      <path d="M4.6 19.4l14.8-2.2M4.6 17.2l14.8 2.2" />
    </g>

    <!-- Die: practice -->
    <g v-else-if="name === 'dice'">
      <rect x="3.6" y="3.6" width="16.8" height="16.8" rx="4" />
      <circle cx="8.6" cy="8.6" r="1.35" fill="currentColor" stroke="none" />
      <circle cx="15.4" cy="8.6" r="1.35" fill="currentColor" stroke="none" />
      <circle cx="12" cy="12" r="1.35" fill="currentColor" stroke="none" />
      <circle cx="8.6" cy="15.4" r="1.35" fill="currentColor" stroke="none" />
      <circle cx="15.4" cy="15.4" r="1.35" fill="currentColor" stroke="none" />
    </g>

    <!-- Open log book: gallery -->
    <g v-else-if="name === 'book'">
      <path d="M12 6.4C10.4 5 8.4 4.4 4.8 4.4v13c3.6 0 5.6.6 7.2 2 1.6-1.4 3.6-2 7.2-2v-13c-3.6 0-5.6.6-7.2 2z" />
      <path d="M12 6.4v13" />
    </g>

    <!-- Bar chart: stats -->
    <g v-else-if="name === 'chart'">
      <path d="M4.5 20h15" />
      <rect x="6" y="12" width="3.4" height="6" rx="1" fill="currentColor" stroke="none" opacity=".55" />
      <rect x="10.3" y="7.5" width="3.4" height="10.5" rx="1" fill="currentColor" stroke="none" />
      <rect x="14.6" y="10" width="3.4" height="8" rx="1" fill="currentColor" stroke="none" opacity=".75" />
    </g>

    <!-- Flame: streak -->
    <g v-else-if="name === 'flame'">
      <path d="M13 2.4c.5 2.6-.7 4-2 5.2-1.4 1.3-3.1 2.6-3.1 5.5A6.1 6.1 0 0 0 14 18.9a6 6 0 0 0 3.6-5.5c0-3.4-2-5-3.2-6.4a6.6 6.6 0 0 1-1.4-4.6z" fill="currentColor" stroke="none" opacity=".2" />
      <path d="M13 2.4c.5 2.6-.7 4-2 5.2-1.4 1.3-3.1 2.6-3.1 5.5a6.1 6.1 0 0 0 12.1 0c0-3.4-2-5-3.2-6.4a6.6 6.6 0 0 1-1.4-4.6z" transform="translate(-1.9)" />
      <path d="M12 21.6c1.8 0 3.1-1.3 3.1-2.9 0-2-1.7-2.9-3.1-4.8-1.4 1.9-3.1 2.8-3.1 4.8 0 1.6 1.3 2.9 3.1 2.9z" fill="currentColor" stroke="none" />
    </g>

    <!-- Ship's wheel: settings -->
    <g v-else-if="name === 'wheel'">
      <circle cx="12" cy="12" r="3.2" />
      <circle cx="12" cy="12" r="7.4" />
      <path d="M12 1.8v3M12 19.2v3M1.8 12h3M19.2 12h3M4.8 4.8l2.1 2.1M17.1 17.1l2.1 2.1M19.2 4.8l-2.1 2.1M6.9 17.1l-2.1 2.1" />
    </g>

    <!-- Trophy: leaderboard -->
    <g v-else-if="name === 'trophy'">
      <path d="M7.4 4.2h9.2v4.4a4.6 4.6 0 0 1-9.2 0z" fill="currentColor" stroke="none" opacity=".2" />
      <path d="M7.4 4.2h9.2v4.4a4.6 4.6 0 0 1-9.2 0z" />
      <path d="M7.4 5.6H5.2a2.4 2.4 0 0 0 2.4 3.6M16.6 5.6h2.2a2.4 2.4 0 0 1-2.4 3.6" />
      <path d="M12 13.2v3.4M8.8 20.2h6.4M10 16.6h4l.8 3.6H9.2z" />
    </g>

    <!-- Question mark: help -->
    <g v-else-if="name === 'help'">
      <circle cx="12" cy="12" r="8.6" />
      <path d="M9.6 9.4a2.5 2.5 0 0 1 4.9.6c0 1.7-2.5 2-2.5 3.6" />
      <circle cx="12" cy="17.2" r="1.05" fill="currentColor" stroke="none" />
    </g>

    <!-- Scroll: first-appearance clue -->
    <g v-else-if="name === 'scroll'">
      <path d="M6 4.5h9.5a2 2 0 0 1 2 2v11a2 2 0 0 0 2 2H8.5a2 2 0 0 1-2-2V6.5" />
      <path d="M6 4.5a1.8 1.8 0 0 0 0 3.6h2.5" />
      <path d="M10 9.6h5M10 12.6h5M10 15.6h3" />
    </g>

    <!-- Four elements: bending clue -->
    <g v-else-if="name === 'elements'">
      <circle cx="12" cy="12" r="8.8" />
      <path d="M12 3.2v17.6M3.2 12h17.6" opacity=".5" />
      <path d="M7.6 9.2c.8-1 2-1 2.8 0 .8 1 .8 2-.2 2.4" />
      <path d="M13.6 8.2c1 1.6 1.4 2.4.6 3.4-.5.6-1.6.5-1.9-.3" />
      <path d="M7 15.4h3.6M7.6 17h2.4" />
      <path d="M14.6 16.9c-.6 0-1-.5-1-1.1 0-.9.9-1.4 1.1-2.3.6.6 1.2 1.3 1.2 2.2 0 .7-.6 1.2-1.3 1.2z" fill="currentColor" stroke="none" />
    </g>

    <!-- Banner: affiliation clue -->
    <g v-else-if="name === 'banner'">
      <path d="M7 3.6h10v14.8l-5-3.2-5 3.2z" fill="currentColor" stroke="none" opacity=".2" />
      <path d="M7 3.6h10v14.8l-5-3.2-5 3.2z" />
      <path d="M5.2 3.6h13.6" />
      <circle cx="12" cy="9.4" r="2.1" />
    </g>

    <!-- White Lotus tile: settings -->
    <g v-else-if="name === 'lotus'">
      <rect x="3.6" y="3.6" width="16.8" height="16.8" rx="3" />
      <path d="M12 16.6c-2.4 0-4.4-1.5-5-3.6 1.6-.4 3-1.3 3.8-2.6.4 1 .8 1.7 1.2 2.2.4-.5.8-1.2 1.2-2.2.8 1.3 2.2 2.2 3.8 2.6-.6 2.1-2.6 3.6-5 3.6z" fill="currentColor" stroke="none" opacity=".25" />
      <path d="M12 16.6c-2.4 0-4.4-1.5-5-3.6 1.6-.4 3-1.3 3.8-2.6.4 1 .8 1.7 1.2 2.2.4-.5.8-1.2 1.2-2.2.8 1.3 2.2 2.2 3.8 2.6-.6 2.1-2.6 3.6-5 3.6z" />
      <path d="M12 12.6V7.6" />
    </g>

    <!-- Target: random starter -->
    <g v-else-if="name === 'target'">
      <circle cx="12" cy="12" r="8.4" />
      <circle cx="12" cy="12" r="4.8" />
      <circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none" />
    </g>

    <!-- Compass rose: generic marker -->
    <g v-else-if="name === 'compass'">
      <circle cx="12" cy="12" r="8.6" />
      <path d="M15.2 8.8l-1.9 4.5-4.5 1.9 1.9-4.5z" fill="currentColor" stroke="none" opacity=".65" />
      <path d="M15.2 8.8l-1.9 4.5-4.5 1.9 1.9-4.5z" />
    </g>

    <!-- Share -->
    <g v-else-if="name === 'share'">
      <circle cx="17.4" cy="6.2" r="2.4" />
      <circle cx="6.6" cy="12" r="2.4" />
      <circle cx="17.4" cy="17.8" r="2.4" />
      <path d="M8.8 10.8l6.4-3.4M8.8 13.2l6.4 3.4" />
    </g>
  </svg>
</template>

<style scoped>
.icon {
  display: block;
  flex: none;
  overflow: visible;
}
</style>
