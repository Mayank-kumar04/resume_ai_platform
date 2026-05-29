"""
ResumeAI Platform — Database Layer (Phase 2)
SQLite integration with schema creation, insert, and query helpers.
All DB access goes through DatabaseManager (singleton pattern).
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional


DB_PATH = os.path.join(os.path.dirname(__file__), "resume_ai.db")


class DatabaseManager:
    """
    Singleton database manager.
    Creates tables on first run, exposes typed query methods.

    Usage:
        db = DatabaseManager.instance()
        db.save_resume("resume.pdf", 82)
    """

    _instance: Optional["DatabaseManager"] = None

    @classmethod
    def instance(cls) -> "DatabaseManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row   # dict-like rows
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._create_schema()

    # ─── Schema ────────────────────────────────────────────────────────────────
    def _create_schema(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS resumes (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                filename     TEXT    NOT NULL,
                filepath     TEXT    NOT NULL,
                upload_date  TEXT    NOT NULL,
                ats_score    INTEGER DEFAULT 0,
                raw_text     TEXT
            );

            CREATE TABLE IF NOT EXISTS job_descriptions (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT,
                content      TEXT    NOT NULL,
                created_at   TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS analysis_reports (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id        INTEGER NOT NULL,
                jd_id            INTEGER,
                created_at       TEXT    NOT NULL,
                ats_score        INTEGER DEFAULT 0,
                keyword_score    INTEGER DEFAULT 0,
                grammar_score    INTEGER DEFAULT 0,
                formatting_score INTEGER DEFAULT 0,
                structure_score  INTEGER DEFAULT 0,
                impact_score     INTEGER DEFAULT 0,
                compliance_score INTEGER DEFAULT 0,
                keyword_match_pct REAL   DEFAULT 0.0,
                matched_keywords TEXT,   -- JSON array
                missing_keywords TEXT,   -- JSON array
                grammar_issues   TEXT,   -- JSON array
                suggestions      TEXT,   -- JSON array
                FOREIGN KEY (resume_id) REFERENCES resumes(id),
                FOREIGN KEY (jd_id)     REFERENCES job_descriptions(id)
            );

            CREATE TABLE IF NOT EXISTS benchmark_comparisons (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id       INTEGER NOT NULL,
                benchmark_path  TEXT    NOT NULL,
                created_at      TEXT    NOT NULL,
                overall_delta   INTEGER DEFAULT 0,
                comparison_json TEXT,
                FOREIGN KEY (resume_id) REFERENCES resumes(id)
            );

            CREATE TABLE IF NOT EXISTS app_settings (
                key   TEXT PRIMARY KEY,
                value TEXT
            );
        """)
        self._conn.commit()

    # ─── Resumes ───────────────────────────────────────────────────────────────
    def save_resume(self, filename: str, filepath: str,
                    raw_text: str = "", ats_score: int = 0) -> int:
        """Insert a resume record and return its new ID."""
        cursor = self._conn.execute(
            """INSERT INTO resumes (filename, filepath, upload_date, ats_score, raw_text)
               VALUES (?, ?, ?, ?, ?)""",
            (filename, filepath, _now(), ats_score, raw_text)
        )
        self._conn.commit()
        return cursor.lastrowid

    def update_resume_score(self, resume_id: int, ats_score: int):
        self._conn.execute(
            "UPDATE resumes SET ats_score = ? WHERE id = ?",
            (ats_score, resume_id)
        )
        self._conn.commit()

    def get_resume(self, resume_id: int) -> Optional[sqlite3.Row]:
        return self._conn.execute(
            "SELECT * FROM resumes WHERE id = ?", (resume_id,)
        ).fetchone()

    def list_resumes(self) -> list:
        return self._conn.execute(
            "SELECT * FROM resumes ORDER BY upload_date DESC"
        ).fetchall()

    # ─── Job Descriptions ──────────────────────────────────────────────────────
    def save_jd(self, content: str, title: str = "") -> int:
        cursor = self._conn.execute(
            "INSERT INTO job_descriptions (title, content, created_at) VALUES (?, ?, ?)",
            (title, content, _now())
        )
        self._conn.commit()
        return cursor.lastrowid

    def get_jd(self, jd_id: int) -> Optional[sqlite3.Row]:
        return self._conn.execute(
            "SELECT * FROM job_descriptions WHERE id = ?", (jd_id,)
        ).fetchone()

    def list_jds(self) -> list:
        return self._conn.execute(
            "SELECT * FROM job_descriptions ORDER BY created_at DESC"
        ).fetchall()

    # ─── Analysis Reports ──────────────────────────────────────────────────────
    def save_report(self, resume_id: int, scores: dict,
                    jd_id: Optional[int] = None) -> int:
        """
        scores dict keys: ats, keyword, grammar, formatting,
                          structure, impact, compliance,
                          keyword_match_pct, matched_keywords,
                          missing_keywords, grammar_issues, suggestions
        """
        import json
        cursor = self._conn.execute(
            """INSERT INTO analysis_reports
               (resume_id, jd_id, created_at,
                ats_score, keyword_score, grammar_score,
                formatting_score, structure_score, impact_score, compliance_score,
                keyword_match_pct, matched_keywords, missing_keywords,
                grammar_issues, suggestions)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                resume_id, jd_id, _now(),
                scores.get("ats", 0),
                scores.get("keyword", 0),
                scores.get("grammar", 0),
                scores.get("formatting", 0),
                scores.get("structure", 0),
                scores.get("impact", 0),
                scores.get("compliance", 0),
                scores.get("keyword_match_pct", 0.0),
                json.dumps(scores.get("matched_keywords", [])),
                json.dumps(scores.get("missing_keywords", [])),
                json.dumps(scores.get("grammar_issues", [])),
                json.dumps(scores.get("suggestions", [])),
            )
        )
        self._conn.commit()
        return cursor.lastrowid

    def get_latest_report(self, resume_id: int) -> Optional[sqlite3.Row]:
        return self._conn.execute(
            """SELECT * FROM analysis_reports
               WHERE resume_id = ?
               ORDER BY created_at DESC LIMIT 1""",
            (resume_id,)
        ).fetchone()

    def list_reports(self, resume_id: int) -> list:
        return self._conn.execute(
            "SELECT * FROM analysis_reports WHERE resume_id = ? ORDER BY created_at DESC",
            (resume_id,)
        ).fetchall()

    # ─── Settings ──────────────────────────────────────────────────────────────
    def set_setting(self, key: str, value: str):
        self._conn.execute(
            "INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        self._conn.commit()

    def get_setting(self, key: str, default: str = "") -> str:
        row = self._conn.execute(
            "SELECT value FROM app_settings WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default

    # ─── Utility ───────────────────────────────────────────────────────────────
    def close(self):
        if self._conn:
            self._conn.close()


def _now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
