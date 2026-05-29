"""
ResumeAI Platform — Resume ↔ JD Matcher (Phase 6)
Computes keyword overlap and TF-IDF cosine similarity between
the resume and job description.

ResumeMatcher.match(resume_data, jd_analysis) → MatchResult
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from parser.resume_parser import ResumeData
from analysis.jd_analyzer import JDAnalysis


# ─── Result Dataclass ─────────────────────────────────────────────────────────
@dataclass
class MatchResult:
    match_pct:          float       = 0.0   # 0–100
    semantic_score:     float       = 0.0   # cosine similarity 0–1
    matched:            list[str]   = field(default_factory=list)
    missing:            list[str]   = field(default_factory=list)
    high_priority_gaps: list[str]   = field(default_factory=list)  # in required, not in resume
    low_priority_gaps:  list[str]   = field(default_factory=list)  # in preferred only
    skill_overlap_pct:  float       = 0.0
    summary:            str         = ""


# ─── Matcher ─────────────────────────────────────────────────────────────────
class ResumeMatcher:
    """
    Compares a parsed resume against a JD analysis.

    Usage:
        matcher = ResumeMatcher()
        result  = matcher.match(resume_data, jd_analysis)
    """

    def match(self, resume: ResumeData, jd: JDAnalysis) -> MatchResult:
        result = MatchResult()

        if not jd.all_keywords:
            result.summary = "No JD keywords to match against."
            return result

        # Normalise resume text to a token set
        resume_tokens = self._tokenize(resume.raw_text)

        # ── Keyword overlap ───────────────────────────────────────────
        jd_keywords_set = set(jd.all_keywords)
        matched  = []
        missing  = []

        for kw in jd.all_keywords:
            # Whole-word search in resume text
            pattern = r"\b" + re.escape(kw) + r"\b"
            if re.search(pattern, resume.raw_text.lower()):
                matched.append(kw)
            else:
                missing.append(kw)

        result.matched = matched
        result.missing = missing

        total = len(jd_keywords_set)
        result.match_pct = round((len(matched) / total) * 100, 1) if total else 0.0

        # ── Priority gaps ─────────────────────────────────────────────
        required_set  = set(jd.required_skills)
        preferred_set = set(jd.preferred_skills)
        missing_set   = set(missing)

        result.high_priority_gaps = sorted(missing_set & required_set)
        result.low_priority_gaps  = sorted(missing_set & preferred_set)

        # ── Skill overlap % (resume skills vs JD required) ───────────
        resume_skills_set = set(s.lower() for s in resume.skills)
        if required_set:
            overlap = len(resume_skills_set & required_set)
            result.skill_overlap_pct = round((overlap / len(required_set)) * 100, 1)

        # ── Cosine similarity (TF-IDF fallback) ──────────────────────
        result.semantic_score = self._cosine_similarity(
            resume.raw_text.lower(),
            " ".join(jd.all_keywords)
        )

        # ── Summary ───────────────────────────────────────────────────
        result.summary = (
            f"{result.match_pct:.1f}% keyword match. "
            f"{len(result.high_priority_gaps)} high-priority skills missing. "
            f"Semantic similarity: {result.semantic_score:.2f}."
        )

        return result

    # ── Tokenizer ────────────────────────────────────────────────────────────
    def _tokenize(self, text: str) -> set:
        """Return a set of lowercase word tokens."""
        return set(re.findall(r"\b[a-zA-Z0-9#.+\-]{2,}\b", text.lower()))

    # ── Cosine Similarity (TF-IDF-like bag-of-words) ─────────────────────────
    def _cosine_similarity(self, text_a: str, text_b: str) -> float:
        """
        Simple bag-of-words cosine similarity.
        Falls back gracefully if scikit-learn is unavailable.
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity as sk_cos
            import numpy as np

            vectorizer = TfidfVectorizer()
            tfidf = vectorizer.fit_transform([text_a, text_b])
            score = sk_cos(tfidf[0:1], tfidf[1:2])[0][0]
            return round(float(score), 3)

        except Exception:
            # Manual dot-product fallback
            tokens_a = self._tokenize(text_a)
            tokens_b = self._tokenize(text_b)
            if not tokens_a or not tokens_b:
                return 0.0
            intersection = tokens_a & tokens_b
            score = len(intersection) / (len(tokens_a) ** 0.5 * len(tokens_b) ** 0.5)
            return round(score, 3)
