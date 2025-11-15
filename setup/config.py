import json

ART_TYPES = json.load(open("setup/art_types.json", encoding="utf-8"))
TECHNIQUES = json.load(open("setup/techniques.json", encoding="utf-8"))
SUPPORTS = json.load(open("setup/supports.json", encoding="utf-8"))


def get_art_types():
    return ART_TYPES


def get_techniques():
    return TECHNIQUES


def get_supports():
    return SUPPORTS
