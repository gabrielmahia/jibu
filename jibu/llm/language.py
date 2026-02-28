"""jibu — Language detection.

Detects whether a question is in Kiswahili or English.
Jibu is bilingual: the response language matches the question language.

Detection approach: lightweight keyword + character pattern heuristic.
A full language detection library (langdetect, lingua) is overkill for
a two-language system where the signal is strong.
"""
from __future__ import annotations

from enum import Enum


class Language(str, Enum):
    SWAHILI = "sw"
    ENGLISH = "en"
    UNKNOWN = "unknown"


# High-frequency Kiswahili words that are unambiguous (not also common English)
_SW_MARKERS = frozenset([
    "ni", "na", "ya", "wa", "kwa", "je", "nini", "jinsi", "gani", "haki",
    "sheria", "serikali", "polisi", "kazi", "mshahara", "ardhi", "afya",
    "biashara", "unapaswa", "ninaweza", "naweza", "unaweza", "mimi", "wewe",
    "wao", "sisi", "hakuna", "lazima", "lakini", "pia", "sana", "zaidi",
    "kutoka", "mpaka", "baada", "kabla", "tafadhali", "asante", "karibu",
    "nzuri", "mbaya", "pesa", "fedha", "nyumba", "mtu", "watu", "mtoto",
    "familia", "mkopo", "benki", "hesabu", "mkataba",
])

_MIN_SW_TOKENS = 2  # Require at least this many Swahili markers to classify as Swahili


def detect(text: str) -> Language:
    """Detect whether ``text`` is primarily Kiswahili or English.

    Returns:
        :class:`Language` — SWAHILI, ENGLISH, or UNKNOWN for very short inputs.
    """
    if not text or len(text.strip()) < 3:
        return Language.UNKNOWN

    tokens = text.lower().split()
    sw_count = sum(1 for t in tokens if t.strip("?.!,;:") in _SW_MARKERS)

    if len(tokens) < 3:
        return Language.UNKNOWN

    sw_ratio = sw_count / len(tokens)

    if sw_count >= _MIN_SW_TOKENS and sw_ratio >= 0.15:
        return Language.SWAHILI

    return Language.ENGLISH


def detect_or_default(text: str, default: Language = Language.ENGLISH) -> Language:
    """Like ``detect`` but returns ``default`` instead of UNKNOWN."""
    result = detect(text)
    return default if result == Language.UNKNOWN else result
