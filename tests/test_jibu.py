"""Tests for jibu — language detection and prompt construction."""
from __future__ import annotations

import pytest
from jibu.llm.language import Language, detect, detect_or_default
from jibu.llm.prompt import build_system_prompt


class TestLanguageDetection:
    def test_english_question(self):
        assert detect("What is the minimum wage in Kenya?") == Language.ENGLISH

    def test_swahili_question(self):
        assert detect("Mshahara wa chini ni kiasi gani kwa Kenya?") == Language.SWAHILI

    def test_swahili_rights_question(self):
        assert detect("Je, nina haki gani kama polisi wamenizuia?") == Language.SWAHILI

    def test_swahili_business_question(self):
        assert detect("Ninaweza kusajili biashara yangu vipi?") == Language.SWAHILI

    def test_empty_string_returns_unknown(self):
        assert detect("") == Language.UNKNOWN

    def test_very_short_returns_unknown(self):
        assert detect("ok") == Language.UNKNOWN

    def test_detect_or_default_unknown_returns_default(self):
        result = detect_or_default("hi", default=Language.ENGLISH)
        assert result == Language.ENGLISH

    def test_detect_or_default_swahili(self):
        result = detect_or_default("Je, nina haki gani kama polisi wamenizuia?")
        assert result == Language.SWAHILI


class TestPromptConstruction:
    def test_prompt_is_string(self):
        prompt = build_system_prompt(Language.ENGLISH)
        assert isinstance(prompt, str)
        assert len(prompt) > 100

    def test_prompt_contains_citation_requirement(self):
        prompt = build_system_prompt(Language.ENGLISH)
        assert "cite" in prompt.lower() or "citation" in prompt.lower() or "source" in prompt.lower()

    def test_prompt_contains_scope_boundaries(self):
        prompt = build_system_prompt(Language.ENGLISH)
        assert "outside" in prompt.lower() or "scope" in prompt.lower()

    def test_prompt_contains_legal_aid_orgs(self):
        prompt = build_system_prompt(Language.ENGLISH)
        assert "Kituo" in prompt or "FIDA" in prompt

    def test_prompt_does_not_claim_lawyer_role(self):
        prompt = build_system_prompt(Language.ENGLISH)
        # Should explicitly disclaim being a lawyer
        assert "lawyer" in prompt.lower()
