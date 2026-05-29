"""
ResumeAI Platform — Section Analyzer (Phase 10)
Provides section-by-section quality feedback.
"""

import re
from dataclasses import dataclass, field
from parser.resume_parser import ResumeData


@dataclass
class SectionFeedback:
    section:    str
    score:      int            = 0     # 0–100
    issues:     list[str]      = field(default_factory=list)
    strengths:  list[str]      = field(default_factory=list)
    tips:       list[str]      = field(default_factory=list)


class SectionAnalyzer:
    """
    Analyses individual resume sections for quality indicators.
    Returns a SectionFeedback per section.
    """

    def analyze(self, resume: ResumeData) -> list[SectionFeedback]:
        results = []

        if resume.sections.get("summary"):
            results.append(self._check_summary(resume.sections["summary"]))
        else:
            results.append(SectionFeedback(
                section="Summary", score=0,
                issues=["Summary/Objective section not found."],
                tips=["Add a 2–3 sentence professional summary at the top of your resume."]
            ))

        if resume.sections.get("experience"):
            results.append(self._check_experience(resume.sections["experience"]))

        if resume.sections.get("skills"):
            results.append(self._check_skills(resume.sections["skills"]))

        if resume.sections.get("projects"):
            results.append(self._check_projects(resume.sections["projects"]))

        if resume.sections.get("education"):
            results.append(self._check_education(resume.sections["education"]))

        return results

    def _check_summary(self, text: str) -> SectionFeedback:
        fb = SectionFeedback(section="Summary", score=100)
        words = len(text.split())

        if words < 20:
            fb.score -= 30
            fb.issues.append("Summary is too short (< 20 words).")
            fb.tips.append("Expand to 40–80 words highlighting your key strengths and goals.")
        elif words > 120:
            fb.score -= 15
            fb.tips.append("Summary is long — keep it under 100 words for ATS best practices.")

        weak_terms = ["passionate", "motivated", "team player", "hard-working", "dynamic"]
        used = [w for w in weak_terms if w in text.lower()]
        if used:
            fb.score -= 10 * len(used)
            fb.issues.append(f"Generic filler words found: {', '.join(used)}")
            fb.tips.append("Replace generic phrases with specific accomplishments or skills.")
        else:
            fb.strengths.append("Summary avoids generic buzzwords.")

        return fb

    def _check_experience(self, text: str) -> SectionFeedback:
        fb = SectionFeedback(section="Experience", score=100)
        lines = text.splitlines()

        bullet_lines = [l for l in lines if re.match(r"^\s*[•\-\*▪]\s+", l)]
        quantified   = [b for b in bullet_lines if re.search(r"\d", b)]

        if len(bullet_lines) < 5:
            fb.score -= 20
            fb.issues.append("Fewer than 5 bullet points in Experience.")
            fb.tips.append("Add 3–6 bullet points per role with concrete achievements.")
        else:
            fb.strengths.append(f"{len(bullet_lines)} bullet points in Experience section.")

        if quantified:
            fb.strengths.append(f"{len(quantified)} bullets contain metrics.")
        else:
            fb.score -= 25
            fb.issues.append("No quantified achievements in Experience.")
            fb.tips.append("Add numbers: '40% faster', '2× throughput', '10K users'.")

        # Check for dates
        if not re.search(r"\b(20\d\d|19\d\d|present|current)\b", text, re.IGNORECASE):
            fb.score -= 10
            fb.tips.append("Include start/end dates for each role.")

        return fb

    def _check_skills(self, text: str) -> SectionFeedback:
        fb = SectionFeedback(section="Skills", score=100)
        skill_tokens = [t.strip() for t in re.split(r"[,|•\n·/]", text) if t.strip()]

        if len(skill_tokens) < 6:
            fb.score -= 25
            fb.issues.append("Skills section appears sparse — fewer than 6 items detected.")
            fb.tips.append("List 10–20 skills covering languages, frameworks, tools, and platforms.")
        elif len(skill_tokens) >= 12:
            fb.strengths.append(f"Comprehensive skills section with {len(skill_tokens)} items.")

        return fb

    def _check_projects(self, text: str) -> SectionFeedback:
        fb = SectionFeedback(section="Projects", score=100)
        bullet_lines = [l for l in text.splitlines() if re.match(r"^\s*[•\-\*▪]\s+", l)]
        quantified   = [b for b in bullet_lines if re.search(r"\d", b)]

        if len(bullet_lines) < 3:
            fb.score -= 20
            fb.tips.append("Add 2–4 bullet points per project describing tech stack and outcomes.")

        if not quantified:
            fb.score -= 20
            fb.issues.append("Projects section lacks metrics.")
            fb.tips.append("Add a usage or impact stat to at least one project bullet.")

        links = re.findall(r"https?://\S+", text)
        if links:
            fb.strengths.append("Projects section includes links.")
        else:
            fb.tips.append("Consider adding GitHub or live demo links to your projects.")

        return fb

    def _check_education(self, text: str) -> SectionFeedback:
        fb = SectionFeedback(section="Education", score=100)

        if not re.search(r"\b(b\.?tech|bachelor|master|phd|m\.?tech|b\.?sc)\b", text, re.IGNORECASE):
            fb.score -= 20
            fb.tips.append("Clearly state your degree type (e.g., B.Tech, B.Sc, M.S.).")

        if not re.search(r"\b(gpa|cgpa|percentage|\d\.\d)\b", text, re.IGNORECASE):
            fb.tips.append("Include your GPA/CGPA if it is above 3.0/7.0 (depending on scale).")

        return fb
