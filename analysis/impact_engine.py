"""
ResumeAI Platform — Impact Quantifier (Phase 8)
Detects bullet points lacking measurable impact and suggests
how to quantify them based on context clues.
"""

import re
from dataclasses import dataclass, field


@dataclass
class ImpactSuggestion:
    original:   str
    suggestion:  str
    reason:      str
    category:    str    # 'scale' | 'performance' | 'time' | 'adoption' | 'quality'


# ─── Quantification Templates ─────────────────────────────────────────────────
# Maps context pattern → (suggestion template, category)
QUANT_TEMPLATES = [
    # App / platform usage
    (r"\b(app|application|platform|tool|system)\b",
     "Add user scale: e.g., '…used by 500+ users' or '…serving 10K+ monthly active users'",
     "scale"),

    # Performance / speed
    (r"\b(optimiz|improv|reduc|speed|fast|perform|latency|load)\w*",
     "Add a performance metric: e.g., 'reduced load time by 40%' or 'improved throughput by 2×'",
     "performance"),

    # Automation
    (r"\b(automat|script|pipeline|workflow|process)\w*",
     "Quantify time saved: e.g., 'automating 3 hours of manual work per week'",
     "time"),

    # API / integration
    (r"\b(api|endpoint|integrat|microservice)\w*",
     "Add scale: e.g., 'handling 1,000+ requests/minute' or 'integrating 5 third-party services'",
     "scale"),

    # Testing
    (r"\b(test|coverage|bug|defect|qa)\w*",
     "Add coverage or reduction stat: e.g., 'achieving 90% test coverage' or 'reducing bugs by 60%'",
     "quality"),

    # Team / collaboration
    (r"\b(team|collaborat|mentor|train|onboard)\w*",
     "Add team size: e.g., 'collaborating with a team of 8 engineers'",
     "scale"),

    # Revenue / cost
    (r"\b(revenue|cost|saving|profit|customer|sale)\w*",
     "Add financial impact: e.g., 'contributing to $50K cost reduction' or 'supporting 200+ customers'",
     "scale"),

    # Machine learning / model
    (r"\b(model|accuracy|precision|recall|train|classif)\w*",
     "Add accuracy metric: e.g., 'achieving 94% accuracy on validation set'",
     "performance"),

    # Deployment
    (r"\b(deploy|launch|release|ship)\w*",
     "Add deployment scale or frequency: e.g., 'deploying to AWS serving 50K users'",
     "adoption"),

    # Database / data
    (r"\b(data|database|migrat|pipeline|etl)\w*",
     "Add data scale: e.g., 'processing 1M+ records daily' or 'migrating 500GB of data'",
     "scale"),
]


# ─── Impact Engine ────────────────────────────────────────────────────────────
class ImpactEngine:
    """
    Analyses resume bullets for missing quantification.
    Returns a list of ImpactSuggestion for each weak bullet.

    Usage:
        engine      = ImpactEngine()
        suggestions = engine.analyze(resume_text)
    """

    def analyze(self, text: str) -> list[ImpactSuggestion]:
        suggestions = []

        for line in text.splitlines():
            stripped = line.strip()

            # Only examine bullet-point lines
            if not re.match(r"^[•\-\*▪◦>]\s+", stripped):
                continue

            content = re.sub(r"^[•\-\*▪◦>]\s*", "", stripped)

            # Skip lines that already have numbers (already quantified)
            if re.search(r"\d", content):
                continue

            # Skip very short lines
            if len(content.split()) < 5:
                continue

            # Try to match a template
            for pattern, suggestion_text, category in QUANT_TEMPLATES:
                if re.search(pattern, content, re.IGNORECASE):
                    suggestions.append(ImpactSuggestion(
                        original   = stripped[:120],
                        suggestion = suggestion_text,
                        reason     = f"No metrics found — context suggests '{category}' quantification is possible.",
                        category   = category,
                    ))
                    break   # one suggestion per line

        return suggestions

    def quantification_score(self, text: str) -> dict:
        """
        Returns a summary dict:
          total_bullets, quantified_bullets, unquantified_bullets, pct_quantified
        """
        bullets = [
            line.strip() for line in text.splitlines()
            if re.match(r"^\s*[•\-\*▪◦>]\s+", line)
        ]
        quantified = [b for b in bullets if re.search(r"\d", b)]
        total = len(bullets)
        pct = round((len(quantified) / total) * 100, 1) if total else 0.0

        return {
            "total_bullets":      total,
            "quantified_bullets": len(quantified),
            "unquantified_bullets": total - len(quantified),
            "pct_quantified":     pct,
        }
