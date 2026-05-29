"""
ResumeAI Platform — Benchmark Engine (Phase 10)
Compares a user's resume against a successful benchmark resume
for quality, structure, impact, and keyword richness.

This is NOT plagiarism detection — it is quality comparison.
"""

import re
from dataclasses import dataclass, field
from parser.resume_parser import ResumeParser, ResumeData


@dataclass
class BenchmarkDimension:
    name:         str
    user_score:   int
    bench_score:  int
    delta:        int        # positive = user is ahead
    insight:      str


@dataclass
class BenchmarkResult:
    overall_delta:  int                    = 0
    dimensions:     list[BenchmarkDimension] = field(default_factory=list)
    advantages:     list[str]              = field(default_factory=list)
    gaps:           list[str]              = field(default_factory=list)
    summary:        str                    = ""
    benchmark_name: str                    = ""


class BenchmarkEngine:
    """
    Loads a benchmark PDF and compares it against the user's resume
    across 6 quality dimensions.

    Usage:
        engine = BenchmarkEngine()
        result = engine.compare(user_resume_data, benchmark_pdf_path)
    """

    def compare(self, user: ResumeData, benchmark_path: str) -> BenchmarkResult:
        parser = ResumeParser()
        bench  = parser.parse(benchmark_path)

        result = BenchmarkResult()
        result.benchmark_name = benchmark_path.split("/")[-1]

        dims = [
            self._compare_impact(user, bench),
            self._compare_skills(user, bench),
            self._compare_structure(user, bench),
            self._compare_action_verbs(user, bench),
            self._compare_section_depth(user, bench),
            self._compare_quantification(user, bench),
        ]

        result.dimensions = dims
        result.overall_delta = sum(d.delta for d in dims) // len(dims)

        for d in dims:
            if d.delta >= 10:
                result.advantages.append(f"Your '{d.name}' is stronger than the benchmark.")
            elif d.delta <= -15:
                result.gaps.append(f"Benchmark has stronger '{d.name}' — {d.insight}")

        result.summary = (
            f"Overall delta vs benchmark: {result.overall_delta:+d} points. "
            f"{len(result.advantages)} strengths, {len(result.gaps)} areas to improve."
        )

        return result

    # ── Dimensions ────────────────────────────────────────────────────────────

    def _compare_impact(self, user: ResumeData, bench: ResumeData) -> BenchmarkDimension:
        def _quantified_pct(data: ResumeData) -> int:
            bullets = [l for l in data.raw_text.splitlines()
                       if re.match(r"^\s*[•\-\*▪]\s+", l)]
            if not bullets:
                return 0
            q = sum(1 for b in bullets if re.search(r"\d", b))
            return int((q / len(bullets)) * 100)

        u = _quantified_pct(user)
        b = _quantified_pct(bench)
        return BenchmarkDimension(
            name="Impact Quantification", user_score=u, bench_score=b, delta=u - b,
            insight=f"Benchmark has {b}% quantified bullets vs your {u}%."
        )

    def _compare_skills(self, user: ResumeData, bench: ResumeData) -> BenchmarkDimension:
        u = len(user.skills)
        b = len(bench.skills)
        score_u = min(100, u * 5)
        score_b = min(100, b * 5)
        return BenchmarkDimension(
            name="Skill Breadth", user_score=score_u, bench_score=score_b, delta=score_u - score_b,
            insight=f"Benchmark lists {b} skills vs your {u}."
        )

    def _compare_structure(self, user: ResumeData, bench: ResumeData) -> BenchmarkDimension:
        def _section_score(r: ResumeData) -> int:
            return sum([r.has_summary, r.has_experience, r.has_education,
                        r.has_skills, r.has_projects]) * 20
        u = _section_score(user)
        b = _section_score(bench)
        return BenchmarkDimension(
            name="Resume Structure", user_score=u, bench_score=b, delta=u - b,
            insight="Benchmark covers more standard resume sections."
        )

    def _compare_action_verbs(self, user: ResumeData, bench: ResumeData) -> BenchmarkDimension:
        STRONG = [
            "developed", "engineered", "architected", "implemented", "optimized",
            "designed", "built", "launched", "led", "reduced", "increased",
            "automated", "deployed", "integrated",
        ]
        def _verb_density(r: ResumeData) -> int:
            text = r.raw_text.lower()
            hits = sum(1 for v in STRONG if v in text)
            return min(100, hits * 7)
        u = _verb_density(user)
        b = _verb_density(bench)
        return BenchmarkDimension(
            name="Action Verb Strength", user_score=u, bench_score=b, delta=u - b,
            insight="Benchmark uses more strong action verbs."
        )

    def _compare_section_depth(self, user: ResumeData, bench: ResumeData) -> BenchmarkDimension:
        def _depth(r: ResumeData) -> int:
            return min(100, r.word_count // 4)
        u = _depth(user)
        b = _depth(bench)
        return BenchmarkDimension(
            name="Content Depth", user_score=u, bench_score=b, delta=u - b,
            insight=f"Benchmark has {bench.word_count} words vs your {user.word_count}."
        )

    def _compare_quantification(self, user: ResumeData, bench: ResumeData) -> BenchmarkDimension:
        def _bullet_count(r: ResumeData) -> int:
            return min(100, r.bullet_count * 5)
        u = _bullet_count(user)
        b = _bullet_count(bench)
        return BenchmarkDimension(
            name="Bullet Usage", user_score=u, bench_score=b, delta=u - b,
            insight=f"Benchmark has {bench.bullet_count} bullets vs your {user.bullet_count}."
        )
