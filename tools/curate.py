#!/usr/bin/env python3
"""Reviewed overrides for the wiki draft, as code so they can be diffed and commented.

Writes out/corrections.json and out/history.json for build_dataset.py. Every value
here is the character as known by the end of Book 3; the wiki's infobox mixes in the
comics and Korra, so the primary affiliation in particular has to be picked by hand.
"""
import json
from pathlib import Path

OUT = Path(__file__).parent / "out"

# requested name -> primary affiliation (end of series)
AFFILIATION = {}
def aff(value, *names):
    for n in names:
        AFFILIATION[n] = value

aff("Team Avatar", "Aang", "Katara", "Sokka", "Toph Beifong", "Zuko", "Suki", "Appa", "Momo")
aff("Order of the White Lotus", "Iroh", "Piandao", "Jeong Jeong")
aff("Fire Nation Royal Family", "Ozai", "Azula", "Ursa", "Sozin", "Lu Ten")
aff("Azula's team", "Mai", "Ty Lee")
aff("Fire Nation military", "Zhao", "Warden (Boiling Rock)", "Poon", "Yon Rha")
aff("Sun Warriors", "Ran and Shaw", "Sun Warrior chief")
aff("Fire Nation", "Combustion Man", "Hide", "On Ji", "Roku", "Chit Sang", "Lo and Li")
aff("Southern Water Tribe", "Hakoda", "Kanna", "Hama", "Kya (nonbender)")
aff("Northern Water Tribe", "Pakku", "Yue", "Arnook", "Hahn", "Yagoda", "Kuruk")
aff("Foggy Swamp Tribe", "Huu", "Due", "Tho")
aff("Omashu", "Bumi (King of Omashu)")
aff("Ba Sing Se", "Kuei", "Bosco")
aff("Dai Li", "Long Feng", "Joo Dee")
aff("Freedom Fighters", "Jet", "Smellerbee", "Longshot", "Pipsqueak")
aff("Kyoshi Island", "Kyoshi")
aff("Earth Rumble", "The Boulder", "The Big Bad Hippo")
aff("Beifong family", "Lao Beifong", "Poppy Beifong")
aff("Si Wong tribes", "Sha-Mo", "Ghashiun")
aff("Northern Air Temple", "Mechanist", "Teo")
aff("Earth Kingdom", "Haru", "Lee", "Sela", "Chong", "June", "Cabbage merchant", "Canyon guide", "Nyla")
aff("Air Nomads", "Gyatso", "Yangchen", "Pathik")
aff("Spirit World", "Wan Shi Tong", "Koh", "Hei Bai", "Tui", "La", "Lion turtle", "Painted Lady")

# Display names where the wiki title carries a disambiguator or lowercase.
NAMES = {
    "Bumi (King of Omashu)": "Bumi", "Kya (nonbender)": "Kya",
    "Warden (Boiling Rock)": "The Warden", "Lion turtle": "Lion Turtle",
    "Cabbage merchant": "Cabbage Merchant",
    "Canyon guide": "Canyon Guide", "Sun Warrior chief": "Sun Warrior Chief", "Mechanist": "The Mechanist",
}

ALIASES = {
    "Aang": ["Avatar Aang", "Twinkle Toes", "Kuzon", "Bonzu Pippinpaddleopsicopolis III"],
    "Katara": ["The Painted Lady", "Sugar Queen", "Sapphire Fire"],
    "Sokka": ["Wang Fire", "Captain Boomerang", "Snoozles"],
    "Toph Beifong": ["Toph", "The Blind Bandit", "The Runaway", "Melon Lord"],
    "Zuko": ["The Blue Spirit", "Lee", "Zuzu", "Sifu Hotman"],
    "Iroh": ["The Dragon of the West", "Mushi", "Uncle Iroh"],
    "Azula": ["Princess Azula"],
    "Ozai": ["Fire Lord Ozai", "Phoenix King"],
    "Bumi (King of Omashu)": ["King Bumi", "The Mad Genius"],
    "Kuei": ["Earth King Kuei", "The Earth King"],
    "Pakku": ["Master Pakku"],
    "Gyatso": ["Monk Gyatso"],
    "Pathik": ["Guru Pathik"],
    "Combustion Man": ["Sparky Sparky Boom Man"],
    "Roku": ["Avatar Roku"], "Kyoshi": ["Avatar Kyoshi"], "Kuruk": ["Avatar Kuruk"], "Yangchen": ["Avatar Yangchen"],
    "Zhao": ["Commander Zhao", "Admiral Zhao", "Zhao the Conqueror"],
    "Jeong Jeong": ["The Deserter"],
    "Long Feng": ["Grand Secretariat"],
    "Wan Shi Tong": ["The Knowledge Spirit", "He Who Knows Ten Thousand Things"],
    "Koh": ["The Face Stealer"],
    "Tui": ["The Moon Spirit"], "La": ["The Ocean Spirit"],
    "Hei Bai": ["The Forest Spirit"],
    "Yue": ["Princess Yue"],
    "The Big Bad Hippo": ["The Hippo"],
    "Kanna": ["Gran Gran"],
    "Hama": ["The Puppetmaster"],
    "Lee": ["Lee (farm boy)"],
    "Hakoda": ["Chief Hakoda"],
    "Arnook": ["Chief Arnook"],
    "Kanna": ["Gran Gran", "Kanna of the Southern Water Tribe"],
}

GENDER = {"Lo and Li": "Female", "Ran and Shaw": "Unknown", "Due": "Male",
          "Tho": "Male", "Tui": "Unknown", "Lion turtle": "Male"}

NATION = {"Pathik": "Unknown", "Lion turtle": "Spirit World"}

BENDING = {"Yue": "Non-bender", "Tui": "Non-bender", "La": "Non-bender", "Lion turtle": "Non-bender"}

HAIR = {"Aang": "Bald", "Gyatso": "Bald", "Pathik": "Bald", "Combustion Man": "Bald",
        "Zhao": "Black", "Zuko": "Brown", "Appa": "White", "Momo": "White",
        "Hei Bai": "White", "Koh": "None", "Wan Shi Tong": "None", "Ran and Shaw": "None", "Tui": "None",
        "La": "None", "Lion turtle": "None", "Nyla": "Brown",
        "Bosco": "Brown", "Sun Warrior chief": "Black"}

# Age during the series; the tile shows this, the modal adds the true age.
AGE = {"Aang": 12, "Suki": 15, "Ty Lee": 14, "Mai": 15, "Haru": 16, "Kyoshi": 230,
       "Roku": 70, "Sozin": None}
TRUE_AGE = {"Aang": 112}

SKILLS = {
    "Aang": ["Energybending"],
    "Katara": ["Healing", "Bloodbending"],
    "Sokka": ["Boomerang", "Swords"],
    "Toph Beifong": ["Metalbending", "Seismic sense"],
    "Zuko": ["Swords", "Lightning redirection"],
    "Iroh": ["Lightning", "Lightning redirection"],
    "Azula": ["Lightning"],
    "Ozai": ["Lightning"],
    "Suki": ["War fans"],
    "Yagoda": ["Healing"],
    "Kyoshi": ["War fans"],
    "Huu": ["Plantbending"],
    "Lion turtle": ["Energybending"],
    "Roku": ["Lavabending"],
    "Smellerbee": ["Knives"],
    "Sokka": ["Boomerang", "Swords"],
}

# Values that change inside the series, newest first, dated by the episode the
# viewer learns them. Characters not listed get a single entry at their debut.
# Wiki leads fold in the comics and Korra; rewrite one here when it misleads.
DESCRIPTION = {
    "Aang": "Aang was the Air Nomad Avatar succeeding Avatar Roku. As the Avatar during the Hundred "
            "Year War, he was the only person capable of using all four bending arts: airbending, "
            "waterbending, earthbending, and firebending. He was also one of a select few Avatars to "
            "learn the ancient art of energybending, and the first known to have actively used it.",
    "Zuko": "Zuko was a Fire Nation royal and firebending master, the eldest child of Fire Lord Ozai "
            "and Princess Ursa. Originally the primary enemy of Team Avatar, Zuko devoted three years "
            "to trying to capture the long-lost Avatar to end his banishment and regain his honor as "
            "Crown Prince of the Fire Nation, before joining Team Avatar and being crowned Fire Lord at "
            "the end of the Hundred Year War.",
}

HISTORY = {
    "Zuko": {"affiliation": [{"value": "Team Avatar", "episode": 52}, {"value": "Fire Nation Royal Family", "episode": 1}],
             "skills": [{"value": "Lightning redirection", "episode": 29}, {"value": "Swords", "episode": 13}]},
    "Iroh": {"affiliation": [{"value": "Order of the White Lotus", "episode": 59}, {"value": "Fire Nation Royal Family", "episode": 1}],
             "skills": [{"value": "Lightning redirection", "episode": 21}, {"value": "Lightning", "episode": 21}]},
    "Piandao": {"affiliation": [{"value": "Order of the White Lotus", "episode": 59}, {"value": "Fire Nation", "episode": 44}]},
    "Jeong Jeong": {"affiliation": [{"value": "Order of the White Lotus", "episode": 59}, {"value": "Fire Nation military", "episode": 16}]},
    "Suki": {"affiliation": [{"value": "Team Avatar", "episode": 55}, {"value": "Kyoshi Warriors", "episode": 4}]},
    "Toph Beifong": {"affiliation": [{"value": "Team Avatar", "episode": 26}, {"value": "Beifong family", "episode": 24}],
                     "skills": [{"value": "Metalbending", "episode": 40}, {"value": "Seismic sense", "episode": 26}]},
    "Katara": {"skills": [{"value": "Bloodbending", "episode": 48}, {"value": "Healing", "episode": 18}]},
    "Sokka": {"skills": [{"value": "Swords", "episode": 44}, {"value": "Boomerang", "episode": 1}]},
    "Aang": {"skills": [{"value": "Energybending", "episode": 61}]},
    "Azula": {"skills": [{"value": "Lightning", "episode": 21}]},
    "Ozai": {"skills": [{"value": "Lightning", "episode": 51}]},
    "Lion turtle": {"skills": [{"value": "Energybending", "episode": 59}]},
}


def main():
    corrections = {}
    names = set(AFFILIATION) | set(NAMES) | set(ALIASES) | set(GENDER) | set(NATION) | set(BENDING) \
        | set(HAIR) | set(AGE) | set(SKILLS) | set(DESCRIPTION)
    for n in sorted(names):
        c = {}
        if n in AFFILIATION: c["affiliation"] = AFFILIATION[n]
        if n in NAMES: c["name"] = NAMES[n]
        if n in ALIASES: c["aliases"] = ALIASES[n]
        if n in GENDER: c["gender"] = GENDER[n]
        if n in NATION: c["nation"] = NATION[n]
        if n in BENDING: c["bending"] = BENDING[n]
        if n in HAIR: c["hair"] = HAIR[n]
        if n in AGE: c["age"] = AGE[n]
        if n in TRUE_AGE: c["trueAge"] = TRUE_AGE[n]
        if n in SKILLS: c["skills"] = SKILLS[n]
        if n in DESCRIPTION: c["description"] = DESCRIPTION[n]
        corrections[n] = c
    (OUT / "corrections.json").write_text(json.dumps(corrections, indent=1, ensure_ascii=False))
    (OUT / "history.json").write_text(json.dumps(HISTORY, indent=1, ensure_ascii=False))
    print(f"{len(corrections)} corrections, {len(HISTORY)} histories")


if __name__ == "__main__":
    main()
