"""Native, fictional SEST service ribbons; no native save editing.

Mission completion is the only claim made by these awards. Performance
commendations need their own recorded evidence and are not inferred from cost.
"""
from pathlib import Path
import re

CAMPAIGNS = {
    "sest-southern-watch": ("southern_watch_service", "Southern Watch Service Ribbon", "Southern Watch", ("#123A58", "#DCE6E8", "#317E8C", "#D9B65B", "#317E8C", "#DCE6E8", "#123A58")),
    "sest-southern-reach": ("southern_reach_service", "Southern Reach Service Ribbon", "Southern Reach / Tasman Shield", ("#243B65", "#E1E8EF", "#87B4CE", "#E1E8EF", "#243B65")),
    "sest-red-line": ("red_line_service", "Red Line Service Ribbon", "Red Line", ("#2A3244", "#B94A48", "#D8BD6D", "#B94A48", "#2A3244")),
    "sest-sulu-line": ("sulu_line_service", "Sulu Line Service Ribbon", "Sulu Line", ("#164B4D", "#E5D7A6", "#405D86", "#E5D7A6", "#164B4D")),
}


def base_slug(slug):
    return slug.removesuffix("-open")


def award_id(slug):
    row = CAMPAIGNS.get(base_slug(slug))
    return "sest_" + row[0] if row else None


def commander_settings(text, slug):
    """Append our definitions while retaining every pre-existing ribbon ID."""
    slug = base_slug(slug)
    if slug not in CAMPAIGNS:
        return text
    short, name, operation, colours = CAMPAIGNS[slug]
    rid = "sest_" + short
    section = re.search(r"(?ms)^\[TaskForceRibbons\]\s*\n(.*?)(?=^\[|\Z)", text)
    if section:
        body = section.group(1)
        existing = re.search(r"(?m)^RibbonIds\s*=\s*(.*)$", body)
        ids = [i.strip() for i in existing.group(1).split(",") if i.strip()] if existing else []
        if rid not in ids:
            ids.append(rid)
        replacement = "RibbonIds=" + ",".join(ids)
        body = re.sub(r"(?m)^RibbonIds\s*=.*$", replacement, body) if existing else body + replacement + "\n"
        text = text[:section.start(1)] + body + text[section.end(1):]
    else:
        text = text.rstrip() + "\n\n[TaskForceRibbons]\nRibbonIds=" + rid + "\n"
    if re.search(rf"(?m)^\[Ribbon_{re.escape(rid)}\]$", text):
        return text
    return text.rstrip() + f"""

[Ribbon_{rid}]
Type=CampaignAward
Precedence=120
Name_en={name}
ImagePath=campaigns/{slug}/art/ribbons/{rid}.png
StripeColors={'|'.join(colours)}
StripeWidths={'|'.join(['20'] * len(colours))}
CitationIssuingBody_en=Joint Maritime Campaign Headquarters
CitationIssuance_en=Joint Maritime Campaign Headquarters awards the
CitationAwardName_en={name}
CitationAuthority_en=To
CitationRecipient_en={{CommanderRank}} {{CommanderName}}
CitationText_en=For completing command service during {operation} as commander of {{TaskForceName}}. This fictional campaign service award records completion of the operation; it does not certify an unrecorded performance condition.
CitationSignatureName_en=Campaign Operations Staff
CitationSignatureTitle_en=Joint Maritime Campaign Headquarters
ReferenceSource=Fictional
"""


def render(campaign_directory, slug):
    """Create original, code-drawn ribbon artwork from the declared stripes."""
    from PIL import Image, ImageDraw
    slug = base_slug(slug)
    row = CAMPAIGNS.get(slug)
    if not row:
        return
    path = Path(campaign_directory) / "art" / "ribbons" / (award_id(slug) + ".png")
    path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGBA", (140, 36), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    colours = row[3]
    for index, colour in enumerate(colours):
        left = round(2 + 136 * index / len(colours))
        right = round(2 + 136 * (index + 1) / len(colours))
        draw.rectangle((left, 3, right, 32), fill=colour)
    draw.rectangle((1, 2, 138, 33), outline="#B0B4B8", width=1)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    stitches = ImageDraw.Draw(overlay)
    for y in range(5, 32, 3):
        stitches.line((3, y, 136, y), fill=(255, 255, 255, 22))
    image = Image.alpha_composite(image, overlay)
    image.save(path)


def final_mission_awards(campaign_text, slug):
    """Apply to a serialized spine only when integrating a preserved pack."""
    rid = award_id(slug)
    if not rid:
        return campaign_text
    sections = list(re.finditer(r"(?ms)^\[Mission\d+\][^\n]*\n(.*?)(?=^\[|\Z)", campaign_text))
    for section in reversed(sections):
        body = section.group(1)
        if "TaskForceModeFinalMission=True" not in body:
            continue
        match = re.search(r"(?m)^TaskForceModeRibbonAwards=(.*)$", body)
        ids = [x.strip() for x in match.group(1).split(",") if x.strip()] if match else []
        if rid not in ids:
            ids.append(rid)
        line = "TaskForceModeRibbonAwards=" + ",".join(ids)
        body = re.sub(r"(?m)^TaskForceModeRibbonAwards=.*$", line, body) if match else body.rstrip() + "\n" + line + "\n"
        return campaign_text[:section.start(1)] + body + campaign_text[section.end(1):]
    raise ValueError("Campaign has no explicit native final mission: " + slug)
