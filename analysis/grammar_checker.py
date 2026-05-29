"""
ResumeAI Platform — Grammar & Writing Analyzer (Phase 7)
Uses language-tool-python for grammar/spelling checks.
Falls back to a regex-based lite checker if LanguageTool is unavailable.

GrammarAnalyzer.check(text) → list[GrammarIssue]
"""

import re
from dataclasses import dataclass, field


# ─── Issue Dataclass ─────────────────────────────────────────────────────────
@dataclass
class GrammarIssue:
    message:     str   = ""
    context:     str   = ""
    suggestions: list  = field(default_factory=list)
    offset:      int   = 0
    length:      int   = 0
    rule_id:     str   = ""
    severity:    str   = "warning"   # 'error' | 'warning' | 'style'

    def to_dict(self) -> dict:
        return {
            "message":     self.message,
            "context":     self.context,
            "suggestions": self.suggestions[:3],
            "rule_id":     self.rule_id,
            "severity":    self.severity,
        }


# ─── Regex Patterns for Lite Fallback ────────────────────────────────────────
WEAK_PHRASE_PATTERNS = [
    (r"\bresponsible for\b",  "Replace 'responsible for' with an action verb (e.g., 'Managed', 'Led')."),
    (r"\bworked on\b",        "Replace 'worked on' with a specific action verb."),
    (r"\bhelped (?:to )?",    "Replace 'helped' with a direct action verb."),
    (r"\bwas involved in\b",  "Replace 'was involved in' — use an active verb instead."),
    (r"\bassisted (?:in|with)", "Replace 'assisted' with a direct action verb."),
    (r"\bknowledge of\b",     "Replace 'knowledge of X' with a concrete skill claim."),
    (r"\bfamiliar with\b",    "Replace 'familiar with' — either list it as a skill or remove."),
    (r"\bpassionate about\b", "Remove filler phrase 'passionate about'."),
    (r"\bteam player\b",      "Remove generic phrase 'team player' — show it with examples."),
    (r"\bhard[- ]?working\b", "Remove 'hard-working' — it adds no value to ATS."),
    (r"\bself[- ]?motivated\b", "Remove 'self-motivated' — universally used filler."),
    (r"\bexcellent communication\b", "Remove 'excellent communication' — show don't tell."),
    (r"\betc\.\b",            "Avoid 'etc.' in bullet points — be specific about what you list."),
    (r"\bvarious\b",          "Replace 'various' with specific examples."),
]

PASSIVE_VOICE_PATTERN = re.compile(
    r"\b(was|were|been|is|are|am|be)\s+\w+ed\b", re.IGNORECASE
)

TENSE_INCONSISTENCY_PRESENT = re.compile(
    r"\b(develop|build|implement|create|design|maintain|manage)\b", re.IGNORECASE
)

DOUBLE_SPACE = re.compile(r"  +")
MISSING_PERIOD = re.compile(r"[a-z]{3,}\n[A-Z]")


# ─── Grammar Analyzer ────────────────────────────────────────────────────────
class GrammarAnalyzer:
    """
    Checks resume text for grammar, spelling, passive voice, and weak phrases.

    Tries to use language-tool-python first; falls back to regex checks
    if LT is not installed or the server fails to start.

    Usage:
        analyzer = GrammarAnalyzer()
        issues   = analyzer.check(text)
    """

    def __init__(self):
        self._lt = None
        self._lt_available = False
        self._init_language_tool()

    def _init_language_tool(self):
        try:
            import language_tool_python
            self._lt = language_tool_python.LanguageTool("en-US")
            self._lt_available = True
        except Exception:
            self._lt_available = False

    # ── Public API ────────────────────────────────────────────────────────────
    def check(self, text: str) -> list[GrammarIssue]:
        """Return a list of GrammarIssue for the given resume text."""
        issues: list[GrammarIssue] = []

        if self._lt_available:
            issues.extend(self._lt_check(text))
        else:
            issues.extend(self._regex_spelling_check(text))

        # Always run style checks regardless of LT availability
        issues.extend(self._check_weak_phrases(text))
        issues.extend(self._check_passive_voice(text))

        # Deduplicate by (offset, message)
        seen = set()
        unique = []
        for issue in issues:
            key = (issue.offset, issue.message[:40])
            if key not in seen:
                seen.add(key)
                unique.append(issue)

        return unique

    # ── LanguageTool Check ────────────────────────────────────────────────────
    def _lt_check(self, text: str) -> list[GrammarIssue]:
        issues = []
        try:
            matches = self._lt.check(text)
            for m in matches:
                # Filter out irrelevant rules
                if m.ruleId in {"WHITESPACE_RULE", "EN_QUOTES", "COMMA_PARENTHESIS_WHITESPACE"}:
                    continue
                issues.append(GrammarIssue(
                    message     = m.message,
                    context     = m.context,
                    suggestions = list(m.replacements[:3]),
                    offset      = m.offset,
                    length      = m.errorLength,
                    rule_id     = m.ruleId,
                    severity    = "error" if "spelling" in m.message.lower() else "warning",
                ))
        except Exception:
            pass
        return issues

    # ── Regex Spelling / Double-space ────────────────────────────────────────
    def _regex_spelling_check(self, text: str) -> list[GrammarIssue]:
        issues = []
        for match in DOUBLE_SPACE.finditer(text):
            issues.append(GrammarIssue(
                message  = "Extra whitespace detected.",
                context  = text[max(0, match.start()-20):match.end()+20],
                offset   = match.start(),
                rule_id  = "DOUBLE_SPACE",
                severity = "warning",
            ))
        return issues

    # ── Weak Phrase Detection ─────────────────────────────────────────────────
    def _check_weak_phrases(self, text: str) -> list[GrammarIssue]:
        issues = []
        for pattern, advice in WEAK_PHRASE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                issues.append(GrammarIssue(
                    message  = advice,
                    context  = text[max(0, match.start()-30):match.end()+30],
                    offset   = match.start(),
                    rule_id  = "WEAK_PHRASE",
                    severity = "style",
                ))
        return issues

    # ── Passive Voice Detection ───────────────────────────────────────────────
    def _check_passive_voice(self, text: str) -> list[GrammarIssue]:
        issues = []
        for match in PASSIVE_VOICE_PATTERN.finditer(text):
            # Only flag inside bullet-like lines
            line_start = text.rfind("\n", 0, match.start()) + 1
            line = text[line_start:text.find("\n", match.end())]
            if re.match(r"\s*[•\-\*▪]", line):
                issues.append(GrammarIssue(
                    message  = "Passive voice detected in bullet point — use an active verb instead.",
                    context  = line.strip()[:80],
                    offset   = match.start(),
                    rule_id  = "PASSIVE_VOICE",
                    severity = "style",
                ))
        return issues

    # ── Cleanup ───────────────────────────────────────────────────────────────
    def close(self):
        if self._lt_available and self._lt:
            try:
                self._lt.close()
            except Exception:
                pass
