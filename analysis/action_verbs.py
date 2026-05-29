"""
ResumeAI Platform — Action Verb Enhancer (Phase 8)
Detects weak verbs and responsibility-language in bullet points
and suggests stronger, context-aware replacements.
"""

import re
from dataclasses import dataclass, field


# ─── Weak Verb Catalogue ─────────────────────────────────────────────────────
# Maps weak phrase → list of strong alternatives
WEAK_TO_STRONG: dict[str, list[str]] = {
    "worked on":            ["Developed", "Built", "Engineered", "Implemented"],
    "worked with":          ["Collaborated with", "Leveraged", "Utilized", "Integrated"],
    "helped":               ["Assisted", "Contributed to", "Supported", "Enabled"],
    "helped to":            ["Contributed to", "Facilitated", "Streamlined"],
    "helped with":          ["Supported", "Facilitated", "Accelerated"],
    "responsible for":      ["Managed", "Owned", "Led", "Oversaw", "Directed"],
    "was responsible for":  ["Managed", "Led", "Owned", "Spearheaded"],
    "made":                 ["Built", "Developed", "Created", "Engineered", "Produced"],
    "did":                  ["Executed", "Delivered", "Completed", "Achieved"],
    "used":                 ["Leveraged", "Implemented", "Applied", "Utilized"],
    "tried to":             ["Achieved", "Successfully delivered"],
    "attempted to":         ["Completed", "Delivered"],
    "involved in":          ["Contributed to", "Collaborated on", "Played a key role in"],
    "participated in":      ["Contributed to", "Collaborated on"],
    "assisted":             ["Supported", "Contributed to", "Enabled"],
    "assisted in":          ["Contributed to", "Facilitated"],
    "assisted with":        ["Supported", "Streamlined"],
    "given":                ["Delivered", "Presented", "Provided"],
    "did work on":          ["Engineered", "Developed", "Built"],
    "managed to":           ["Successfully", "Delivered"],
    "handled":              ["Managed", "Oversaw", "Executed", "Coordinated"],
    "worked":               ["Developed", "Engineered", "Contributed"],
    "helped build":         ["Co-developed", "Contributed to building", "Engineered"],
    "wrote":                ["Authored", "Developed", "Engineered", "Implemented"],
    "fixed":                ["Resolved", "Debugged", "Patched", "Remediated"],
    "changed":              ["Refactored", "Optimized", "Improved", "Enhanced"],
    "tested":               ["Validated", "Verified", "Automated testing for", "QA'd"],
    "learned":              ["Acquired proficiency in", "Mastered"],
    "looked at":            ["Analyzed", "Investigated", "Evaluated"],
    "set up":               ["Configured", "Deployed", "Provisioned", "Established"],
    "put together":         ["Assembled", "Developed", "Compiled", "Architected"],
    "came up with":         ["Designed", "Conceived", "Architected", "Proposed"],
    "thought of":           ["Conceptualized", "Designed", "Proposed"],
    "talked to":            ["Coordinated with", "Communicated with", "Liaised with"],
    "talked about":         ["Discussed", "Presented", "Communicated"],
    "made sure":            ["Ensured", "Validated", "Verified", "Guaranteed"],
    "kept track of":        ["Monitored", "Tracked", "Maintained oversight of"],
    "spent time":           ["Dedicated", "Invested time"],
}

# Context categories for smarter suggestions
CONTEXT_TECH    = {"develop", "build", "code", "implement", "api", "database", "server", "app", "software"}
CONTEXT_LEAD    = {"team", "managed", "project", "stakeholder", "sprint", "roadmap", "planning"}
CONTEXT_DATA    = {"data", "analysis", "model", "ml", "report", "dashboard", "pipeline"}
CONTEXT_DESIGN  = {"ui", "ux", "design", "figma", "prototype", "interface"}


@dataclass
class VerbSuggestion:
    original:    str
    line:        str
    alternatives: list[str] = field(default_factory=list)
    context:     str = ""


# ─── Action Verb Enhancer ─────────────────────────────────────────────────────
class ActionVerbEnhancer:
    """
    Scans resume text for weak verb phrases in bullet points
    and returns contextual replacement suggestions.

    Usage:
        enhancer    = ActionVerbEnhancer()
        suggestions = enhancer.suggest(resume_text)
    """

    def suggest(self, text: str) -> list[VerbSuggestion]:
        suggestions = []

        for line in text.splitlines():
            stripped = line.strip()

            # Only process bullet-point lines
            if not re.match(r"^[•\-\*▪◦>]\s+", stripped):
                # Also check lines starting with capital word (experience bullets sometimes lack bullet char)
                if not re.match(r"^[A-Z][a-z]", stripped):
                    continue

            line_lower = stripped.lower()
            context = self._detect_context(line_lower)

            for weak, alternatives in WEAK_TO_STRONG.items():
                # Match at the start of the bullet content
                content = re.sub(r"^[•\-\*▪◦>]\s*", "", stripped)
                if content.lower().startswith(weak):
                    # Pick contextual alternatives if available
                    filtered = self._contextual_filter(alternatives, context)
                    suggestions.append(VerbSuggestion(
                        original     = weak,
                        line         = stripped[:100],
                        alternatives = filtered[:3],
                        context      = context,
                    ))
                    break  # one match per line

        return suggestions

    def _detect_context(self, text: str) -> str:
        if any(w in text for w in CONTEXT_TECH):
            return "technical"
        if any(w in text for w in CONTEXT_LEAD):
            return "leadership"
        if any(w in text for w in CONTEXT_DATA):
            return "data"
        if any(w in text for w in CONTEXT_DESIGN):
            return "design"
        return "general"

    def _contextual_filter(self, alternatives: list[str], context: str) -> list[str]:
        """
        Prioritise alternatives that fit the detected context.
        Falls back to the full list if no context-specific match.
        """
        context_priority = {
            "technical":   ["Engineered", "Developed", "Implemented", "Built", "Architected"],
            "leadership":  ["Led", "Managed", "Spearheaded", "Directed", "Oversaw"],
            "data":        ["Analyzed", "Modeled", "Optimized", "Automated", "Processed"],
            "design":      ["Designed", "Prototyped", "Crafted", "Conceptualized"],
            "general":     [],
        }
        priority = context_priority.get(context, [])
        ordered = [a for a in alternatives if a in priority] + \
                  [a for a in alternatives if a not in priority]
        return ordered or alternatives
