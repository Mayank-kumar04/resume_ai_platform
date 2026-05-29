"""
ResumeAI Platform — Template Compliance Checker (Phase 10)
Heuristic checks for ATS-unfriendly formatting.
"""

import re
from dataclasses import dataclass, field
from parser.resume_parser import ResumeData


@dataclass
class TemplateIssue:
    issue:       str
    severity:    str    # 'critical' | 'warning' | 'info'
    fix:         str


class TemplateChecker:
    """Detects ATS-unfriendly template issues via heuristics."""

    def check(self, resume: ResumeData) -> list[TemplateIssue]:
        issues = []
        text = resume.raw_text

        # Multi-column detection (high pipe / tab density)
        pipe_count = text.count("|")
        if pipe_count > 15:
            issues.append(TemplateIssue(
                issue    = f"Possible multi-column layout detected ({pipe_count} pipe characters).",
                severity = "critical",
                fix      = "Use a single-column layout. Many ATS systems read left-to-right "
                           "and skip content in side columns entirely."
            ))

        # Excessive whitespace / blank lines
        blank_lines = len([l for l in text.splitlines() if not l.strip()])
        if blank_lines > 20:
            issues.append(TemplateIssue(
                issue    = f"Too many blank lines ({blank_lines}).",
                severity = "warning",
                fix      = "Reduce excessive spacing. ATS parsers may misread sections separated by large gaps."
            ))

        # Very long unbroken lines (possible table cells)
        long_lines = [l for l in text.splitlines() if len(l) > 120]
        if len(long_lines) > 3:
            issues.append(TemplateIssue(
                issue    = f"{len(long_lines)} lines exceed 120 characters.",
                severity = "warning",
                fix      = "Wrap long lines — may indicate a complex layout that confuses parsers."
            ))

        # Header/footer repetition
        first_page_text = text[:500]
        repeated = sum(1 for line in first_page_text.splitlines()
                       if len(line) > 5 and text.count(line) > 2)
        if repeated > 3:
            issues.append(TemplateIssue(
                issue    = "Repeated content detected — possibly header/footer repeating across pages.",
                severity = "warning",
                fix      = "Avoid repeating your name/header in the footer of every page."
            ))

        # Missing standard sections
        if not resume.has_experience and not resume.has_projects:
            issues.append(TemplateIssue(
                issue    = "Neither 'Experience' nor 'Projects' section detected.",
                severity = "critical",
                fix      = "At least one of these sections must have a clear heading "
                           "for ATS to parse your background."
            ))

        # Page count
        if resume.page_count > 2:
            issues.append(TemplateIssue(
                issue    = f"Resume is {resume.page_count} pages.",
                severity = "warning",
                fix      = "Trim to 1–2 pages. Most ATS systems and recruiters prefer concise resumes."
            ))

        return issues
