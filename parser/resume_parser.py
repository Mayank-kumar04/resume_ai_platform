"""
ResumeAI Platform — Resume Parser (Phase 3)
Extracts structured data from a PDF resume using pdfplumber + regex.

ResumeParser.parse(path) → ResumeData dataclass
"""

import re
import os
from dataclasses import dataclass, field
from typing import Optional

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


# ─── Data Model ───────────────────────────────────────────────────────────────
@dataclass
class ResumeData:
    raw_text:       str               = ""
    name:           str               = ""
    email:          str               = ""
    phone:          str               = ""
    linkedin:       str               = ""
    github:         str               = ""
    portfolio:      str               = ""
    skills:         list[str]         = field(default_factory=list)
    sections:       dict[str, str]    = field(default_factory=dict)
    links:          list[str]         = field(default_factory=list)
    bullet_count:   int               = 0
    page_count:     int               = 0
    word_count:     int               = 0
    has_summary:    bool              = False
    has_experience: bool              = False
    has_education:  bool              = False
    has_skills:     bool              = False
    has_projects:   bool              = False
    parse_errors:   list[str]         = field(default_factory=list)


# ─── Section Heading Patterns ─────────────────────────────────────────────────
SECTION_PATTERNS = {
    "summary":        r"\b(summary|objective|profile|about me|professional summary)\b",
    "experience":     r"\b(experience|work experience|employment|work history|career)\b",
    "education":      r"\b(education|academic|qualifications|degrees?)\b",
    "skills":         r"\b(skills|technical skills|core competencies|technologies|tech stack)\b",
    "projects":       r"\b(projects?|personal projects?|academic projects?|portfolio)\b",
    "certifications": r"\b(certifications?|certificates?|licenses?|credentials)\b",
    "awards":         r"\b(awards?|honors?|achievements?|accomplishments?)\b",
    "publications":   r"\b(publications?|research|papers?)\b",
    "languages":      r"\b(languages?|spoken languages?)\b",
}

# ─── Common Technical Skills Vocabulary ───────────────────────────────────────
TECH_SKILLS_VOCAB = {
    # Languages
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "go", "rust",
    "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "dart", "bash",
    # Web
    "react", "angular", "vue", "next.js", "nuxt", "svelte", "html", "css",
    "tailwind", "bootstrap", "sass", "webpack", "vite",
    # Backend
    "node.js", "express", "django", "flask", "fastapi", "spring", "laravel",
    "rails", "asp.net", "graphql", "rest", "grpc",
    # Databases
    "postgresql", "mysql", "sqlite", "mongodb", "redis", "elasticsearch",
    "cassandra", "dynamodb", "firebase", "supabase",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
    "jenkins", "github actions", "ci/cd", "linux", "nginx",
    # Data & ML
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "spark", "hadoop", "airflow", "tableau", "power bi",
    # Tools
    "git", "github", "gitlab", "jira", "figma", "postman", "vs code",
    "jupyter", "selenium", "pytest",
}


# ─── Main Parser ──────────────────────────────────────────────────────────────
class ResumeParser:
    """
    Parses a PDF resume into structured ResumeData.

    Usage:
        parser = ResumeParser()
        data   = parser.parse("/path/to/resume.pdf")
    """

    def parse(self, filepath: str) -> ResumeData:
        data = ResumeData()

        if pdfplumber is None:
            data.parse_errors.append("pdfplumber not installed — run: pip install pdfplumber")
            return data

        if not os.path.isfile(filepath):
            data.parse_errors.append(f"File not found: {filepath}")
            return data

        if not filepath.lower().endswith(".pdf"):
            data.parse_errors.append("Only PDF files are supported.")
            return data

        try:
            with pdfplumber.open(filepath) as pdf:
                data.page_count = len(pdf.pages)
                pages_text = []

                for page in pdf.pages:
                    text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
                    pages_text.append(text)

                    # Collect hyperlinks
                    for annot in page.annots or []:
                        uri = annot.get("uri")
                        if uri and uri not in data.links:
                            data.links.append(uri)

                data.raw_text = "\n".join(pages_text)

        except Exception as e:
            data.parse_errors.append(f"PDF read error: {e}")
            return data

        # ── Post-process extracted text ───────────────────────────────
        self._extract_contact_info(data)
        self._detect_sections(data)
        self._extract_skills(data)
        self._count_bullets(data)

        data.word_count = len(data.raw_text.split())

        return data

    # ── Contact Info ──────────────────────────────────────────────────────────
    def _extract_contact_info(self, data: ResumeData):
        text = data.raw_text

        # Email
        email_match = re.search(
            r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text
        )
        if email_match:
            data.email = email_match.group()

        # Phone — common formats
        phone_match = re.search(
            r"(\+?\d[\d\s\-().]{7,}\d)", text
        )
        if phone_match:
            data.phone = phone_match.group().strip()

        # LinkedIn
        linkedin = re.search(
            r"linkedin\.com/in/[\w\-]+", text, re.IGNORECASE
        )
        if linkedin:
            data.linkedin = "https://" + linkedin.group()

        # GitHub
        github = re.search(
            r"github\.com/[\w\-]+(?:/[\w\-]+)?", text, re.IGNORECASE
        )
        if github:
            data.github = "https://" + github.group()

        # Portfolio / personal site
        portfolio = re.search(
            r"https?://(?!.*(?:linkedin|github))[\w\-./]+\.[a-zA-Z]{2,}", text
        )
        if portfolio:
            data.portfolio = portfolio.group()

        # Name heuristic: first non-empty line, title-cased, no special chars
        for line in text.splitlines():
            line = line.strip()
            if line and re.match(r"^[A-Z][a-zA-Z]+(\s[A-Z][a-zA-Z]+)+$", line):
                data.name = line
                break

    # ── Section Detection ─────────────────────────────────────────────────────
    def _detect_sections(self, data: ResumeData):
        """
        Split raw text into labelled sections by detecting heading lines.
        A heading line is short (< 60 chars), matches a known pattern,
        and is in UPPER CASE or Title Case.
        """
        lines = data.raw_text.splitlines()
        current_section = "header"
        section_buffer: dict[str, list[str]] = {"header": []}

        for line in lines:
            stripped = line.strip()
            if not stripped:
                section_buffer.setdefault(current_section, []).append("")
                continue

            detected = self._classify_heading(stripped)
            if detected:
                current_section = detected
                section_buffer.setdefault(current_section, [])
            else:
                section_buffer.setdefault(current_section, []).append(stripped)

        # Flatten to string
        data.sections = {k: "\n".join(v).strip() for k, v in section_buffer.items() if v}

        # Set presence flags
        data.has_summary    = bool(data.sections.get("summary"))
        data.has_experience = bool(data.sections.get("experience"))
        data.has_education  = bool(data.sections.get("education"))
        data.has_skills     = bool(data.sections.get("skills"))
        data.has_projects   = bool(data.sections.get("projects"))

    def _classify_heading(self, line: str) -> Optional[str]:
        """Return section key if line looks like a heading, else None."""
        # Headings are typically short and ALL CAPS / Title Case
        if len(line) > 60:
            return None
        if not (line.isupper() or re.match(r"^[A-Z][A-Za-z\s&/]+$", line)):
            return None

        lower = line.lower()
        for section_key, pattern in SECTION_PATTERNS.items():
            if re.search(pattern, lower):
                return section_key
        return None

    # ── Skill Extraction ──────────────────────────────────────────────────────
    def _extract_skills(self, data: ResumeData):
        """Find known tech skills in the full text."""
        text_lower = data.raw_text.lower()
        found = set()

        for skill in TECH_SKILLS_VOCAB:
            # Whole-word match
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_lower):
                found.add(skill)

        # Also grab comma/pipe-separated tokens from the Skills section
        skills_text = data.sections.get("skills", "")
        for token in re.split(r"[,|•\n·/]", skills_text):
            token = token.strip().lower()
            if 2 <= len(token) <= 40:
                found.add(token)

        data.skills = sorted(found)

    # ── Bullet Count ──────────────────────────────────────────────────────────
    def _count_bullets(self, data: ResumeData):
        """Count bullet-point lines (lines starting with •, -, *, or ▪)."""
        data.bullet_count = sum(
            1 for line in data.raw_text.splitlines()
            if re.match(r"^\s*[•\-\*▪◦>]\s+\S", line)
        )
