"""
ResumeAI Platform — Job Description Analyzer (Phase 6)
Extracts required skills, preferred skills, tools, experience level,
and action verbs from a raw job description string.
No web scraping — works on pasted text only.
"""

import re
from collections import Counter
from dataclasses import dataclass, field


# ─── Result Dataclass ─────────────────────────────────────────────────────────
@dataclass
class JDAnalysis:
    title:              str         = ""
    required_skills:    list[str]   = field(default_factory=list)
    preferred_skills:   list[str]   = field(default_factory=list)
    tools:              list[str]   = field(default_factory=list)
    experience_years:   int         = 0
    all_keywords:       list[str]   = field(default_factory=list)
    keyword_freq:       dict        = field(default_factory=dict)
    action_verbs:       list[str]   = field(default_factory=list)
    education_req:      str         = ""
    is_remote:          bool        = False
    seniority:          str         = ""    # junior | mid | senior | lead


# ─── Known Keywords ───────────────────────────────────────────────────────────
TECH_KEYWORDS = {
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "dart",
    # Web
    "react", "angular", "vue", "next.js", "nuxt", "svelte", "html", "css",
    "tailwind", "bootstrap", "webpack", "graphql", "rest api", "restful",
    # Backend
    "node.js", "express", "django", "flask", "fastapi", "spring boot", "laravel",
    "asp.net", "grpc", "microservices", "kafka", "rabbitmq",
    # DB
    "postgresql", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "firebase", "oracle",
    # Cloud / DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s",
    "terraform", "ansible", "jenkins", "github actions", "ci/cd",
    "linux", "nginx", "apache",
    # Data / ML
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "spark", "hadoop", "airflow", "tableau", "power bi", "sql", "nosql",
    "machine learning", "deep learning", "nlp", "data science", "llm",
    # Tools
    "git", "github", "gitlab", "jira", "confluence", "figma", "postman",
    "selenium", "jest", "pytest", "agile", "scrum",
    # Auth / Security
    "jwt", "oauth", "ssl", "tls", "auth0",
}

SOFT_KEYWORDS = {
    "communication", "teamwork", "collaboration", "leadership", "problem-solving",
    "adaptability", "time management", "critical thinking", "creativity",
    "mentoring", "cross-functional",
}

SENIORITY_MAP = {
    "junior":       ["junior", "entry level", "entry-level", "associate", "0-2 years", "fresher"],
    "mid":          ["mid level", "mid-level", "2-5 years", "3+ years", "2+ years"],
    "senior":       ["senior", "5+ years", "4+ years", "experienced"],
    "lead":         ["lead", "principal", "staff", "architect", "manager", "head of"],
}

EDUCATION_PATTERNS = [
    r"\b(b\.?tech|bachelor'?s?|b\.?e\.?|b\.?sc)\b",
    r"\b(m\.?tech|master'?s?|m\.?sc|m\.?e\.?|mba)\b",
    r"\b(phd|ph\.?d\.?|doctorate)\b",
]


# ─── JD Analyzer ─────────────────────────────────────────────────────────────
class JDAnalyzer:
    """
    Analyzes a job description string.

    Usage:
        analyzer = JDAnalyzer()
        result   = analyzer.analyze(jd_text)
    """

    def analyze(self, jd_text: str) -> JDAnalysis:
        if not jd_text or not jd_text.strip():
            return JDAnalysis()

        result = JDAnalysis()
        text = jd_text.strip()
        text_lower = text.lower()

        result.title      = self._extract_title(text)
        result.is_remote  = bool(re.search(r"\bremote\b", text_lower))
        result.seniority  = self._detect_seniority(text_lower)
        result.experience_years = self._extract_experience_years(text_lower)
        result.education_req    = self._extract_education(text_lower)

        result.required_skills, result.preferred_skills = \
            self._split_required_preferred(text, text_lower)

        result.tools     = self._extract_tools(text_lower)
        result.all_keywords, result.keyword_freq = \
            self._extract_all_keywords(text_lower)
        result.action_verbs = self._extract_action_verbs(text_lower)

        return result

    # ── Title ────────────────────────────────────────────────────────────────
    def _extract_title(self, text: str) -> str:
        # First non-empty line is usually the job title
        for line in text.splitlines():
            line = line.strip()
            if line and len(line) < 80:
                return line
        return ""

    # ── Seniority ────────────────────────────────────────────────────────────
    def _detect_seniority(self, text: str) -> str:
        for level, patterns in SENIORITY_MAP.items():
            if any(p in text for p in patterns):
                return level
        return "mid"

    # ── Experience Years ─────────────────────────────────────────────────────
    def _extract_experience_years(self, text: str) -> int:
        matches = re.findall(r"(\d+)\+?\s*years?", text)
        if matches:
            return max(int(m) for m in matches)
        return 0

    # ── Education ────────────────────────────────────────────────────────────
    def _extract_education(self, text: str) -> str:
        if re.search(r"\bphd|ph\.d", text):
            return "PhD"
        if re.search(r"\bmaster|m\.tech|m\.sc|mba", text):
            return "Master's"
        if re.search(r"\bbachelor|b\.tech|b\.sc|b\.e\b", text):
            return "Bachelor's"
        return ""

    # ── Required vs Preferred Skills ─────────────────────────────────────────
    def _split_required_preferred(self, text: str, text_lower: str):
        """
        Split the JD into required and preferred blocks by scanning for
        section headers like 'Requirements', 'Nice to have', etc.
        """
        required_block = text_lower
        preferred_block = ""

        # Common patterns that indicate a "preferred / nice-to-have" section
        pref_markers = [
            "nice to have", "preferred qualifications", "preferred skills",
            "bonus", "plus if", "good to have", "preferred experience",
        ]
        for marker in pref_markers:
            idx = text_lower.find(marker)
            if idx != -1:
                required_block = text_lower[:idx]
                preferred_block = text_lower[idx:]
                break

        required = [k for k in TECH_KEYWORDS if re.search(r"\b" + re.escape(k) + r"\b", required_block)]
        preferred = [k for k in TECH_KEYWORDS if re.search(r"\b" + re.escape(k) + r"\b", preferred_block)]

        # Remove overlap
        preferred = [k for k in preferred if k not in required]

        return sorted(required), sorted(preferred)

    # ── Tool Extraction ───────────────────────────────────────────────────────
    def _extract_tools(self, text: str) -> list[str]:
        tool_set = {
            "jira", "confluence", "github", "gitlab", "bitbucket", "figma",
            "postman", "insomnia", "datadog", "grafana", "splunk", "kibana",
            "jupyter", "colab", "vs code", "pycharm", "intellij",
            "slack", "notion", "linear", "asana", "trello",
        }
        return sorted(t for t in tool_set if re.search(r"\b" + re.escape(t) + r"\b", text))

    # ── All Keywords + Frequency ──────────────────────────────────────────────
    def _extract_all_keywords(self, text: str):
        all_vocab = TECH_KEYWORDS | SOFT_KEYWORDS
        found = {}
        for kw in all_vocab:
            count = len(re.findall(r"\b" + re.escape(kw) + r"\b", text))
            if count > 0:
                found[kw] = count
        # Sort by frequency
        sorted_kw = sorted(found.items(), key=lambda x: -x[1])
        keywords = [k for k, _ in sorted_kw]
        freq = dict(sorted_kw)
        return keywords, freq

    # ── Action Verbs ──────────────────────────────────────────────────────────
    def _extract_action_verbs(self, text: str) -> list[str]:
        job_verbs = [
            "develop", "design", "implement", "build", "deploy", "optimize",
            "maintain", "collaborate", "communicate", "lead", "mentor",
            "architect", "analyze", "test", "debug", "monitor", "automate",
            "integrate", "manage", "deliver", "scale", "improve",
        ]
        return [v for v in job_verbs if v in text]
