#!/usr/bin/env python3
"""Fetch character data from the Avatar wiki API and build a draft dataset.

Outputs:
  tools/out/characters.draft.json  - parsed per-character records
  tools/out/report.json            - missing/ambiguous fields needing review
  tools/out/images.json            - portrait URL per character
"""
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://avatar.fandom.com/api.php"
UA = {"User-Agent": "AvatarDleFanProject/1.0 (personal, low-volume data fetch)"}
HERE = Path(__file__).parent
CACHE = HERE / "cache"
OUT = HERE / "out"
DATA = HERE.parent / "src" / "data"
CACHE.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)


def api_get(params, cache_key):
    cache_file = CACHE / (cache_key + ".json")
    if cache_file.exists():
        return json.loads(cache_file.read_text())
    qs = urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(f"{API}?{qs}", headers=UA)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read().decode())
            cache_file.write_text(json.dumps(data))
            time.sleep(0.4)
            return data
        except Exception as e:
            print(f"  retry {attempt+1} for {cache_key}: {e}", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"failed: {cache_key}")


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def fetch_content(titles):
    """Return {requested_title: (resolved_title, wikitext)}"""
    result = {}
    for batch in chunks(titles, 20):
        bh = hashlib.md5("|".join(batch).encode()).hexdigest()[:10]
        d = api_get({
            "action": "query", "titles": "|".join(batch),
            "prop": "revisions", "rvprop": "content", "rvslots": "main",
            "redirects": 1,
        }, f"content_{bh}")
        q = d["query"]
        redir = {}
        for r in q.get("normalized", []) + q.get("redirects", []):
            redir[r["from"]] = r["to"]
        by_title = {}
        for pid, p in q["pages"].items():
            if int(pid) < 0:
                by_title[p.get("title", "")] = None
                continue
            by_title[p["title"]] = p["revisions"][0]["slots"]["main"]["*"]
        for t in batch:
            r = t
            seen = set()
            while r in redir and r not in seen:
                seen.add(r)
                r = redir[r]
            result[t] = (r, by_title.get(r))
    return result


def fetch_image_urls(filenames):
    """Return {File title: url}"""
    result = {}
    titles = [f"File:{f}" for f in filenames]
    for batch in chunks(titles, 20):
        bh = hashlib.md5("|".join(batch).encode()).hexdigest()[:10]
        d = api_get({
            "action": "query", "titles": "|".join(batch),
            "prop": "imageinfo", "iiprop": "url", "redirects": 1,
        }, f"imginfo_{bh}")
        q = d["query"]
        redir = {r["from"]: r["to"] for r in q.get("normalized", []) + q.get("redirects", [])}
        by_title = {}
        for pid, p in q["pages"].items():
            info = p.get("imageinfo")
            if info:
                by_title[p["title"]] = info[0]["url"]
        for t in batch:
            r = t
            while r in redir:
                r = redir[r]
            if r in by_title:
                result[t[len("File:"):]] = by_title[r]
    return result


# ---------- wikitext parsing ----------

def find_template(text, name_re):
    """Balanced-brace scan for the first template whose name matches."""
    if not text:
        return None
    m = re.search(r"\{\{\s*(" + name_re + r")", text, re.I)
    if not m:
        return None
    i = m.start()
    depth = 0
    j = i
    while j < len(text):
        if text[j:j+2] == "{{":
            depth += 1
            j += 2
        elif text[j:j+2] == "}}":
            depth -= 1
            j += 2
            if depth == 0:
                break
        else:
            j += 1
    return text[i:j]


def template_fields(box):
    # gallery captions use bare pipes, which would otherwise split the field
    box = re.sub(r"<gallery[^>]*>.*?</gallery>",
                 lambda m: m.group(0).replace("|", "\x00"), box, flags=re.S)
    fields = {}
    depth = 0
    cur = []
    parts = []
    k = 0
    while k < len(box):
        c2 = box[k:k+2]
        if c2 in ("{{", "[["):
            depth += 1
            cur.append(c2)
            k += 2
        elif c2 in ("}}", "]]"):
            depth -= 1
            cur.append(c2)
            k += 2
        elif box[k] == "|" and depth == 1:
            parts.append("".join(cur))
            cur = []
            k += 1
        else:
            cur.append(box[k])
            k += 1
    parts.append("".join(cur))
    for part in parts[1:]:
        if "=" in part:
            key, _, val = part.partition("=")
            val = val.strip()
            if val.endswith("}}") and val.count("}}") > val.count("{{"):
                val = val[:-2].strip()
            fields[key.strip().lower()] = val.replace("\x00", "|")
    return fields


def strip_refs(s):
    if not s:
        return s
    out = []
    k = 0
    while k < len(s):
        if s[k:k+2] == "{{":
            depth = 0
            j = k
            while j < len(s):
                if s[j:j+2] == "{{":
                    depth += 1
                    j += 2
                elif s[j:j+2] == "}}":
                    depth -= 1
                    j += 2
                    if depth == 0:
                        break
                else:
                    j += 1
            inner = s[k+2:j-2]
            parts = inner.split("|")
            name = parts[0].strip().lower()
            if name in ("chinese", "avatarian"):
                # {{Chinese|漢字|pinyin}} carries no Latin text; {{Avatarian|glyphs|Name}} -> Name
                out.append(parts[2] if name == "avatarian" and len(parts) > 2 else "")
            elif name.startswith("cite") or name in ("ref",):
                pass
            else:
                out.append(s[k:j])
            k = j
        else:
            out.append(s[k])
            k += 1
    s = "".join(out)
    s = re.sub(r"<ref[^>]*/>", "", s)
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    return s.strip()


def strip_links(s):
    if not s:
        return s
    s = re.sub(r"\[\[([^\]|]*)\|([^\]]*)\]\]", r"\2", s)
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    s = s.replace("'''", "").replace("''", "")
    return s.strip()


def strip_small(s):
    return re.sub(r"<small>.*?</small>", "", s or "", flags=re.S)


def bullets(raw):
    """Bulleted or single value -> list of cleaned strings (parentheticals kept)."""
    if not raw:
        return []
    s = strip_refs(raw)
    items = [x for x in re.split(r"^\*\s*|\n\*\s*|<br\s*/?>", s, flags=re.M) if x.strip()]
    out = []
    for it in items:
        t = strip_links(re.sub(r"</?small>", "", it)).strip().strip(",;")
        if t:
            out.append(t)
    return out


def clean_list(raw):
    """Bullets with the (formerly)/(by X) notes removed."""
    out = []
    for it in bullets(strip_small(raw)):
        t = re.sub(r"\s*\(.*?\)", "", it).strip().strip(",;")
        if t:
            out.append(t)
    return out


def parse_age(raw):
    """-> (age, biological age) from the first (series) bullet."""
    if not raw:
        return None, None
    first = bullets(raw)
    if not first:
        return None, None
    s = first[0]
    bio = re.search(r"biologically\s+(\d+)", s)
    m = re.search(r"(\d+)", s)
    return (int(m.group(1)) if m else None), (int(bio.group(1)) if bio else None)


def parse_appearance(raw):
    """-> (episode title, note)"""
    if not raw:
        return None, None
    s = strip_refs(raw)
    note = re.search(r"<small>\((.*?)\)</small>", s)
    m = re.search(r"\[\[([^\]|]*)(?:\|[^\]]*)?\]\]", s)
    title = m.group(1).strip() if m else strip_links(strip_small(s)).strip('" ')
    title = re.sub(r"\s*\(episode\)$", "", title)
    return title, (strip_links(note.group(1)) if note else None)


def parse_image(raw):
    if not raw:
        return None
    s = raw
    g = re.search(r"<gallery[^>]*>(.*?)</gallery>", s, re.S)
    if g:
        lines = [l.strip() for l in g.group(1).splitlines() if l.strip()]
        if not lines:
            return None
        s = lines[0].split("|")[0]
    s = strip_refs(s).strip()
    s = re.sub(r"^\[\[(?:File|Image):", "", s).split("|")[0].rstrip("]").strip()
    return s or None


def strip_files(s):
    """Drop [[File:...]] / [[Image:...]] embeds, whose captions may nest links."""
    out = []
    k = 0
    while k < len(s):
        if s[k:k+2] == "[[" and re.match(r"\[\[\s*(File|Image):", s[k:], re.I):
            depth = 0
            j = k
            while j < len(s):
                if s[j:j+2] == "[[":
                    depth += 1
                    j += 2
                elif s[j:j+2] == "]]":
                    depth -= 1
                    j += 2
                    if depth == 0:
                        break
                else:
                    j += 1
            k = j
        else:
            out.append(s[k])
            k += 1
    return "".join(out)


def parse_lead(txt, box_txt, limit=480):
    """First paragraph after the infobox -> plain prose, cut at a sentence boundary."""
    if not txt:
        return None
    body = txt
    if box_txt:
        i = txt.find(box_txt)
        if i >= 0:
            body = txt[i + len(box_txt):]
    body = body.split("\n==", 1)[0]
    body = strip_files(strip_refs(body))
    body = re.sub(r"\{\{[^{}]*\}\}", "", body)
    body = re.sub(r"<br\s*/?>", " ", body)
    body = re.sub(r"<[^>]+>", "", body)
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    paras = [p for p in paras if not p.startswith((":", "*", "{", "|", "["))]
    if not paras:
        return None
    text = strip_links(paras[0])
    text = re.sub(r"\s+", " ", text).replace(" ,", ",").replace(" .", ".").strip()
    if len(text) <= limit:
        return text or None
    out = ""
    for sent in re.split(r"(?<=[.!?])\s+(?=[A-Z\"“])", text):
        if out and len(out) + len(sent) + 1 > limit:
            break
        out = f"{out} {sent}".strip()
    return out or text[:limit]


ELEMENTS = {"airbender": "Air", "waterbender": "Water", "earthbender": "Earth", "firebender": "Fire"}
NATIONS = {"air": "Air Nomads", "water": "Water Tribe", "earth": "Earth Kingdom", "fire": "Fire Nation",
           "spirit": "Spirit World", "urn": "Unknown"}

SKILL_PATTERNS = [
    ("Healing", r"\bhealing\b"),
    ("Bloodbending", r"bloodbend"),
    ("Metalbending", r"metalbend"),
    ("Sandbending", r"sandbend"),
    ("Lightning redirection", r"lightning redirect"),
    ("Lightning", r"lightning generation|\blightning\b(?! redirect)"),
    ("Combustion", r"combustion"),
    ("Chi-blocking", r"chi[- ]block"),
    ("Swords", r"sword|\bdao\b|\bjian\b|katana|\bsabre\b|\bsaber\b"),
    ("Archery", r"archer|\bbow\b"),
    ("Boomerang", r"boomerang"),
    ("War fans", r"\bfans?\b|tessen"),
    ("Knives", r"knive|knife|shuriken|stiletto|dagger|dart"),
    ("Spirit projection", r"spirit(ual)? projection|astral"),
    ("Seismic sense", r"seismic"),
]


def parse_skills(*raws):
    text = " ".join(strip_links(strip_refs(r or "")) for r in raws).lower()
    return [name for name, pat in SKILL_PATTERNS if re.search(pat, text)]


def parse_bending(icons, fightingstyle):
    found = []
    for tok in (icons or "").split("|"):
        t = tok.strip().lower()
        if t in ELEMENTS and ELEMENTS[t] not in found:
            found.append(ELEMENTS[t])
    fs = strip_links(strip_refs(fightingstyle or "")).lower()
    for key, el in (("waterbending", "Water"), ("earthbending", "Earth"),
                    ("firebending", "Fire"), ("airbending", "Air")):
        if key in fs and el not in found:
            found.append(el)
    if len(found) >= 2:
        return "Avatar", found
    if len(found) == 1:
        return f"{found[0]}bender", found
    return "Non-bender", []


def main():
    roster = json.loads((HERE / "roster.json").read_text())
    names = [n for group in roster.values() for n in group]
    episodes = json.loads((DATA / "episodes.json").read_text())
    ep_by_title = {e["title"]: e["n"] for e in episodes}
    print(f"{len(names)} characters")

    print("fetching page content...")
    content = fetch_content(names)

    records = []
    report = {"missing_page": [], "no_infobox": [], "issues": {}}
    image_files = {}
    for req_name in names:
        rt, txt = content[req_name]
        if txt is None:
            report["missing_page"].append(req_name)
            continue
        box_txt = find_template(txt, r"[\w ]*infobox")
        if box_txt is None:
            report["no_infobox"].append(req_name)
            box = {}
        else:
            box = template_fields(box_txt)
        icons_t = find_template(txt, r"Icons")
        icons = icons_t[2:-2] if icons_t else ""

        pronouns = strip_links(strip_refs(box.get("pronouns", ""))).lower()
        gender = "Male" if "he/him" in pronouns else "Female" if "she/her" in pronouns else None
        nation_raw = strip_links(strip_refs(box.get("nation", ""))).lower().strip()
        nation = NATIONS.get(nation_raw, nation_raw or None)
        bending, elements = parse_bending(icons, box.get("fightingstyle"))
        age, bio_age = parse_age(box.get("age"))
        ep_title, ep_note = parse_appearance(box.get("appearance"))
        image = parse_image(box.get("image"))
        if image:
            image_files[req_name] = image

        rec = {
            "name": rt,
            "requested": req_name,
            "gender": gender,
            "nation": nation,
            "origin": clean_list(box.get("origin"))[:1] and clean_list(box.get("origin"))[0],
            "ethnicity": clean_list(box.get("ethnicity"))[:1] and clean_list(box.get("ethnicity"))[0],
            "bending": bending,
            "elements": elements,
            "skills": parse_skills(box.get("fightingstyle"), box.get("weapon")),
            "fightingStyleRaw": strip_links(strip_refs(strip_small(box.get("fightingstyle", "")))),
            "weaponRaw": strip_links(strip_refs(strip_small(box.get("weapon", "")))),
            "affiliations": clean_list(box.get("affiliation")),
            "positions": clean_list(box.get("position"))[:4],
            "age": age,
            "bioAge": bio_age,
            "hair": clean_list(box.get("hair"))[:1] and clean_list(box.get("hair"))[0],
            "eyes": clean_list(box.get("eyes"))[:1] and clean_list(box.get("eyes"))[0],
            "aliases": clean_list(box.get("alias")) + clean_list(box.get("nickname")),
            "appearanceTitle": ep_title,
            "appearanceNote": ep_note,
            "firstEpisode": ep_by_title.get(ep_title),
            "imageFile": image,
            "description": parse_lead(txt, box_txt),
        }
        for k in ("origin", "ethnicity", "hair", "eyes"):
            if rec[k] == []:
                rec[k] = None
        issues = [k for k in ("gender", "nation", "age", "hair", "firstEpisode", "imageFile")
                  if rec[k] in (None, [])]
        if not rec["affiliations"]:
            issues.append("affiliations")
        if issues:
            report["issues"][req_name] = issues
        records.append(rec)

    print("fetching image urls...")
    urls = fetch_image_urls(sorted(set(image_files.values())))
    for r in records:
        r["image"] = urls.get(r["imageFile"]) if r["imageFile"] else None
        if r["imageFile"] and not r["image"]:
            report["issues"].setdefault(r["requested"], []).append("image url")

    (OUT / "characters.draft.json").write_text(
        json.dumps(records, indent=1, ensure_ascii=False))
    (OUT / "report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    (OUT / "images.json").write_text(json.dumps(
        {r["requested"]: r["image"] for r in records}, indent=1, ensure_ascii=False))
    print(f"wrote {len(records)} records")
    print(f"missing pages: {report['missing_page']}")
    print(f"no infobox: {report['no_infobox']}")
    print(f"records with issues: {len(report['issues'])}")


if __name__ == "__main__":
    main()
