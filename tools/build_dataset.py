#!/usr/bin/env python3
"""Merge the wiki draft with the reviewed overrides into the app dataset.

Inputs:
  out/characters.draft.json  (fetch_wiki.py)
  out/corrections.json       (curate.py)
  out/history.json           (curate.py)
  out/portraits.json         (download_portraits.py)
  ../src/data/episodes.json
Outputs:
  ../src/data/characters.json
  out/final_report.txt
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "out"
DATA = HERE.parent / "src" / "data"

VALID_GENDER = {"Male", "Female", "Unknown"}
VALID_NATION = {"Water Tribe", "Earth Kingdom", "Fire Nation", "Air Nomads", "Spirit World", "Unknown"}
VALID_BENDING = {"Non-bender", "Waterbender", "Earthbender", "Firebender", "Airbender", "Avatar"}
VALID_SKILLS = {"Healing", "Bloodbending", "Metalbending", "Sandbending", "Plantbending", "Lavabending",
                "Energybending", "Lightning", "Lightning redirection", "Combustion", "Chi-blocking",
                "Seismic sense", "Swords", "Archery", "Boomerang", "War fans", "Knives"}
VALID_HAIR = {"Black", "Brown", "Gray", "White", "Auburn", "Bald", "None"}


def norm_hair(raw):
    if not raw:
        return None
    s = re.split(r"[/,]| and | with ", raw)[0].strip()
    s = re.sub(r"^(Dark|Light|Dirty)\s+", "", s, flags=re.I)
    s = s.capitalize()
    return {"Grey": "Gray", "Blonde": "Blond", "Cream": "White"}.get(s, s)


def main():
    drafts = {r["requested"]: r for r in json.loads((OUT / "characters.draft.json").read_text())}
    corrections = json.loads((OUT / "corrections.json").read_text())
    history = json.loads((OUT / "history.json").read_text())
    portraits = json.loads((OUT / "portraits.json").read_text())
    episodes = json.loads((DATA / "episodes.json").read_text())
    ep_by_n = {e["n"]: e for e in episodes}

    problems = []
    final = []
    for req, d in drafts.items():
        c = corrections.get(req, {})

        def pick(key, default=None):
            return c[key] if key in c else d.get(key, default)

        name = c.get("name", d["name"])
        gender = pick("gender") or "Unknown"
        if gender not in VALID_GENDER:
            problems.append(f"{req}: bad gender {gender!r}")
            gender = "Unknown"

        nation = pick("nation") or "Unknown"
        if nation not in VALID_NATION:
            problems.append(f"{req}: bad nation {nation!r} -> Unknown")
            nation = "Unknown"

        bending = pick("bending") or "Non-bender"
        if bending not in VALID_BENDING:
            problems.append(f"{req}: bad bending {bending!r}")
            bending = "Non-bender"

        skills = pick("skills") or []
        bad = [s for s in skills if s not in VALID_SKILLS]
        if bad:
            problems.append(f"{req}: bad skills {bad}")
            skills = [s for s in skills if s in VALID_SKILLS]

        affiliation = c.get("affiliation")
        if not affiliation:
            problems.append(f"{req}: NO PRIMARY AFFILIATION (draft: {d['affiliations'][:3]})")
            affiliation = (d["affiliations"] or ["Unknown"])[0]

        hair = c.get("hair") or norm_hair(d.get("hair"))
        if hair not in VALID_HAIR:
            problems.append(f"{req}: bad hair {hair!r} (raw {d.get('hair')!r})")
            hair = "Unknown"

        age = c["age"] if "age" in c else (d.get("bioAge") or d.get("age"))
        first = pick("firstEpisode")
        if first is None or first not in ep_by_n:
            problems.append(f"{req}: no first episode ({d.get('appearanceTitle')})")

        aliases = c.get("aliases") if "aliases" in c else [a for a in d.get("aliases", []) if len(a) <= 30][:4]
        aliases = [a for a in aliases if a.lower() != name.lower()]

        hist = dict(history.get(req, {}))
        if not hist.get("affiliation"):
            hist["affiliation"] = [{"value": affiliation, "episode": first}]
        if skills and not hist.get("skills"):
            hist["skills"] = [{"value": s, "episode": first} for s in skills]
        for field in ("affiliation", "skills"):
            for e in hist.get(field, []):
                if first is not None and e["episode"] < first:
                    problems.append(f"{req}: {field} history at {e['episode']} predates debut {first}")
        if hist.get("affiliation") and hist["affiliation"][0]["value"] != affiliation:
            problems.append(f"{req}: affiliation {affiliation!r} != history head {hist['affiliation'][0]['value']!r}")
        if skills and hist.get("skills") and set(e["value"] for e in hist["skills"]) != set(skills):
            problems.append(f"{req}: skills {skills} != history {[e['value'] for e in hist['skills']]}")

        if req not in portraits:
            problems.append(f"{req}: no portrait")
        if not pick("description"):
            problems.append(f"{req}: no description")

        final.append({
            "name": name,
            "aliases": aliases,
            "gender": gender,
            "nation": nation,
            "origin": d.get("origin"),
            "bending": bending,
            "elements": d.get("elements", []),
            "skills": skills,
            "affiliation": affiliation,
            "age": age,
            "trueAge": c.get("trueAge"),
            "hair": hair,
            "eyes": d.get("eyes"),
            "firstEpisode": first,
            "firstEpisodeNote": d.get("appearanceNote"),
            "history": hist,
            "portrait": portraits.get(req),
            "wikiPage": d["name"],
            "description": pick("description"),
        })

    final.sort(key=lambda r: r["name"])
    names = Counter(r["name"] for r in final)
    for n, k in names.items():
        if k > 1:
            problems.append(f"duplicate display name {n!r}")
    (DATA / "characters.json").write_text(json.dumps(final, indent=1, ensure_ascii=False))

    lines = [f"{len(final)} characters", ""]
    for field in ("affiliation", "nation", "bending", "hair", "gender"):
        lines.append(f"== {field} ==")
        for k, n in Counter(r[field] for r in final).most_common():
            lines.append(f"  {n:3d}  {k}")
    lines.append("== skills ==")
    for k, n in Counter(s for r in final for s in r["skills"]).most_common():
        lines.append(f"  {n:3d}  {k}")
    lines.append("== first book ==")
    for k, n in sorted(Counter(ep_by_n[r['firstEpisode']]['book'] for r in final if r['firstEpisode']).items()):
        lines.append(f"  {n:3d}  Book {k}")
    lines.append("")
    lines.append("== problems / notes ==")
    lines += ["  " + p for p in problems]
    (OUT / "final_report.txt").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
