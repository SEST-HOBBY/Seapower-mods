"""MNO environment service, offline reference implementation (Python, standard library only).

Modern Naval Operations (MNO) / Global Command Operations (GCO) environmental layer.
This package is the tested reference for the data pipeline, deterministic clock, per-save
persistence, forecast intelligence, mission weather adapter, ice and route rules. It runs
outside Sea Power. Nothing here is loaded by the game, and nothing here makes a network call
unless a tool is run with an explicit --online flag.

Status labels used in docstrings and docs/environment/ENV-STATUS.md:
BUILD-TESTED, IN-GAME TESTED, VISUAL DEMO ONLY, DESIGN ONLY, BLOCKED.
"""

RULES_VERSION = "mno.env.rules.2026-11-18.1"
FEATURE_FLAG = "MNO_ENVIRONMENT_ENABLED"  # off unless the owner sets it; see ENV-ARCHITECTURE.md
