<script setup>
const emit = defineEmits(['close'])
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal panel">
      <button class="modal-close" @click="emit('close')">×</button>
      <h2>How to play</h2>
      <p>Guess today's <i>Avatar: The Last Airbender</i> character. Each guess reveals its properties and how they compare to the hidden character.</p>
      <ul class="colors">
        <li><span class="swatch exact"></span><b>Green</b> — exact match</li>
        <li><span class="swatch partial"></span><b>Yellow</b> — partial match (some overlap)</li>
        <li><span class="swatch wrong"></span><b>Red</b> — no match</li>
      </ul>
      <p>On <b>Age</b> and <b>First Seen</b>, an arrow shows whether the hidden character's value is <b>▲ higher/later</b> or <b>▼ lower/earlier</b> than your guess.</p>

      <h3>Properties</h3>
      <table class="props">
        <tbody>
          <tr><td>Gender</td><td>Male, Female or Unknown</td></tr>
          <tr><td>Nation</td><td>Water Tribe, Earth Kingdom, Fire Nation, Air Nomads or Spirit World</td></tr>
          <tr><td>Bending</td><td>Non-bender, Waterbender, Earthbender, Firebender, Airbender or Avatar. Yellow when one is the Avatar and the other bends a single element</td></tr>
          <tr><td>Skills</td><td>Sub-bending and signature techniques: 💧 healing, 🩸 bloodbending, ⛓️ metalbending, 🏜️ sandbending, 🌿 plantbending, 🌋 lavabending, ✨ energybending, ⚡ lightning, ↩️ lightning redirection, 💥 combustion, 🤜 chi-blocking, 👣 seismic sense, ⚔️ swords, 🏹 archery, 🪃 boomerang, 🪭 war fans, 🔪 knives — ✖ none. Yellow when you share at least one but not all of them</td></tr>
          <tr><td>Affiliation</td><td>Main group or nation at the end of the series (e.g. Team Avatar, Dai Li, Fire Nation Royal Family)</td></tr>
          <tr><td>Age</td><td>Age during the series. Aang counts as 12 — his hundred years in the iceberg don't count</td></tr>
          <tr><td>Hair</td><td>Black, Brown, Gray, White, Auburn, Bald — or None for creatures and spirits</td></tr>
          <tr><td>First Seen</td><td>Book and episode of first appearance, as the Avatar Wiki records it (visions and flashbacks count). Arrows follow airing order</td></tr>
        </tbody>
      </table>

      <h3>Clues</h3>
      <p>Stuck? After several guesses you unlock the <b>First Appearance</b> clue (book and episode), the <b>Bending</b> clue (bending type and skills) and, after 10 guesses, the <b>Affiliation</b> clue.</p>
      <h3>Modes</h3>
      <table class="props">
        <tbody>
          <tr><td>🌀 Classic</td><td>One character per day, shared by everyone. Resets at your local midnight.</td></tr>
          <tr><td>🎲 Practice</td><td>Unlimited random characters — hit <b>New character</b> any time to reroll.</td></tr>
          <tr><td>📖 Gallery</td><td>Browse all characters and search by name, nation, bending or affiliation. Tap a card for full details, or untick it to keep it out of practice mode.</td></tr>
        </tbody>
      </table>

      <h3>🏆 Leaderboard</h3>
      <p>
        Pick a pseudonym and a password to join — no email required. Sign in with the same two on
        any device and your ranked record follows you. The same account works on
        <a href="https://hugobourretdesmarais.github.io/onepiecedle/">OnePieceDle</a>, and signing in
        on one signs you in on the other. There's no password reset yet, so don't reuse
        an important password. Every classic win is ranked, and the board shows the spoiler limit
        each player last won under. Your local 📊 stats stay on this device and are separate from
        your ranked record.
      </p>

      <h3>Avoiding spoilers</h3>
      <p>
        Not caught up? Open <b>Settings</b> and set how far you've watched. Only characters who have
        appeared by the end of that book show up as the answer, in the guess suggestions or in the
        gallery — and each card <b>rewinds</b> to what was known by then. Affiliation and skills
        follow the story: in Book 1, Zuko is still Fire Nation royalty chasing the Avatar, Katara
        has not learned bloodbending and Toph hasn't shown up at all.
      </p>

      <p class="note">Data from the Avatar Wiki — with no spoiler limit set, the whole series is fair game!</p>
    </div>
  </div>
</template>

<style scoped>
p, li { font-size: 15px; }
h3 {
  font-family: 'Lilita One', cursive;
  color: var(--brown-dark);
  margin-bottom: 4px;
}
.colors {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.props {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}
.props td {
  border-top: 1px solid var(--tan);
  padding: 5px 8px 5px 0;
  vertical-align: top;
}
.props td:first-child {
  font-weight: 700;
  white-space: nowrap;
  color: var(--brown-dark);
}
.note { font-style: italic; color: var(--brown); }
</style>
