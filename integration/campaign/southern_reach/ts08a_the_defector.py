"""TS08A - The Defector. Optional Bight escort, 17 February 2029.

A fresh implementation of the paused session's visible defector-escort
brief, not recovered output from its failed design synthesis. The fictional
mutiny is on a support vessel: no prize destroyer, automatic asylum decision
or persistent fleet grant. Handover uses the stock side-transfer action.
"""
from campaign_data import U, F, S, HELO, RECON

MISSION = dict(
    code="TS08A", series="Tasman Shield", seq="TASMAN SHIELD  ·  OPTIONAL",
    group="optional", num="08A", key="The Defector",
    place="The eastern Great Australian Bight",
    intro="A bridge party aboard a Russian support vessel requests protection. "
          "Meet her before the recovery escort closes, then bring her out.",
    special="Optional diversion after the Bight search. The request closes when "
            "The Southern Convoy is complete. No repair, rearm or new allocation "
            "is available; the convoy's support window remains available if you skip this.",
    sender="Commodore Alex Mercer, Joint Maritime Command",
    intent="SEVERNY VETER's bridge party says it has refused orders and confined "
           "the detachment's security officer. We have a voice transmission, "
           "not independent confirmation of its account. Bring your flagship "
           "within two miles of the stopped vessel to accept navigational "
           "control, then escort her to the marked handover area. Her people "
           "and their records are the reason for going. Protect them; their "
           "claims will be examined ashore.",
    date=(2029, 2, 17), time=(6, 20), sea=3, clouds="Broken_2", wind="SW",
    difficulty=3, minutes=95, centre=(-35.60, 134.30),
    blue_nation="Australia", red_nation="Russia",
    brief=(
        "EASTERN GREAT AUSTRALIAN BIGHT, first light. RV SEVERNY VETER, a "
        "support vessel attached to the Russian research detachment, has "
        "stopped southwest of your force. Her chief mate reports that a "
        "bridge party has refused orders to return to the detachment and "
        "requests Australian protection. Some of the crew opposed the move. "
        "The account has not been independently verified.\\n\\n"
        "SEVERNY VETER remains plotted on the opposing side. Hold fire on "
        "her. Take YOUR FLAGSHIP into the two-mile rendezvous around her "
        "reported position. On contact she will accept your navigational "
        "control. Then give her a course and speed: she is stopped and will "
        "not sail herself to safety. Bring both her and your flagship into "
        "the marked handover area to the northeast within 95 minutes. "
        "A helicopter overflight does not complete the rendezvous.\\n\\n"
        "A separate Udaloy-class recovery escort is closing from the "
        "southwest with a Ka-27 searching ahead. Its intercepted orders "
        "authorise force against a foreign escort intervening. Defend your "
        "ships and the people asking for protection. Sinking the pursuer "
        "does not complete the escort task. Two Port Lincoln fishing boats "
        "and a westbound merchant are crossing the sector; harm none of "
        "them. The Seahawk and Edinburgh's patrol aircraft are available "
        "if assigned.\\n\\n"
        "This diversion offers no stores or repairs. The convoy still sails "
        "on the nineteenth. Your task is safe passage; the decision on the "
        "crew's request belongs ashore."
    ),
    forces="Your task group, with its Seahawk and a patrol aircraft from "
           "Edinburgh if assigned. Requesting protection: RV Severny Veter. "
           "Opposing: one Udaloy-class recovery escort and its Ka-27. "
           "Neutral: two fishing boats and a westbound merchant.",
    objectives=[
        ("Passage", "Accept Severny Veter's handover, then bring her and your "
                    "flagship into the handover area", "40,-40,Fail,Main"),
        ("Traffic", "Harm no fishing boat or merchant", "0,-30,Complete"),
        ("Flagship", "Bring your flagship out intact", "10,-20,Complete"),
    ],
    victory=dict(
        kind="arrive", station="defector", min_units=1, objective="Passage",
        at=(-35.58, 134.45), radius=4,
        also=[dict(units=["escort"], min_units=1)],
        after=dict(
            kind="area", units="escort", at_unit="defector", radius=2,
            min_units=1, transfer_to_player="defector",
            intel="Severny Veter has accepted your navigational control. "
                  "She is stopped. Set her course and speed and escort her "
                  "northeast. Both she and your flagship must reach the "
                  "marked handover area before the window closes."
        ),
    ),
    fatal=[F("Passage", ["defector"]), F("Flagship", ["escort"])],
    neutral_objective="Traffic",
    win="Severny Veter and your flagship have reached the handover area. "
        "The ship's people and records can now be received by the relief "
        "organisation. Their account remains to be examined. Mercer: "
        "'You brought them out. We will deal with the questions ashore.'",
    lose="The protection operation has failed. Preserve the engagement "
         "record and report the loss; the convoy task remains ahead.",
    timeout="The handover window has closed without both Severny Veter "
            "and your flagship in the marked area after the rendezvous. "
            "Safe passage has not been established.",
    stations={
        "escort": S(-35.57, 134.32, "Flagship", heading=220),
        "flight": S(-35.58, 134.32, "Ship's flight", heading=220, alt=500),
        "mpa": S(-35.47, 134.20, "Maritime patrol", heading=240, alt=10000),
        "defector": S(-35.72, 134.15, "Severny Veter rendezvous", heading=55),
        "pursuer": S(-36.12, 133.60, "Recovery escort", heading=50),
        "red_helo": S(-35.97, 133.72, "Recovery escort's Ka-27", heading=50, alt=1500),
        "fish1": S(-35.70, 134.43, "Fishing boat", heading=45),
        "fish2": S(-35.33, 134.10, "Fishing boat", heading=135),
        "merchant": S(-35.85, 134.55, "Westbound merchant", heading=270),
        "home": S(-34.703, 138.622, "RAAF Base Edinburgh"),
    },
    units=[
        U("blue", "SEST_RAN_Fleet", "ran_ffh_anzac", "escort",
          variant="Variant7", weapons="Tight", extra=dict(Telegraph="0")),
        U("blue", "us-navy-2027", "usn_mh-60r", "flight",
          alt=500, slot="HeloRecon", weapons="Tight"),
        U("blue", "p-8-poseidon", "usn_p8", "mpa", squadron="Squadron3",
          alt=10000, loadout="ASW", slot="Recon", weapons="Tight"),
        # Fixed until the rendezvous: at_unit is a fixed area, not a moving
        # proximity predicate. No JoinTaskForce/CampaignTag is emitted.
        U("red", "_vanilla", "civ_ms_kommunist", "defector",
          name="RV Severny Veter", weapons="Hold", extra=dict(Telegraph="0")),
        # A separate escort, not TS08's named Udaloy (which the player may
        # have sunk). Its stock SS-N-14B reaches 27 NM; the Ka-27's
        # sonobuoy range is not an anti-ship weapon's engagement range.
        U("red", "_vanilla", "wp_bpk_udaloy", "pursuer",
          name="Recovery escort", weapons="Free",
          route=[(-35.72, 134.15, 0), (-35.58, 134.45, 0)], telegraph=4),
        U("red", "_vanilla", "wp_ka-27", "red_helo", name="Recovery escort's Ka-27",
          alt=1500, loadout="ASW", weapons="Hold",
          route=[(-35.80, 134.10, 1500), (-35.60, 134.40, 1500)], loop=True),
        U("neutral", "_vanilla", "civ_fv_fishingboat_a", "fish1",
          name="Fishing boat Coffin Bay", weapons="Hold",
          route=[(-35.25, 135.00, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_fv_fishingboat_b", "fish2",
          name="Fishing boat Cape Wiles", weapons="Hold",
          route=[(-35.75, 134.65, 0)], telegraph=2),
        U("neutral", "_vanilla", "civ_ms_bulk", "merchant",
          name="MV Bight Trader (Whyalla-Fremantle)", weapons="Hold",
          route=[(-35.85, 132.50, 0)], telegraph=3),
        U("blue", "SEST_RAAF_Bases", "airbase_raaf_edinburgh", "home",
          name="RAAF Base Edinburgh", nation="australia", weapons="Hold"),
    ],
    resolve={"Passage": "victory", "Traffic": "neutral",
             "Flagship": ("protect", "escort")},
    window=dict(flights=[HELO, RECON], detachment=True,
                situation="An urgent diversion with the ships and stores "
                          "already available. No purchases, repair or rearm. "
                          "Support resumes before The Southern Convoy."),
    expires_after="The Southern Convoy",
    role="escort",
)
