"""
ResumeAI Platform — ATS Scoring Engine (Phase 5)
Calculates a weighted ATS score from 0–100 across 6 categories.
All scores are deterministic and explainable — never random.

Category weights (must sum to 1.0):
    keyword_match   30%
    formatting      20%
    grammar         15%
    structure       15%
    impact_writing  10%
    ats_compliance  10%
"""

import re
from dataclasses import dataclass, field
from typing import Optional

from parser.resume_parser import ResumeData


# ─── Score Result ─────────────────────────────────────────────────────────────
@dataclass
class ATSScoreResult:
    overall:          int             = 0
    keyword:          int             = 0
    formatting:       int             = 0
    grammar:          int             = 0
    structure:        int             = 0
    impact:           int             = 0
    compliance:       int             = 0

    reasoning:        dict[str, str]  = field(default_factory=dict)
    improvements:     list[str]       = field(default_factory=list)
    strengths:        list[str]       = field(default_factory=list)

    # Pass-through from matcher (set externally)
    keyword_match_pct:  float         = 0.0
    matched_keywords:   list[str]     = field(default_factory=list)
    missing_keywords:   list[str]     = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "ats":                self.overall,
            "keyword":            self.keyword,
            "formatting":         self.formatting,
            "grammar":            self.grammar,
            "structure":          self.structure,
            "impact":             self.impact,
            "compliance":         self.compliance,
            "keyword_match_pct":  self.keyword_match_pct,
            "matched_keywords":   self.matched_keywords,
            "missing_keywords":   self.missing_keywords,
        }


# ─── Weights ──────────────────────────────────────────────────────────────────
WEIGHTS = {
    "keyword":    0.30,
    "formatting": 0.20,
    "grammar":    0.15,
    "structure":  0.15,
    "impact":     0.10,
    "compliance": 0.10,
}


# ─── ATS Scorer ───────────────────────────────────────────────────────────────
class ATSScorer:
    """
    Orchestrates all sub-scores and produces a final ATSScoreResult.

    Usage:
        scorer = ATSScorer()
        result = scorer.score(resume_data, jd_keywords=[], grammar_issues=[])
    """

    def score(
        self,
        resume: ResumeData,
        jd_keywords:      list[str]  = None,
        grammar_issues:   list[dict] = None,
        matcher_result:   dict       = None,
    ) -> ATSScoreResult:

        jd_keywords    = jd_keywords    or []
        grammar_issues = grammar_issues or []
        matcher_result = matcher_result or {}

        result = ATSScoreResult()

        # ── Individual category scores ────────────────────────────────
        result.keyword    = self._score_keywords(resume, jd_keywords, matcher_result, result)
        result.formatting = self._score_formatting(resume, result)
        result.grammar    = self._score_grammar(grammar_issues, result)
        result.structure  = self._score_structure(resume, result)
        result.impact     = self._score_impact(resume, result)
        result.compliance = self._score_compliance(resume, result)

        # ── Weighted overall ──────────────────────────────────────────
        result.overall = int(
            result.keyword    * WEIGHTS["keyword"]    +
            result.formatting * WEIGHTS["formatting"] +
            result.grammar    * WEIGHTS["grammar"]    +
            result.structure  * WEIGHTS["structure"]  +
            result.impact     * WEIGHTS["impact"]     +
            result.compliance * WEIGHTS["compliance"]
        )

        # Pass-through matcher data
        if matcher_result:
            result.keyword_match_pct = matcher_result.get("match_pct", 0.0)
            result.matched_keywords  = matcher_result.get("matched", [])
            result.missing_keywords  = matcher_result.get("missing", [])

        return result

    # ── Keyword Score (30%) ───────────────────────────────────────────────────
    def _score_keywords(self, resume: ResumeData, jd_keywords: list[str],
                        matcher_result: dict, result: ATSScoreResult) -> int:
        if not jd_keywords:
            # No JD provided — score based on skill density alone
            skill_count = len(resume.skills)
            score = min(100, skill_count * 4)
            result.reasoning["keyword"] = (
                f"No job description provided. Scored {score}/100 based on "
                f"{skill_count} detected skills."
            )
            if skill_count < 10:
                result.improvements.append("Add more technical skills to your Skills section.")
            return score

        match_pct = matcher_result.get("match_pct", 0.0)
        score = int(match_pct)

        result.reasoning["keyword"] = (
            f"{match_pct:.1f}% keyword overlap with job description. "
            f"{len(matcher_result.get('matched', []))} matched, "
            f"{len(matcher_result.get('missing', []))} missing."
        )

        if match_pct < 40:
            result.improvements.append("Fewer than 40% of JD keywords found — tailor your resume more closely.")
        elif match_pct >= 80:
            result.strengths.append("Excellent keyword alignment with the job description.")

        return min(100, score)

    # ── Formatting Score (20%) ────────────────────────────────────────────────
    def _score_formatting(self, resume: ResumeData, result: ATSScoreResult) -> int:
        score = 100
        notes = []

        # Page count: 1–2 pages ideal
        if resume.page_count == 0:
            score -= 30
            notes.append("Could not determine page count.")
        elif resume.page_count > 2:
            score -= 15
            result.improvements.append(
                f"Resume is {resume.page_count} pages — ATS prefers 1–2 pages for most roles."
            )

        # Word count sanity check (200–800 words ideal)
        if resume.word_count < 200:
            score -= 20
            notes.append("Resume appears very short (< 200 words).")
            result.improvements.append("Expand resume content — aim for 400–700 words.")
        elif resume.word_count > 900:
            score -= 10
            result.improvements.append("Resume is long — consider trimming to under 800 words.")

        # Bullet usage
        if resume.bullet_count < 5:
            score -= 15
            result.improvements.append(
                "Add more bullet points — ATS scanners parse bullet-formatted achievements more reliably."
            )
        elif resume.bullet_count >= 15:
            result.strengths.append("Good use of bullet points throughout the resume.")

        # Contact info completeness
        if not resume.email:
            score -= 10
            result.improvements.append("Email address not detected — ensure it is present and parseable.")
        if not resume.phone:
            score -= 5

        result.reasoning["formatting"] = (
            f"Pages: {resume.page_count}, Words: {resume.word_count}, "
            f"Bullets: {resume.bullet_count}. " + " ".join(notes)
        )

        return max(0, score)

    # ── Grammar Score (15%) ───────────────────────────────────────────────────
    def _score_grammar(self, grammar_issues: list[dict],
                       result: ATSScoreResult) -> int:
        issue_count = len(grammar_issues)

        if issue_count == 0:
            result.strengths.append("No grammar or spelling issues detected.")
            result.reasoning["grammar"] = "Zero grammar issues found."
            return 100

        # Deduct proportionally: each issue costs ~3 points, max penalty 70
        score = max(30, 100 - issue_count * 3)

        result.reasoning["grammar"] = (
            f"{issue_count} grammar/spelling issue(s) detected."
        )
        if issue_count > 10:
            result.improvements.append(
                f"{issue_count} grammar issues found — proofread carefully before submitting."
            )

        return score

    # ── Structure Score (15%) ─────────────────────────────────────────────────
    def _score_structure(self, resume: ResumeData,
                         result: ATSScoreResult) -> int:
        score = 0
        present = []
        missing = []

        checklist = {
            "Summary/Objective":   resume.has_summary,
            "Experience":          resume.has_experience,
            "Education":           resume.has_education,
            "Skills":              resume.has_skills,
            "Projects":            resume.has_projects,
        }

        for label, present_flag in checklist.items():
            if present_flag:
                score += 20
                present.append(label)
            else:
                missing.append(label)

        result.reasoning["structure"] = (
            f"Detected sections: {', '.join(present) or 'none'}. "
            f"Missing: {', '.join(missing) or 'none'}."
        )

        for m in missing:
            result.improvements.append(f"Add a clear '{m}' section heading.")

        if len(present) >= 4:
            result.strengths.append("Resume contains all major sections expected by ATS systems.")

        # Bonus: LinkedIn or GitHub present
        if resume.linkedin or resume.github:
            score = min(100, score + 5)

        return min(100, score)

    # ── Impact Writing Score (10%) ────────────────────────────────────────────
    def _score_impact(self, resume: ResumeData,
                      result: ATSScoreResult) -> int:
        text = resume.raw_text.lower()
        score = 50  # baseline

        # Check for quantification (numbers in bullet points)
        bullets_with_numbers = sum(
            1 for line in resume.raw_text.splitlines()
            if re.match(r"^\s*[•\-\*▪]\s+", line) and re.search(r"\d+", line)
        )

        if bullets_with_numbers >= 5:
            score = min(100, score + 35)
            result.strengths.append(
                f"{bullets_with_numbers} bullet points contain metrics or numbers."
            )
        elif bullets_with_numbers >= 2:
            score = min(100, score + 20)
            result.improvements.append(
                "Add more quantified achievements — e.g. 'Reduced load time by 40%'."
            )
        else:
            result.improvements.append(
                "Almost no quantified metrics found. Recruiters respond strongly to numbers."
            )

        # Strong action verbs
        strong_verbs = [
            "developed", "engineered", "architected", "implemented", "optimized",
            "designed", "built", "launched", "led", "reduced", "increased",
            "automated", "deployed", "integrated", "created", "improved",
        ]
        verb_hits = sum(1 for v in strong_verbs if v in text)

        if verb_hits >= 8:
            score = min(100, score + 15)
            result.strengths.append("Strong use of action verbs throughout.")
        elif verb_hits < 4:
            score = max(0, score - 10)
            result.improvements.append(
                "Replace weak verbs ('worked on', 'helped', 'responsible for') "
                "with strong action verbs."
            )

        result.reasoning["impact"] = (
            f"{bullets_with_numbers} quantified bullets, {verb_hits} strong action verbs found."
        )

        return max(0, min(100, score))

    # ── ATS Compliance Score (10%) ────────────────────────────────────────────
    def _score_compliance(self, resume: ResumeData,
                          result: ATSScoreResult) -> int:
        score = 100
        text = resume.raw_text

        # Check for table-like layouts (lots of pipe characters = multi-column)
        pipe_count = text.count("|")
        if pipe_count > 10:
            score -= 20
            result.improvements.append(
                "Resume may use a multi-column or table layout — "
                "many ATS systems cannot parse these correctly."
            )

        # Check for very long unbroken lines (common in graphics-heavy resumes)
        long_lines = sum(1 for line in text.splitlines() if len(line) > 120)
        if long_lines > 5:
            score -= 10
            result.improvements.append(
                "Some lines are very long — may indicate a complex layout that confuses ATS parsers."
            )

        # Verify standard section headings exist
        standard_headings_found = sum([
            resume.has_experience,
            resume.has_education,
            resume.has_skills,
        ])
        if standard_headings_found < 2:
            score -= 20
            result.improvements.append(
                "Standard section headings (Experience, Education, Skills) "
                "must be clearly labelled for ATS parsing."
            )

        # File type already validated (PDF) — give credit
        if score >= 90:
            result.strengths.append("Resume format is ATS-compatible.")

        result.reasoning["compliance"] = (
            f"Pipe characters: {pipe_count}, Long lines: {long_lines}, "
            f"Standard headings: {standard_headings_found}/3."
        )

        return max(0, score)
