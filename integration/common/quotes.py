"""The SEST quotation set: the lines the loading screen and the briefing
pages share.

One list, two readers. SEST Collection Fixes makes the set the game's
loading-screen text in place of its gameplay tips (build_loading_tips); the
campaign pack sets one under the banner of every mission briefing
(epigraph_xml), chosen by the mission's role. Changing a line here changes
it everywhere.

Every entry is one of three kinds, and the label says which, so a modern
internet aphorism never borrows the authority of a Fleet Admiral:

  named        a traceable speaker and an official or archival source; the
               year is given only where the source dates the line
  institution  an official formulation (a summit declaration, doctrine)
  maxim        a traditional or anonymous saying, labelled as such

The set and its attributions follow the 6 October 2026 research note
(docs/quotes.md keeps the source for every line). Wording is ASCII only:
straight quotes and hyphens, because the game's font has no glyph for the
curly kind in some weights, and a loading tip is one ini value - no '=' and
no line break.
"""

# theme -> the briefing roles that reach for it first (campaign_data role=)
ROLE_THEMES = {
    "escort": ("readiness", "deterrence", "coalition"),
    "patrol": ("deterrence", "credibility", "airpower"),
    "recon": ("credibility", "planning", "deterrence"),
    "strike": ("airpower", "adaptation", "readiness"),
    "fleet": ("coalition", "adaptation", "airpower"),
    "logistics": ("logistics", "industry", "readiness"),
    "opening": ("planning", "readiness", "deterrence"),
}

QUOTES = [
    # --- airpower ---------------------------------------------------------
    dict(text="Air superiority is not guaranteed. It must be earned every day.",
         who="Gen. Kenneth S. Wilsbach, Chief of Staff, US Air Force", year=2025,
         theme="airpower", kind="named",
         source="First letter to the force, December 2025 (af.mil)"),
    dict(text="Neither air superiority nor victory are American birthrights. Both are at "
              "significant risk.",
         who="Gen. Mark Kelly, Commander, Air Combat Command", year=2021,
         theme="airpower", kind="named",
         source="Air Combat Command address, 2021 (af.mil)"),
    dict(text="Victory smiles upon those who anticipate the changes in the character of "
              "war, not upon those who wait to adapt themselves after the changes occur.",
         who="Giulio Douhet", year=1921,
         theme="adaptation", kind="named",
         source="The Command of the Air; reproduced by Air University"),
    dict(text="We must think in terms of tomorrow.",
         who="Gen. Henry H. 'Hap' Arnold, US Army Air Forces", year=None,
         theme="planning", kind="named",
         source="Air University, historical treatment of Arnold and future airpower"),
    # --- deterrence and credibility --------------------------------------
    dict(text="It's not enough to talk about deterrence: I believe we must demonstrate "
              "that we can deliver air power to degrade, disrupt, destroy, and defeat.",
         who="Air Marshal Stephen Chappell, Chief of Air Force, RAAF", year=2026,
         theme="deterrence", kind="named",
         source="Chief of Air Force address, March 2026 (defence.gov.au)"),
    dict(text="Simply stated, strategic deterrence is about communicating capability and "
              "intent.",
         who="Adm. Cecil D. Haney, Commander, US Strategic Command", year=None,
         theme="deterrence", kind="named",
         source="USSTRATCOM commander's remarks (stratcom.mil)"),
    dict(text="Saying so, unfortunately, does not make it true; and if true, saying so "
              "does not always make it believed.",
         who="Thomas C. Schelling", year=None,
         theme="credibility", kind="named",
         source="Arms and Influence; quoted by National Defense University, 2025"),
    dict(text="Stability is not a passive state of affairs - it's achieved through "
              "strength and active diplomacy.",
         who="Air Marshal Robert Chipman, Chief of Air Force, RAAF", year=2023,
         theme="deterrence", kind="named",
         source="Chief of Air Force address, 2023 (defence.gov.au)"),
    dict(text="Readiness is critical to an effective deterrence, not only in Air Force, "
              "but across all domains.",
         who="Air Vice-Marshal Harvey Reynolds, Deputy Chief of Air Force, RAAF", year=None,
         theme="readiness", kind="named",
         source="Deputy Chief of Air Force remarks (defence.gov.au)"),
    dict(text="If deterrence fails, we'll provide a decisive response. Decisive in every "
              "way that word means.",
         who="Gen. John E. Hyten, Commander, US Strategic Command", year=2018,
         theme="deterrence", kind="named",
         source="USSTRATCOM commander's remarks, 2018 (stratcom.mil)"),
    dict(text="An attack on one is an attack on all.",
         who="NATO Ankara Summit Declaration", year=2026,
         theme="coalition", kind="institution",
         source="NATO Heads of State and Government, Ankara, July 2026 (nato.int)"),
    # --- readiness, training, adaptation ---------------------------------
    dict(text="Readiness is our first responsibility.",
         who="Gen. Kenneth S. Wilsbach, Chief of Staff, US Air Force", year=2025,
         theme="readiness", kind="named",
         source="First letter to the force, December 2025 (af.mil)"),
    dict(text="We are not training for our best day out. We are training for our worst "
              "day and then the next day and the day after.",
         who="Wing Commander Tim Hurford, RAAF", year=2026,
         theme="readiness", kind="named",
         source="RAAF Aviator Symposium, March 2026 (defence.gov.au)"),
    dict(text="This is so we can fight not just the way we want to, but the way we have to.",
         who="Air Vice-Marshal Glen Braz, Air Commander Australia", year=2026,
         theme="readiness", kind="named",
         source="On RAAF fighting depth, March 2026 (defence.gov.au)"),
    dict(text="Combat is unforgiving, and victory belongs to the side that adapts faster, "
              "fights harder, and endures longer.",
         who="Gen. Eric M. Smith, Commandant of the Marine Corps", year=2025,
         theme="adaptation", kind="named",
         source="Force Design update, 2025 (marines.mil)"),
    dict(text="If we fail to adapt, fail to innovate, fail to develop and grow, we will "
              "find ourselves forever reacting and struggling.",
         who="Gen. Anthony Zinni, US Marine Corps", year=None,
         theme="adaptation", kind="named",
         source="Reproduced in the US Marine Corps' official modernization history"),
    dict(text="Train, train, train, and train some more.",
         who="Gen. Leon E. Salomon, US Army", year=None,
         theme="readiness", kind="named",
         source="US Army leadership collection (army.mil)"),
    dict(text="Plans are worthless, but planning is everything.",
         who="Dwight D. Eisenhower", year=1957,
         theme="planning", kind="named",
         source="Eisenhower Presidential Library, remarks of 14 November 1957"),
    dict(text="Under pressure, you don't rise to the occasion - you sink to the level of "
              "your training.",
         who="military training maxim, speaker unknown; often called a SEAL saying",
         year=None, theme="readiness", kind="maxim",
         source="No original speaker, unit or dated source found; not Archilochus"),
    dict(text="The more you sweat in training, the less you bleed in battle.",
         who="traditional training maxim",
         year=None, theme="readiness", kind="maxim",
         source="'Sweat in peace, bleed in war' is recorded from 1939; the training "
                "wording came later"),
    # --- logistics, sustainment, industry --------------------------------
    dict(text="An understanding of both pure logistics and the broad aspects of applied "
              "logistics is essential to the exercise of high command.",
         who="Rear Adm. Henry E. Eccles, US Navy", year=1959,
         theme="logistics", kind="named",
         source="Logistics in the National Defense"),
    dict(text="During deployment, it is too late to practice battlefield sustainment "
              "skills.",
         who="Gen. Gustave F. Perna, US Army Materiel Command", year=2019,
         theme="logistics", kind="named",
         source="Army Sustainment, 2019 (army.mil)"),
    dict(text="Our stockpiles need to be replenished. And we need this to happen fast.",
         who="Radmila Shekerinska, NATO Deputy Secretary General", year=2026,
         theme="logistics", kind="named",
         source="Ankara Dialogues, July 2026 (nato.int)"),
    dict(text="There is no strong defence without a strong defence industry.",
         who="Mark Rutte, NATO Secretary General", year=2026,
         theme="industry", kind="named",
         source="NATO Summit Defence Industry Forum, 2026 (nato.int)"),
    dict(text="'Better' is the enemy of 'good enough'.",
         who="Soviet naval maxim, reportedly displayed in Adm. Sergey Gorshkov's office",
         year=None, theme="planning", kind="maxim",
         source="The office motto is reported; Gorshkov did not originate the saying"),
    # --- coalition ---------------------------------------------------------
    dict(text="United we fought and united we prevail.",
         who="Fleet Adm. Chester W. Nimitz", year=1945,
         theme="coalition", kind="named",
         source="Message to the Pacific Fleet, 2 September 1945 (history.navy.mil)"),
]


def attribution(q):
    """`Gen. Kenneth S. Wilsbach, Chief of Staff, US Air Force, 2025`, or the
    maxim's honest label with no year."""
    return q["who"] + (f", {q['year']}" if q.get("year") else "")


def tip_line(q):
    """The quote as one loading-screen tip value: `<text> - <attribution>`,
    one line, no '=', and no quotation mark at either end. The game's ini
    reader takes quotes at a value's ends as delimiters (vanilla writes
    Key="text " to keep a trailing space), so a value opening on one could
    lose everything after its closing quote - the attribution. The panel's
    QUOTATION header does the quotation marks' work."""
    line = f'{q["text"]} - {attribution(q)}'
    if "=" in line or "\n" in line or line[0] == '"' or line[-1] == '"':
        raise ValueError(f"quote cannot be a tip value: {line[:60]}")
    return line


def by_theme(theme):
    return [q for q in QUOTES if q["theme"] == theme]


def plan_epigraphs(roles):
    """One quote per mission, roles in campaign order -> list of quotes.

    A mission takes the first quote not yet used in this campaign from the
    themes its role reaches for, in order; when every candidate is spent it
    takes any unused quote, and only a campaign longer than the set repeats
    one. The result depends on nothing but the roles, so a rebuild on any
    machine sets the same line under the same banner.
    """
    used, out = set(), []
    for role in roles:
        themes = ROLE_THEMES.get(role, ROLE_THEMES["escort"])
        pool = [q for t in themes for q in by_theme(t)]
        pool += [q for q in QUOTES if q not in pool]
        pick = next((q for q in pool if id(q) not in used), pool[0])
        used.add(id(pick))
        out.append(pick)
    return out


def check():
    """The invariants every reader relies on."""
    for q in QUOTES:
        for key in ("text", "who", "theme", "kind", "source"):
            if not q.get(key):
                raise ValueError(f"quote missing {key}: {q}")
        if q["kind"] not in ("named", "institution", "maxim"):
            raise ValueError(f"unknown kind {q['kind']!r}: {q['text'][:40]}")
        if any(ord(ch) > 126 for ch in q["text"] + q["who"]):
            raise ValueError(f"quote is not ASCII: {q['text'][:40]}")
        tip_line(q)
    if len({q["text"] for q in QUOTES}) != len(QUOTES):
        raise ValueError("duplicate quote text")
    for role, themes in ROLE_THEMES.items():
        for t in themes:
            if not by_theme(t):
                raise ValueError(f"role {role}: no quote carries theme {t!r}")
    return len(QUOTES)


if __name__ == "__main__":
    print(f"{check()} quotes")
    for q in QUOTES:
        print(" ", tip_line(q))
