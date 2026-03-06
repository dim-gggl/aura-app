import json
from pathlib import Path

_BASE = Path(__file__).parent

ART_TYPES = json.loads((_BASE / "art_types.json").read_text(encoding="utf-8"))
TECHNIQUES = json.loads((_BASE / "techniques.json").read_text(encoding="utf-8"))
SUPPORTS = json.loads((_BASE / "supports.json").read_text(encoding="utf-8"))


def get_art_types():
    return ART_TYPES


def get_techniques():
    return TECHNIQUES


def get_supports():
    return SUPPORTS
