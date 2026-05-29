"""
ResumeAI Platform — Report Exporter (Phase 11)
Generates HTML and plain-text analysis reports from a result dict.
"""

import os
from datetime import datetime


def _now_str() -> str:
    return datetime.now().strftime("%B %d, %Y at %I:%M %p")


def _score_color(score: int) -> str:
    if score >= 80:
        return "#22C55E"
    elif score >= 50:
        return "#F59E0B"
    return "#EF4444"


# ─── HTML Report ──────────────────────────────────────────────────────────────
def export_html(result: dict, output_path: str) -> str:
    """
    Generates a self-contained HTML report.
    Returns the output path on success.
    """
    ats    = result.get("ats")
    resume = result.get("resume")
    match  = result.get("match")
    jd     = result.get("jd")

    ats_score   = ats.overall    if ats    else 0
    resume_name = os.path.basename(resume.filepath if hasattr(resume, "filepath") else "resume.pdf") \
                  if resume else "Resume"

    # ── Category rows ─────────────────────────────────────────────────
    category_rows = ""
    if ats:
        cats = [
            ("Keyword Match",    ats.keyword,    "30%"),
            ("Formatting",       ats.formatting, "20%"),
            ("Grammar",          ats.grammar,    "15%"),
            ("Resume Structure", ats.structure,  "15%"),
            ("Impact Writing",   ats.impact,     "10%"),
            ("ATS Compliance",   ats.compliance, "10%"),
        ]
        for name, score, weight in cats:
            color = _score_color(score)
            category_rows += f"""
            <tr>
                <td>{name}</td>
                <td style="color:{color}; font-weight:700">{score}/100</td>
                <td>{weight}</td>
                <td>
                    <div style="background:#30363D; border-radius:4px; height:8px; width:200px;">
                        <div style="background:{color}; width:{score * 2}px; height:8px; border-radius:4px;"></div>
                    </div>
                </td>
            </tr>"""

    # ── Keyword section ───────────────────────────────────────────────
    keyword_html = ""
    if match:
        matched_chips = "".join(
            f'<span style="background:#0C2340; color:#38BDF8; border-radius:10px; '
            f'padding:3px 10px; margin:3px; display:inline-block; font-size:11px;">{k}</span>'
            for k in match.matched[:20]
        )
        missing_chips = "".join(
            f'<span style="background:#450A0A; color:#EF4444; border-radius:10px; '
            f'padding:3px 10px; margin:3px; display:inline-block; font-size:11px;">{k}</span>'
            for k in match.missing[:20]
        )
        keyword_html = f"""
        <div class="section">
            <h2>Keyword Match — {match.match_pct:.1f}%</h2>
            <p style="color:#8B949E">{match.summary}</p>
            <h3 style="color:#22C55E">✓ Matched</h3>
            <div>{matched_chips}</div>
            <h3 style="color:#EF4444; margin-top:16px">✗ Missing</h3>
            <div>{missing_chips}</div>
        </div>"""

    # ── Suggestions ───────────────────────────────────────────────────
    suggestions_html = ""
    if ats and ats.improvements:
        items = "".join(f"<li>{tip}</li>" for tip in ats.improvements)
        suggestions_html = f"""
        <div class="section">
            <h2>Recommendations</h2>
            <ul style="color:#E6EDF3; font-size:13px; line-height:2">{items}</ul>
        </div>"""

    # ── Grammar issues ────────────────────────────────────────────────
    grammar_html = ""
    grammar_issues = result.get("grammar_issues", [])
    if grammar_issues:
        rows = ""
        for issue in grammar_issues[:15]:
            d = issue.to_dict() if hasattr(issue, "to_dict") else {}
            rows += f"""
            <tr>
                <td style="color:#E6EDF3">{d.get("message","")[:80]}</td>
                <td style="color:#8B949E; font-style:italic">{d.get("context","")[:60]}</td>
                <td><span style="background:#451A03;color:#F59E0B;border-radius:6px;
                    padding:2px 8px;font-size:11px">{d.get("severity","").upper()}</span></td>
            </tr>"""
        grammar_html = f"""
        <div class="section">
            <h2>Grammar & Writing ({len(grammar_issues)} issues)</h2>
            <table width="100%">
                <thead><tr>
                    <th style="text-align:left">Issue</th>
                    <th style="text-align:left">Context</th>
                    <th>Severity</th>
                </tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>"""

    ats_color = _score_color(ats_score)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ResumeAI Analysis Report</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: "Segoe UI", "SF Pro Display", Arial, sans-serif;
    background: #0D1117;
    color: #E6EDF3;
    padding: 40px;
    max-width: 900px;
    margin: 0 auto;
  }}
  .header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 24px;
    border-bottom: 1px solid #30363D;
    margin-bottom: 32px;
  }}
  .logo {{ font-size: 22px; font-weight: 800; color: #2563EB; }}
  .meta {{ color: #8B949E; font-size: 13px; text-align: right; }}
  .score-hero {{
    text-align: center;
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 16px;
    padding: 40px;
    margin-bottom: 32px;
  }}
  .score-hero .score {{
    font-size: 72px;
    font-weight: 900;
    color: {ats_color};
    line-height: 1;
  }}
  .score-hero .label {{ color: #8B949E; font-size: 14px; margin-top: 8px; }}
  .section {{
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
  }}
  h2 {{
    color: #E6EDF3;
    font-size: 17px;
    font-weight: 700;
    margin-bottom: 16px;
  }}
  h3 {{ font-size: 13px; font-weight: 600; margin-bottom: 8px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th {{ color: #8B949E; font-size: 11px; text-transform: uppercase;
       letter-spacing: 0.5px; padding: 10px 12px; border-bottom: 1px solid #30363D; }}
  td {{ padding: 10px 12px; border-bottom: 1px solid #1C2128; }}
  .footer {{
    text-align: center;
    color: #484F58;
    font-size: 12px;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #30363D;
  }}
</style>
</head>
<body>

<div class="header">
  <div class="logo">🎯 ResumeAI</div>
  <div class="meta">
    <div style="font-size:15px; font-weight:700; color:#E6EDF3">{resume_name}</div>
    <div>Generated: {_now_str()}</div>
    {f'<div>Role: {jd.title}</div>' if jd else ''}
  </div>
</div>

<div class="score-hero">
  <div class="score">{ats_score}</div>
  <div class="label">ATS Score / 100</div>
</div>

<div class="section">
  <h2>Category Breakdown</h2>
  <table>
    <thead>
      <tr>
        <th style="text-align:left">Category</th>
        <th>Score</th>
        <th>Weight</th>
        <th>Progress</th>
      </tr>
    </thead>
    <tbody>{category_rows}</tbody>
  </table>
</div>

{keyword_html}
{grammar_html}
{suggestions_html}

<div class="footer">
  Generated by ResumeAI Platform &nbsp;·&nbsp; {_now_str()}
</div>

</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


# ─── Plain-Text Report ────────────────────────────────────────────────────────
def export_text(result: dict, output_path: str) -> str:
    """Generate a plain .txt summary report."""
    ats    = result.get("ats")
    resume = result.get("resume")
    match  = result.get("match")

    lines = [
        "=" * 60,
        "  ResumeAI Analysis Report",
        f"  Generated: {_now_str()}",
        "=" * 60,
        "",
    ]

    if ats:
        lines += [
            f"ATS Score: {ats.overall}/100",
            "",
            "Category Scores:",
            f"  Keyword Match   : {ats.keyword}/100  (30%)",
            f"  Formatting      : {ats.formatting}/100  (20%)",
            f"  Grammar         : {ats.grammar}/100  (15%)",
            f"  Resume Structure: {ats.structure}/100  (15%)",
            f"  Impact Writing  : {ats.impact}/100  (10%)",
            f"  ATS Compliance  : {ats.compliance}/100  (10%)",
            "",
        ]

    if match:
        lines += [
            f"Keyword Match: {match.match_pct:.1f}%",
            f"Matched: {', '.join(match.matched[:15])}",
            f"Missing: {', '.join(match.missing[:15])}",
            "",
        ]

    if ats and ats.improvements:
        lines += ["Recommendations:"]
        for tip in ats.improvements:
            lines.append(f"  → {tip}")
        lines.append("")

    if ats and ats.strengths:
        lines += ["Strengths:"]
        for s in ats.strengths:
            lines.append(f"  ✓ {s}")
        lines.append("")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path
