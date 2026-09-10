# AvatarDle (fan game)

Guess the daily *Avatar: The Last Airbender* character, one guess at a time, using colour-coded
property comparisons. A sibling of the [OnePieceDle recreation](../../One%20Piece/onepiecedle) that
shares its engine and look, retargeted to the four nations.

Built with Vue 3 + Vite. Fully responsive — all nine columns fit on a phone screen.

## Play

```bash
npm install
npm run dev
```

Then open http://localhost:5173.

## How the game works

Type a character name and submit. Each guess reveals a row of tiles:

| Colour | Meaning |
| --- | --- |
| 🟩 Green | exact match |
| 🟨 Yellow | partial match (some overlap — e.g. one shared skill, or the Avatar against a single-element bender) |
| 🟥 Red | no overlap |

| Column | Values |
| --- | --- |
| Gender | Male, Female, Unknown |
| Nation | Water Tribe, Earth Kingdom, Fire Nation, Air Nomads, Spirit World |
| Bending | Non-bender, Waterbender, Earthbender, Firebender, Airbender, Avatar |
| Skills | sub-bending and signature techniques (healing, bloodbending, metalbending, lightning, chi-blocking, swords, boomerang, …) shown as icons |
| Affiliation | main group at the end of the series (Team Avatar, Dai Li, Fire Nation Royal Family, Order of the White Lotus, …) |
| Age | age during the series, with ▲/▼ arrows (Aang counts as 12) |
| Hair | Black, Brown, Gray, White, Auburn, Bald, None |
| First Seen | book and episode of first appearance (`B2 E06`), with ▲/▼ arrows in airing order |

Clues unlock as you guess: **First Appearance** (book, episode and title) after 5 tries, **Bending**
(type plus skills) after 8, **Affiliation** after 10. The daily character resets at local midnight;
stats live in `localStorage`.

Modes: 🌀 **Classic** (one shared daily character), 🎲 **Practice** (unlimited, honours the gallery's
practice pool) and 📖 **Gallery** (browse and search the roster, open a card for full details, a short
description taken from the opening of its wiki page, and a link to that page).

### Spoiler limit by book

⚙️ Settings lets you say how far you've watched: **Book 1: Water**, **Book 2: Earth**, or everything.
Only characters who have appeared by the end of that book are in play — as the daily answer, in the
guess suggestions and in the gallery — and each card **rewinds** to what was known by then:
affiliation and skills follow the story, so with a Book 1 limit Zuko is still Fire Nation royalty,
Katara has no bloodbending and Toph has not appeared. The wiki description covers the whole series,
so a limited card folds it behind a button. Players on the same limit share the same daily
character. Episodes are numbered 1–61 across the three books; the limit is the book's last episode.

⚠️ With no limit set, the data covers the whole series.

## Data

128 characters from the animated series only (no comics, Korra or live action), including a few
animals and spirits. Values are as of the end of Book 3. Everything is derived from the
[Avatar Wiki](https://avatar.fandom.com) and then hand-reviewed, since the wiki's infoboxes fold in
the comics and *Korra* (Toph is never "Chief of Police" here).

```bash
python3 tools/fetch_wiki.py          # infoboxes -> tools/out/characters.draft.json (cached)
python3 tools/download_portraits.py  # portraits -> public/portraits/
python3 tools/curate.py              # reviewed overrides -> tools/out/corrections.json, history.json
python3 tools/build_dataset.py       # merge + validate -> src/data/characters.json, out/final_report.txt
python3 tools/make_backgrounds.py    # painted backdrops -> public/backgrounds/, src/data/backgrounds.json
python3 tools/make_textures.py       # wear map for the logo -> public/textures/
node tools/check_spoilers.mjs        # asserts the book rewinds
node api/tools/gen_data.mjs          # regenerate the worker's copy of the roster
```

`tools/roster.json` is the character list, `src/data/episodes.json` the 61 episodes and
`src/data/books.json` the three books. `tools/curate.py` holds every reviewed value as code:
the primary affiliation per character, hair and age fixes, the skills vocabulary, description
rewrites (`DESCRIPTION`, for leads that lean on the comics), and the in-series timelines
(`history`) that the book limit rewinds through. Each description is the first paragraph of the
wiki page, cut at a sentence boundary around 480 characters. First appearances follow the
wiki, so visions and flashbacks count (Toph is first glimpsed in *The Swamp*).

## Look and feel

Same engine as the One Piece version: parchment panels with an inline SVG grain, a drawn SVG
wordmark (here a four-nations seal in front of letters cycling water, earth, fire and air
gradients under a generated wear map), a streak flame, drawn toolbar icons, and a slowly panning
backdrop. The backdrop is the series' world map from the wiki, fetched and encoded by
`tools/download_backgrounds.py` (centre-cropped to 16:9, 1920px, WebP with a JPEG fallback). The
wiki has no other widescreen stills large enough, so `tools/make_backgrounds.py` also paints six
scenes procedurally — Southern Air Temple, Northern Water Tribe, Ba Sing Se, Fire Nation Capital,
Foggy Swamp, Spirit World — reachable with `?bg=1`–`?bg=6` for anyone who wants to swap the map
out. A book limit tints the banner in that book's element colour.

## Backend (solve counter + leaderboard)

`api/` is the same Cloudflare Worker + D1 setup as the original (pseudonym + password accounts,
PBKDF2 in the browser, verified solves, streaks derived from stored days), deployed as
`avatardle-api` with a D1 database named `avatardle` and an `IP_SALT` secret.

```bash
node api/tools/gen_data.mjs                        # after changing characters.json / books.json
cd api && npx wrangler d1 execute avatardle --remote --file=./schema.sql   # first time only
cd api && npx wrangler deploy
```

`schema.sql` is all `CREATE TABLE IF NOT EXISTS`; changes to a live schema go in numbered files
under `api/migrations/`. `VITE_API_URL` in `.env.production` points the site at the worker; it is a
public endpoint, not a secret, and every call fails soft. The spoiler limit travels over the wire
under the original `arcLimit`/`arc_limit` names and holds the book name.

## Deploying

Pushing to `main` builds and publishes to GitHub Pages via `.github/workflows/deploy.yml`.
Enable it once under **Settings → Pages → Source: GitHub Actions**.

## Credits

Avatar: The Last Airbender © Nickelodeon / Paramount. Character data and portraits from the
[Avatar Wiki](https://avatar.fandom.com) (CC BY-SA). Fan project.
