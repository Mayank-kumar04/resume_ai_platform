"""
ResumeAI Platform — Link Validator (Phase 9)
Validates all URLs found in a resume using HTTP HEAD requests.
Detects broken links, private resources, and invalid URLs.
Runs in a thread pool to avoid blocking.
"""

import re
import concurrent.futures
from dataclasses import dataclass
from urllib.parse import urlparse
from typing import Optional

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# ─── Link Result ─────────────────────────────────────────────────────────────
@dataclass
class LinkResult:
    url:         str
    status:      str    # 'ok' | 'broken' | 'private' | 'redirect' | 'invalid' | 'timeout' | 'error'
    http_code:   int    = 0
    final_url:   str    = ""
    note:        str    = ""
    category:    str    = ""   # 'github' | 'linkedin' | 'portfolio' | 'certificate' | 'other'

    @property
    def is_valid(self) -> bool:
        return self.status in ("ok", "redirect")

    @property
    def badge_variant(self) -> str:
        return {
            "ok":       "success",
            "redirect": "info",
            "private":  "warning",
            "broken":   "danger",
            "invalid":  "danger",
            "timeout":  "warning",
            "error":    "warning",
        }.get(self.status, "neutral")


# ─── Link Validator ───────────────────────────────────────────────────────────
class LinkValidator:
    """
    Validates a list of URLs concurrently.

    Usage:
        validator = LinkValidator()
        results   = validator.validate_all(urls)
    """

    TIMEOUT = 8   # seconds per request
    MAX_WORKERS = 6

    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    def validate_all(self, urls: list[str]) -> list[LinkResult]:
        """Validate a list of URLs concurrently. Returns list of LinkResult."""
        if not urls:
            return []

        # Filter and deduplicate
        clean_urls = list({u.strip() for u in urls if u.strip()})

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as pool:
            futures = {pool.submit(self._check, url): url for url in clean_urls}
            results = []
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())

        return sorted(results, key=lambda r: r.url)

    def _check(self, url: str) -> LinkResult:
        category = self._categorize(url)

        # Validate URL structure
        if not self._is_valid_url(url):
            return LinkResult(
                url=url, status="invalid",
                note="URL format is invalid.", category=category
            )

        if not REQUESTS_AVAILABLE:
            return LinkResult(
                url=url, status="error",
                note="requests library not installed.", category=category
            )

        # Special handling: Google Drive private links
        if "drive.google.com" in url and "/view" not in url:
            return LinkResult(
                url=url, status="private",
                note="Google Drive link may not be publicly accessible.",
                category=category
            )

        try:
            response = requests.head(
                url,
                allow_redirects=True,
                timeout=self.TIMEOUT,
                headers=self.HEADERS,
            )

            final_url = response.url
            code = response.status_code

            if code == 200:
                note = "Accessible."
                # LinkedIn always shows 200 but may be behind login wall
                if "linkedin.com" in url and "/in/" in url:
                    note = "LinkedIn profile URL format is valid."
                return LinkResult(url=url, status="ok", http_code=code,
                                  final_url=final_url, note=note, category=category)

            elif code in (301, 302, 303, 307, 308):
                return LinkResult(url=url, status="redirect", http_code=code,
                                  final_url=final_url,
                                  note=f"Redirects to {final_url}", category=category)

            elif code == 403:
                return LinkResult(url=url, status="private", http_code=code,
                                  note="Access forbidden — may require login.", category=category)

            elif code == 404:
                return LinkResult(url=url, status="broken", http_code=code,
                                  note="Page not found (404).", category=category)

            elif code >= 500:
                return LinkResult(url=url, status="error", http_code=code,
                                  note=f"Server error ({code}).", category=category)

            else:
                return LinkResult(url=url, status="ok", http_code=code,
                                  note=f"HTTP {code}", category=category)

        except requests.exceptions.Timeout:
            return LinkResult(url=url, status="timeout",
                              note="Request timed out.", category=category)
        except requests.exceptions.ConnectionError:
            return LinkResult(url=url, status="broken",
                              note="Connection failed.", category=category)
        except Exception as e:
            return LinkResult(url=url, status="error",
                              note=str(e)[:80], category=category)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _is_valid_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except Exception:
            return False

    def _categorize(self, url: str) -> str:
        url_lower = url.lower()
        if "github.com" in url_lower:
            return "github"
        if "linkedin.com" in url_lower:
            return "linkedin"
        if "drive.google.com" in url_lower:
            return "gdrive"
        if any(x in url_lower for x in ["coursera", "udemy", "edx", "credential", "certif"]):
            return "certificate"
        return "portfolio"

    @staticmethod
    def extract_urls(text: str) -> list[str]:
        """Extract all URLs from raw text."""
        pattern = r"https?://[^\s<>\"',;(){}|\\^\[\]`]+"
        return re.findall(pattern, text)
