"""
ResumeAI Platform — Skill Gap Engine (Phase 10)
Recommends missing skills based on JD, resume, and industry frequency data.
"""

from dataclasses import dataclass, field
from analysis.jd_analyzer import JDAnalysis
from parser.resume_parser import ResumeData


# Industry skill frequency tables — higher = more commonly required
INDUSTRY_FREQ: dict[str, int] = {
    "docker": 90, "kubernetes": 75, "aws": 88, "ci/cd": 82,
    "github actions": 70, "redis": 65, "postgresql": 78, "mongodb": 60,
    "react": 85, "typescript": 80, "next.js": 65, "graphql": 55,
    "django": 60, "fastapi": 55, "flask": 58, "spring boot": 60,
    "jwt": 72, "oauth": 68, "linux": 82, "git": 95,
    "python": 90, "java": 75, "javascript": 88, "go": 55,
    "machine learning": 60, "pytorch": 50, "tensorflow": 52,
    "pandas": 65, "sql": 85, "elasticsearch": 52,
    "terraform": 55, "ansible": 45, "nginx": 60,
    "microservices": 68, "kafka": 52, "rabbitmq": 45,
}


@dataclass
class SkillGapResult:
    high_priority:  list[dict] = field(default_factory=list)  # in JD required + high industry freq
    medium_priority:list[dict] = field(default_factory=list)  # in JD preferred or medium freq
    low_priority:   list[dict] = field(default_factory=list)  # low freq extras to consider
    learning_path:  list[str]  = field(default_factory=list)  # ordered learning suggestions


class SkillGapEngine:
    """
    Produces a prioritised skill gap report.

    Usage:
        engine = SkillGapEngine()
        result = engine.analyze(resume_data, jd_analysis)
    """

    def analyze(self, resume: ResumeData, jd: JDAnalysis) -> SkillGapResult:
        result = SkillGapResult()
        resume_skills = {s.lower() for s in resume.skills}

        # High priority: required by JD + not in resume
        for skill in jd.required_skills:
            if skill not in resume_skills:
                freq = INDUSTRY_FREQ.get(skill, 30)
                result.high_priority.append({
                    "skill": skill,
                    "reason": "Required by job description",
                    "industry_freq": freq,
                })

        # Medium priority: preferred by JD or high industry freq
        for skill in jd.preferred_skills:
            if skill not in resume_skills:
                freq = INDUSTRY_FREQ.get(skill, 30)
                result.medium_priority.append({
                    "skill": skill,
                    "reason": "Preferred by job description",
                    "industry_freq": freq,
                })

        # Low priority: common industry skills not in resume or JD
        for skill, freq in sorted(INDUSTRY_FREQ.items(), key=lambda x: -x[1]):
            if skill not in resume_skills and skill not in jd.required_skills \
                    and skill not in jd.preferred_skills and freq >= 70:
                result.low_priority.append({
                    "skill": skill,
                    "reason": f"Commonly required in industry ({freq}% of postings)",
                    "industry_freq": freq,
                })
            if len(result.low_priority) >= 8:
                break

        result.learning_path = self._build_learning_path(result)
        return result

    def _build_learning_path(self, result: SkillGapResult) -> list[str]:
        """Return ordered learning suggestions with rough time estimates."""
        path = []
        for item in result.high_priority[:5]:
            skill = item["skill"]
            path.append(f"🔴 {skill.title()} — critical gap (1–4 weeks to basics)")
        for item in result.medium_priority[:4]:
            skill = item["skill"]
            path.append(f"🟡 {skill.title()} — preferred gap (2–6 weeks)")
        for item in result.low_priority[:3]:
            skill = item["skill"]
            path.append(f"🟢 {skill.title()} — industry standard (explore in 1–2 weeks)")
        return path
