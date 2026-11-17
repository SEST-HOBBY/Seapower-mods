"""Sea Power mission INI weather patching (ENV-01 Weather Lab, ENV-06 mission adapter). BUILD-TESTED.

Only native keys observed in shipped Sea Power files are written:
- [Environment] SeaState (0-12), Clouds (the eight clouds.ini sections), WindDirection
  (N..NW), Weather (Rain, Snow, Fog, Thunderstorm) - documented in the vanilla
  missions/Demo/MissionFileInformation.ini;
- trigger actions Action_SetClouds, Action_SetSeaState, Action_SetRain, Action_SetFog,
  Action_SetThunderstorm, Action_SetWindDirection - each found in vanilla 0.9.2 campaign
  missions. Action_SetSnow appears in NO shipped file, so this module never writes it.

Safety rules (each enforced, each tested):
1. The source text is never modified; the result is a new string.
2. Original triggers are never renumbered or removed. New triggers are appended after the
   highest of NumberOfTriggers and the highest [TriggerN], and NumberOfTriggers is raised
   by exactly the number appended.
3. A weather-only original trigger is set Disabled=True. If another trigger can enable or
   reactivate it (Action_EnableTriggers / Action_ReactivateTriggers), or uses it as a
   mission-timer source, disabling is not stable: the patch refuses unless the caller opts
   in to stripping its weather actions instead.
4. In a trigger that mixes weather with other actions, only the weather action lines are
   removed; every other line stays byte for byte.
5. The patch refuses: duplicate [TriggerN] ids, NumberOfTriggers missing or repeated, or
   NumberOfTriggers below the highest [TriggerN] (raising it would wake sections the game
   currently ignores).
6. Line endings and a UTF-8 BOM are preserved; [Environment] ends with exactly one Clouds
   and SeaState line and at most one Weather line.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

CLOUDS = ("Clear", "Scattered", "Scattered_1", "Scattered_2", "Broken", "Broken_2", "Broken_3", "Overcast")
WIND_DIRECTIONS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
WEATHER_WORDS = ("Rain", "Snow", "Fog", "Thunderstorm")
WEATHER_ACTIONS = ("Action_SetClouds", "Action_SetSeaState", "Action_SetRain", "Action_SetFog",
                   "Action_SetSnow", "Action_SetThunderstorm", "Action_SetWindDirection")
WEATHER_COMPANIONS = ("Action_Forecast",)  # forecast text that only announces a weather change
NEVER_WRITE = ("Action_SetSnow",)  # not observed in any shipped mission

SECTION_RE = re.compile(r"(?m)^\[([^\]\r\n]+)\][^\r\n]*")
TRIGGER_RE = re.compile(r"^Trigger(\d+)$")
ACTION_RE = re.compile(r"(?m)^[ \t]*(Action_\w+)[ \t]*=")
REF_RE = re.compile(r"(?m)^[ \t]*(Action_EnableTriggers|Action_ReactivateTriggers|Action_DisableTriggers|Action_MissionTimerSourceTrigger)[ \t]*=([^\r\n]*)")


class PatchRefused(ValueError):
    """The source cannot be patched without risking its mission logic."""


@dataclass(frozen=True)
class WeatherState:
    clouds: str
    sea_state: int
    rain: bool = False
    fog: bool = False
    thunderstorm: bool = False
    snow: bool = False  # initial [Environment] Weather only; never as a trigger action
    wind: str | None = None

    def check(self, *, initial: bool) -> None:
        if self.clouds not in CLOUDS:
            raise ValueError(f"Clouds {self.clouds!r} not one of {CLOUDS}")
        if not (isinstance(self.sea_state, int) and 0 <= self.sea_state <= 12):
            raise ValueError("SeaState must be an integer 0..12")
        if self.thunderstorm and self.clouds != "Overcast":
            raise ValueError("Thunderstorm is visible with Overcast clouds only (MissionFileInformation.ini)")
        if self.wind is not None and self.wind not in WIND_DIRECTIONS:
            raise ValueError(f"WindDirection {self.wind!r} not one of {WIND_DIRECTIONS}")
        if self.snow and not initial:
            raise ValueError("snow can start a mission (Weather=Snow) but no observed trigger action changes it")

    def weather_value(self) -> str:
        return ",".join(w for w, on in (("Rain", self.rain), ("Snow", self.snow), ("Fog", self.fog), ("Thunderstorm", self.thunderstorm)) if on)

    def actions(self) -> list[str]:
        out = [f"Action_SetClouds={self.clouds}", f"Action_SetSeaState={self.sea_state}"]
        if self.wind:
            out.append(f"Action_SetWindDirection={self.wind}")
        out += [f"Action_SetRain={self.rain}", f"Action_SetFog={self.fog}", f"Action_SetThunderstorm={self.thunderstorm}"]
        return out


@dataclass
class Section:
    name: str
    start: int
    end: int

    @property
    def trigger_id(self) -> int | None:
        m = TRIGGER_RE.match(self.name)
        return int(m.group(1)) if m else None


@dataclass
class PatchReport:
    source_triggers: int = 0
    number_of_triggers_before: int = 0
    number_of_triggers_after: int = 0
    appended: list = field(default_factory=list)
    disabled_weather_only: list = field(default_factory=list)
    already_disabled_weather_only: list = field(default_factory=list)
    stripped_mixed: dict = field(default_factory=dict)
    stripped_referenced: list = field(default_factory=list)
    environment_removed_lines: list = field(default_factory=list)
    renamed_languages: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    newline: str = "\n"
    bom: bool = False
    trigger_style: str = "legacy"
    mixed_newlines: bool = False


def sections(text: str) -> list[Section]:
    marks = list(SECTION_RE.finditer(text))
    out = []
    for k, m in enumerate(marks):
        end = marks[k + 1].start() if k + 1 < len(marks) else len(text)
        out.append(Section(m.group(1).strip(), m.start(), end))
    return out


def _actions(block: str) -> list[str]:
    return ACTION_RE.findall(block)


def is_weather_only(block: str) -> bool:
    acts = _actions(block)
    return bool(acts) and all(a in WEATHER_ACTIONS or a in WEATHER_COMPANIONS for a in acts) and any(a in WEATHER_ACTIONS for a in acts)


def has_weather(block: str) -> bool:
    return any(a in WEATHER_ACTIONS for a in _actions(block))


def references(text: str) -> dict[int, set[str]]:
    """Trigger id -> set of reference kinds (Enable, Reactivate, Disable, Timer)."""
    refs: dict[int, set[str]] = {}
    kinds = {"Action_EnableTriggers": "Enable", "Action_ReactivateTriggers": "Reactivate",
             "Action_DisableTriggers": "Disable", "Action_MissionTimerSourceTrigger": "Timer"}
    for key, value in REF_RE.findall(text):
        value = value.split("//")[0]
        for tok in re.findall(r"\bTrigger(\d+)\b", value):
            refs.setdefault(int(tok), set()).add(kinds[key])
    return refs


def _disable(block: str, nl: str) -> str:
    if re.search(r"(?mi)^[ \t]*Disabled[ \t]*=", block):
        return re.sub(r"(?mi)^([ \t]*Disabled[ \t]*=)[^\r\n]*", r"\1True", block)
    head_end = block.find("\n") + 1 if "\n" in block else len(block)
    if head_end == len(block) and not block.endswith("\n"):
        return block + nl + "Disabled=True" + nl
    return block[:head_end] + "Disabled=True" + nl + block[head_end:]


def _strip_weather_lines(block: str) -> tuple[str, list[str]]:
    removed = []
    keep = []
    for line in block.splitlines(keepends=True):
        m = re.match(r"[ \t]*(Action_\w+)[ \t]*=", line)
        if m and m.group(1) in WEATHER_ACTIONS:
            removed.append(line.rstrip("\r\n"))
        else:
            keep.append(line)
    return "".join(keep), removed


def _set_environment(block: str, state: WeatherState, nl: str, report: PatchReport) -> str:
    lines = block.splitlines(keepends=True)
    header, body = lines[0], lines[1:]
    kept = []
    for line in body:
        m = re.match(r"[ \t]*(Clouds|SeaState|Weather|WindDirection)[ \t]*=", line)
        if m and (m.group(1) != "WindDirection" or state.wind):
            report.environment_removed_lines.append(line.rstrip("\r\n"))
            continue
        kept.append(line)
    trailing = []
    while kept and kept[-1].strip() == "":
        trailing.insert(0, kept.pop())
    if kept and not kept[-1].endswith(("\n", "\r")):
        kept[-1] += nl
    new = [f"SeaState={state.sea_state}{nl}", f"Clouds={state.clouds}{nl}"]
    if state.wind:
        new.append(f"WindDirection={state.wind}{nl}")
    if state.weather_value():
        new.append(f"Weather={state.weather_value()}{nl}")
    if not trailing:
        trailing = [nl]
    return header + "".join(kept) + "".join(new) + "".join(trailing)


def _rename_language(block: str, prefix: str, en_description: str | None) -> str:
    def name_sub(m):
        return f"{m.group(1)}{prefix}{m.group(2)}"
    block = re.sub(r"(?m)^(Name=)(?!" + re.escape(prefix) + r")([^\r\n]*)", name_sub, block, count=1)
    if en_description is not None:
        block = re.sub(r"(?m)^Description=[^\r\n]*", lambda m: "Description=" + en_description, block, count=1)
    return block


def patch(source: str, stages: list[WeatherState], *, interval_s: int = 300, first_at_s: int | None = None,
          title_prefix: str = "MNO Weather Lab: ", en_description: str | None = None,
          referenced_weather: str = "refuse", stage_label: str = "MNO ENV stage",
          times: list[int] | None = None, mission_time: tuple[int, int] | None = None) -> tuple[str, PatchReport]:
    """Return (new_text, report). stages[0] is the starting weather; stages[1:] fire at
    first_at_s + (k-1)*interval_s seconds of mission time (first_at_s defaults to interval_s),
    or at the explicit, strictly increasing `times` (one per stage after the first)."""
    if referenced_weather not in ("refuse", "strip"):
        raise ValueError("referenced_weather must be 'refuse' or 'strip'")
    if not stages:
        raise ValueError("at least the starting state is required")
    if interval_s < 30:
        raise ValueError("interval below 30 s is not a useful test")
    for k, s in enumerate(stages):
        s.check(initial=(k == 0))
    if times is not None:
        if len(times) != len(stages) - 1 or any(t <= 0 for t in times) or any(b <= a for a, b in zip(times, times[1:])):
            raise ValueError("times must be positive, strictly increasing, one per stage after the first")
    report = PatchReport()
    report.bom = source.startswith("﻿")
    text = source[1:] if report.bom else source
    report.newline = nl = "\r\n" if "\r\n" in text else "\n"
    if nl == "\r\n" and "\n" in text.replace("\r\n", ""):
        report.mixed_newlines = True
        report.warnings.append("source already mixes CRLF and LF; new lines use CRLF, existing lines are kept as they are")
    secs = sections(text)
    names = [s.name for s in secs]
    for required in ("Environment", "Mission"):
        if names.count(required) != 1:
            raise PatchRefused(f"expected exactly one [{required}] section, found {names.count(required)}")
    n_matches = list(re.finditer(r"(?m)^[ \t]*NumberOfTriggers[ \t]*=[ \t]*(\d+)", text))
    if len(n_matches) != 1:
        raise PatchRefused(f"expected one NumberOfTriggers line, found {len(n_matches)}")
    n_before = int(n_matches[0].group(1))
    trig = [s for s in secs if s.trigger_id is not None]
    ids = [s.trigger_id for s in trig]
    if len(ids) != len(set(ids)):
        dup = sorted({i for i in ids if ids.count(i) > 1})
        raise PatchRefused(f"duplicate trigger sections {dup}; the game would read only one of each")
    max_id = max(ids) if ids else 0
    if n_before < max_id:
        raise PatchRefused(f"NumberOfTriggers={n_before} is below [Trigger{max_id}]; raising it would activate sections the game ignores today")
    report.source_triggers, report.number_of_triggers_before = len(trig), n_before
    report.trigger_style = "legacy" if re.search(r"(?m)^Condition_Type[ \t]*=", text) or not re.search(r"(?m)^ConditionsCompleted=", text) else "conditions"
    refs = references(text)

    # Rebuild the text section by section so untouched bytes stay identical.
    out = [text[: secs[0].start]] if secs else [text]
    for s in secs:
        block = text[s.start:s.end]
        tid = s.trigger_id
        if s.name == "Environment":
            block = _set_environment(block, stages[0], nl, report)
            if mission_time is not None:
                hh, mm = mission_time
                if not (0 <= hh <= 23 and 0 <= mm <= 59):
                    raise ValueError("mission_time must be (hour 0-23, minute 0-59)")
                if not re.search(r"(?m)^Time=", block):
                    raise PatchRefused("[Environment] has no Time line to change")
                block = re.sub(r"(?m)^Time=[^\r\n]*", f"Time={hh},{mm}", block, count=1)
        elif s.name.startswith("Language_"):
            lang = s.name[len("Language_"):]
            block = _rename_language(block, title_prefix, en_description if lang == "en" else None)
            report.renamed_languages.append(lang)
        elif tid is not None and tid <= n_before and has_weather(block):
            kinds = refs.get(tid, set())
            if is_weather_only(block):
                dangerous = kinds & {"Enable", "Reactivate", "Timer"}
                if dangerous:
                    if referenced_weather == "refuse":
                        raise PatchRefused(f"[Trigger{tid}] is weather-only and other triggers can {sorted(dangerous)} it; "
                                           "disabling it would not hold. Re-run with referenced_weather='strip' to remove its "
                                           "weather actions instead (the trigger stays, with no weather effect).")
                    block, removed = _strip_weather_lines(block)
                    report.stripped_referenced.append(tid)
                    report.stripped_mixed[tid] = removed
                elif re.search(r"(?mi)^[ \t]*Disabled[ \t]*=[ \t]*True", block):
                    report.already_disabled_weather_only.append(tid)
                else:
                    block = _disable(block, nl)
                    report.disabled_weather_only.append(tid)
            else:
                block, removed = _strip_weather_lines(block)
                report.stripped_mixed[tid] = removed
        out.append(block)
    body = "".join(out)
    if not body.endswith(nl):
        body += nl
    first = interval_s if first_at_s is None else first_at_s
    base = max(n_before, max_id)
    added = []
    for k, st in enumerate(stages[1:], start=1):
        tid = base + k
        t = times[k - 1] if times is not None else first + (k - 1) * interval_s
        lines = [f"[Trigger{tid}]  # {stage_label} {k}", f"Name={stage_label} {k}"]
        if report.trigger_style == "conditions":
            lines += ["Condition_Condition1_Type=Time", f"Condition_Condition1_Time={t}", "ConditionsCompleted=<Condition1>"]
        else:
            lines += ["Condition_Type=Time", f"Condition_Time={t}"]
        lines += st.actions()
        added.append(nl.join(lines) + nl)
        report.appended.append({"trigger": tid, "time_s": t, "state": st.__dict__.copy()})
    if added:
        body = body.rstrip("\r\n") + nl + nl + nl.join(added)
    n_after = base + len(added) if added else n_before
    body = re.sub(r"(?m)^([ \t]*NumberOfTriggers[ \t]*=[ \t]*)\d+", lambda m: m.group(1) + str(n_after), body, count=1)
    report.number_of_triggers_after = n_after
    if report.stripped_referenced:
        report.warnings.append("weather stripped from triggers other triggers can re-enable: "
                               + ", ".join(f"Trigger{t}" for t in report.stripped_referenced))
    result = ("﻿" if report.bom else "") + body
    verify(source, result, report)
    return result, report


def verify(source: str, result: str, report: PatchReport) -> None:
    """Independent re-check of the output; raises AssertionError on any rule break."""
    text = result.lstrip("﻿")
    secs = sections(text)
    ids = [s.trigger_id for s in secs if s.trigger_id is not None]
    assert len(ids) == len(set(ids)), "duplicate trigger ids in output"
    n = [int(x) for x in re.findall(r"(?m)^[ \t]*NumberOfTriggers[ \t]*=[ \t]*(\d+)", text)]
    assert n == [report.number_of_triggers_after], "NumberOfTriggers not updated exactly once"
    assert max(ids or [0]) <= n[0], "a trigger section lies beyond NumberOfTriggers"
    env = next(s for s in secs if s.name == "Environment")
    eb = text[env.start:env.end]
    assert len(re.findall(r"(?m)^Clouds=", eb)) == 1 and len(re.findall(r"(?m)^SeaState=", eb)) == 1, "Environment Clouds/SeaState not unique"
    assert len(re.findall(r"(?m)^Weather=", eb)) <= 1, "Environment Weather duplicated"
    assert text.count("Action_SetSnow") <= source.count("Action_SetSnow"), "wrote unobserved Action_SetSnow"
    if report.newline == "\r\n" and not report.mixed_newlines:
        assert "\n" not in text.replace("\r\n", ""), "mixed line endings"
    # Every original trigger id is still present with its header line unchanged.
    src_secs = {s.trigger_id: source.lstrip("﻿")[s.start:s.end].splitlines()[0] for s in sections(source.lstrip("﻿")) if s.trigger_id is not None}
    out_secs = {s.trigger_id: text[s.start:s.end].splitlines()[0] for s in secs if s.trigger_id is not None}
    for tid, head in src_secs.items():
        assert out_secs.get(tid) == head, f"Trigger{tid} header changed or missing"
    # Non-weather lines of every original trigger survive in order.
    src_text = source.lstrip("﻿")
    for s in sections(src_text):
        if s.trigger_id is None:
            continue
        src_lines = [ln for ln in src_text[s.start:s.end].splitlines()
                     if not re.match(r"[ \t]*(" + "|".join(WEATHER_ACTIONS) + r")[ \t]*=", ln) and not re.match(r"(?i)[ \t]*Disabled[ \t]*=", ln)]
        o = next(x for x in secs if x.trigger_id == s.trigger_id)
        out_lines = [ln for ln in text[o.start:o.end].splitlines() if not re.match(r"(?i)[ \t]*Disabled[ \t]*=", ln)]
        it = iter(out_lines)
        assert all(any(ln == x for x in it) for ln in src_lines), f"Trigger{s.trigger_id} lost a non-weather line"


def read_mission_bytes(data: bytes) -> str:
    """Decode a mission file strictly as UTF-8 (BOM kept as U+FEFF). Refuses other encodings
    rather than guessing, because a wrong guess would corrupt every non-ASCII language key."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise PatchRefused(f"mission is not UTF-8 ({exc.reason} at byte {exc.start}); convert it deliberately first") from None


def write_mission_text(text: str) -> bytes:
    return text.encode("utf-8")
