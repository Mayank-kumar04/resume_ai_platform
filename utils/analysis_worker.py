"""
ResumeAI Platform — Analysis Worker (QThread)
Runs all analysis engines in a background thread so the UI stays responsive.
Emits progress updates and a final result dict.
"""

from PyQt5.QtCore import QThread, pyqtSignal

from parser.resume_parser import ResumeParser, ResumeData
from analysis.jd_analyzer import JDAnalyzer
from analysis.resume_matcher import ResumeMatcher
from analysis.ats_engine import ATSScorer
from analysis.grammar_checker import GrammarAnalyzer
from analysis.action_verbs import ActionVerbEnhancer
from analysis.impact_engine import ImpactEngine
from analysis.link_validator import LinkValidator
from analysis.section_analyzer import SectionAnalyzer
from analysis.skill_gap import SkillGapEngine
from analysis.template_checker import TemplateChecker
from database import DatabaseManager


class AnalysisWorker(QThread):
    """
    Background thread that runs the full analysis pipeline.

    Signals:
        progress(int, str)   — percent complete + status message
        finished(dict)       — full result payload
        error(str)           — error message
    """

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error    = pyqtSignal(str)

    def __init__(self, resume_path: str, jd_text: str = "",
                 benchmark_path: str = "", parent=None):
        super().__init__(parent)
        self.resume_path    = resume_path
        self.jd_text        = jd_text
        self.benchmark_path = benchmark_path

    def run(self):
        try:
            result = {}

            # ── Step 1: Parse Resume ──────────────────────────────────
            self.progress.emit(5, "Parsing resume PDF…")
            parser = ResumeParser()
            resume = parser.parse(self.resume_path)

            if resume.parse_errors:
                self.error.emit("; ".join(resume.parse_errors))
                return

            result["resume"] = resume

            # ── Step 2: Analyze JD ────────────────────────────────────
            jd_analysis = None
            matcher_result = {}
            if self.jd_text.strip():
                self.progress.emit(20, "Analyzing job description…")
                jd_analysis = JDAnalyzer().analyze(self.jd_text)
                result["jd"] = jd_analysis

                self.progress.emit(35, "Matching resume against job description…")
                match = ResumeMatcher().match(resume, jd_analysis)
                matcher_result = {
                    "match_pct":  match.match_pct,
                    "matched":    match.matched,
                    "missing":    match.missing,
                    "high_gaps":  match.high_priority_gaps,
                    "low_gaps":   match.low_priority_gaps,
                    "skill_pct":  match.skill_overlap_pct,
                    "summary":    match.summary,
                }
                result["match"] = match

            # ── Step 3: Grammar ───────────────────────────────────────
            self.progress.emit(48, "Checking grammar and writing quality…")
            grammar_analyzer = GrammarAnalyzer()
            grammar_issues   = grammar_analyzer.check(resume.raw_text)
            result["grammar_issues"] = grammar_issues

            # ── Step 4: ATS Score ─────────────────────────────────────
            self.progress.emit(60, "Calculating ATS score…")
            scorer     = ATSScorer()
            jd_kws     = jd_analysis.all_keywords if jd_analysis else []
            ats_result = scorer.score(
                resume,
                jd_keywords    = jd_kws,
                grammar_issues = grammar_issues,
                matcher_result = matcher_result,
            )
            result["ats"] = ats_result

            # ── Step 5: Action Verbs ──────────────────────────────────
            self.progress.emit(68, "Analysing action verbs…")
            result["verb_suggestions"] = ActionVerbEnhancer().suggest(resume.raw_text)

            # ── Step 6: Impact Engine ─────────────────────────────────
            self.progress.emit(73, "Scanning for unquantified bullets…")
            result["impact_suggestions"] = ImpactEngine().analyze(resume.raw_text)
            result["quant_stats"]        = ImpactEngine().quantification_score(resume.raw_text)

            # ── Step 7: Link Validation ───────────────────────────────
            self.progress.emit(78, "Validating links…")
            all_links = resume.links + LinkValidator.extract_urls(resume.raw_text)
            result["link_results"] = LinkValidator().validate_all(list(set(all_links)))

            # ── Step 8: Section Analysis ──────────────────────────────
            self.progress.emit(84, "Evaluating section quality…")
            result["section_feedback"] = SectionAnalyzer().analyze(resume)

            # ── Step 9: Template Compliance ───────────────────────────
            self.progress.emit(88, "Checking ATS template compliance…")
            result["template_issues"] = TemplateChecker().check(resume)

            # ── Step 10: Skill Gap ────────────────────────────────────
            if jd_analysis:
                self.progress.emit(92, "Identifying skill gaps…")
                result["skill_gap"] = SkillGapEngine().analyze(resume, jd_analysis)

            # ── Step 11: Benchmark ────────────────────────────────────
            if self.benchmark_path:
                self.progress.emit(95, "Comparing with benchmark resume…")
                from analysis.benchmark_engine import BenchmarkEngine
                result["benchmark"] = BenchmarkEngine().compare(resume, self.benchmark_path)

            # ── Step 12: Save to DB ───────────────────────────────────
            self.progress.emit(97, "Saving to database…")
            db = DatabaseManager.instance()
            import os
            resume_id = db.save_resume(
                filename  = os.path.basename(self.resume_path),
                filepath  = self.resume_path,
                raw_text  = resume.raw_text,
                ats_score = ats_result.overall,
            )
            jd_id = None
            if jd_analysis and self.jd_text.strip():
                jd_id = db.save_jd(self.jd_text, jd_analysis.title)

            db.save_report(resume_id, ats_result.to_dict(), jd_id)
            result["resume_id"] = resume_id

            self.progress.emit(100, "Analysis complete!")
            self.finished.emit(result)

        except Exception as e:
            import traceback
            self.error.emit(f"Analysis failed: {e}\n{traceback.format_exc()}")
