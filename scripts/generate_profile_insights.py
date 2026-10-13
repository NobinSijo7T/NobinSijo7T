#!/usr/bin/env python3
"""Generate self-hosted SVG insight cards for a GitHub profile README.

Uses only Python's standard library and GitHub's public REST API.
The activity graph reflects public GitHub events returned by the API, not private
contributions or a complete contribution calendar.
"""

from __future__ import annotations

import html
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

USERNAME = os.environ.get("USERNAME", "NobinSijo7T")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "assets"

BG = "#0d1117"
PANEL = "#151b23"
BORDER = "#30363d"
TEXT = "#e6edf3"
MUTED = "#9da7b3"
ACCENT = "#a5b4fc"
PALETTE = ["#f78166", "#79c0ff", "#d2a8ff", "#7ee787", "#ffa657", "#ff9bce", "#a5b4fc"]
LANG_COLORS = {
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Python": "#3572A5",
    "Java": "#b07219", "HTML": "#e34c26", "CSS": "#563d7c",
    "C": "#555555", "C++": "#f34b7d", "C#": "#178600", "Jupyter Notebook": "#DA5B0B",
    "R": "#198CE7", "Go": "#00ADD8", "Rust": "#dea584", "PHP": "#4F5D95",
    "Shell": "#89e051", "Dart": "#00B4AB", "Kotlin": "#A97BFF", "Swift": "#F05138",
}


def api_json(path: str):
    url = "https://api.github.com/" + path.lstrip("/")
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": f"{USERNAME}-profile-readme-insights",
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
        raise RuntimeError(f"GitHub API returned HTTP {exc.code} for {url}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Could not reach GitHub API: {exc}") from exc


def safe(value) -> str:
    return html.escape(str(value or ""), quote=True)


def svg_start(width: int, height: int, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">'
        f'<title id="title">{safe(title)}</title>'
        '<desc id="desc">Automatically generated GitHub profile insights.</desc>'
        '<defs><linearGradient id="line" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{ACCENT}"/><stop offset="100%" stop-color="#79c0ff"/>'
        '</linearGradient></defs>'
        f'<rect width="100%" height="100%" rx="14" fill="{BG}"/>'
        f'<rect x="0.5" y="0.5" width="99%" height="99%" rx="14" fill="none" stroke="{BORDER}"/>'
    )


def text(x, y, value, size=13, color=TEXT, weight=400, extra="") -> str:
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" font-size="{size}" font-weight="{weight}" {extra}>{safe(value)}</text>'


def metric_card(profile, repos, updated_at):
    public_repos = [r for r in repos if not r.get("private") and not r.get("fork")]
    stars = sum(int(r.get("stargazers_count") or 0) for r in public_repos)
    forks = sum(int(r.get("forks_count") or 0) for r in public_repos)
    followers = int(profile.get("followers") or 0)
    following = int(profile.get("following") or 0)
    repo_count = int(profile.get("public_repos") or len(public_repos))
    metrics = [
        ("PUBLIC REPOSITORIES", f"{repo_count:,}", "#79c0ff"),
        ("STARS ON OWN REPOS", f"{stars:,}", "#f1e05a"),
        ("FORKS ON OWN REPOS", f"{forks:,}", "#d2a8ff"),
        ("FOLLOWERS", f"{followers:,}", "#7ee787"),
        ("FOLLOWING", f"{following:,}", "#ffa657"),
    ]
    out = [svg_start(760, 188, f"{USERNAME} profile insights")]
    out.append(text(24, 31, f"{USERNAME}  /  PROFILE INSIGHTS", 12, MUTED, 600, 'letter-spacing="1.2"'))
    out.append(text(736, 31, f"UPDATED {updated_at}", 10, MUTED, 500, 'text-anchor="end"'))
    x_positions = [24, 172, 320, 468, 616]
    for x, (label, value, color) in zip(x_positions, metrics):
        out.append(f'<rect x="{x}" y="48" width="132" height="108" rx="10" fill="{PANEL}" stroke="{BORDER}"/>')
        out.append(f'<rect x="{x}" y="48" width="132" height="3" rx="1.5" fill="{color}"/>')
        out.append(text(x + 12, 79, label, 9, MUTED, 600))
        out.append(text(x + 12, 119, value, 27, TEXT, 650))
    out.append(text(24, 176, "Counts cover public repositories owned by this account; forked repositories are excluded from star/fork totals.", 10, MUTED))
    out.append("</svg>")
    return "".join(out)


def language_card(repos, updated_at):
    public_repos = [r for r in repos if not r.get("private") and not r.get("fork")]
    counts = Counter((r.get("language") or "Other / not set") for r in public_repos)
    popular = counts.most_common(7)
    total = sum(counts.values()) or 1
    width, height = 520, 280
    out = [svg_start(width, height, "Public repositories by primary language")]
    out.append(text(22, 30, "LANGUAGE MIX", 12, MUTED, 600, 'letter-spacing="1.2"'))
    out.append(text(width - 22, 30, f"UPDATED {updated_at}", 10, MUTED, 500, 'text-anchor="end"'))
    if not public_repos:
        out.append(text(22, 85, "No public repositories were returned by the GitHub API.", 13, TEXT))
    else:
        y = 59
        for name, count in popular:
            ratio = count / total
            color = LANG_COLORS.get(name, PALETTE[len(out) % len(PALETTE)])
            out.append(text(22, y + 10, name, 12, TEXT, 500))
            out.append(text(width - 22, y + 10, f"{count} repo{'s' if count != 1 else ''}  ·  {ratio:.0%}", 11, MUTED, 500, 'text-anchor="end"'))
            out.append(f'<rect x="22" y="{y + 18}" width="{width - 44}" height="8" rx="4" fill="{BORDER}"/>')
            out.append(f'<rect x="22" y="{y + 18}" width="{(width - 44) * ratio:.2f}" height="8" rx="4" fill="{color}"/>')
            y += 27
    out.append(text(22, height - 13, "Based on each public, non-fork repository's primary language, not lines of code.", 9, MUTED))
    out.append("</svg>")
    return "".join(out)


def top_repos_card(repos, updated_at):
    public_repos = [r for r in repos if not r.get("private") and not r.get("fork")]
    top = sorted(public_repos, key=lambda r: (int(r.get("stargazers_count") or 0), int(r.get("forks_count") or 0)), reverse=True)[:5]
    width, height = 520, 260
    out = [svg_start(width, height, "Most starred public repositories")]
    out.append(text(22, 30, "REPOSITORY HIGHLIGHTS", 12, MUTED, 600, 'letter-spacing="1.2"'))
    out.append(text(width - 22, 30, f"UPDATED {updated_at}", 10, MUTED, 500, 'text-anchor="end"'))
    if not top:
        out.append(text(22, 85, "No public repositories were returned by the GitHub API.", 13, TEXT))
    y = 59
    for idx, repo in enumerate(top):
        name = repo.get("name", "Unnamed repository")
        lang = repo.get("language") or "Other / not set"
        stars = int(repo.get("stargazers_count") or 0)
        forks = int(repo.get("forks_count") or 0)
        full_name = repo.get("full_name") or f"{USERNAME}/{name}"
        url = safe(repo.get("html_url") or f"https://github.com/{full_name}")
        color = LANG_COLORS.get(lang, PALETTE[idx % len(PALETTE)])
        out.append(f'<a href="{url}"><rect x="20" y="{y - 13}" width="480" height="34" rx="7" fill="{PANEL}" stroke="{BORDER}"/></a>')
        out.append(f'<circle cx="34" cy="{y + 3}" r="4" fill="{color}"/>')
        out.append(text(46, y + 7, name[:33], 12, TEXT, 600))
        out.append(text(493, y + 7, f"★ {stars}   ⑂ {forks}", 10, MUTED, 500, 'text-anchor="end"'))
        y += 37
    out.append(text(22, height - 13, "Sorted by stars, then forks. Forked repositories are excluded.", 9, MUTED))
    out.append("</svg>")
    return "".join(out)


def activity_card(events, updated_at):
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=13)
    days = [start + timedelta(days=i) for i in range(14)]
    counts = Counter()
    kinds = Counter()
    for event in events:
        try:
            stamp = datetime.fromisoformat(event["created_at"].replace("Z", "+00:00")).date()
            if start <= stamp <= today:
                counts[stamp] += 1
                kinds[event.get("type") or "Other"] += 1
        except (KeyError, ValueError, TypeError):
            continue
    total_events = sum(counts.values())
    max_count = max(counts.values(), default=0) or 1
    width, height = 760, 235
    out = [svg_start(width, height, "Public GitHub activity over the last 14 days")]
    out.append(text(22, 30, "PUBLIC ACTIVITY · LAST 14 DAYS", 12, MUTED, 600, 'letter-spacing="1.1"'))
    out.append(text(width - 22, 30, f"{total_events} EVENTS  /  UPDATED {updated_at}", 10, MUTED, 500, 'text-anchor="end"'))
    chart_x, chart_y, chart_w, chart_h = 26, 56, 708, 113
    bar_gap = 10
    bar_w = (chart_w - 13 * bar_gap) / 14
    for i, day in enumerate(days):
        value = counts[day]
        bar_h = max(3, (value / max_count) * (chart_h - 10)) if value else 3
        x = chart_x + i * (bar_w + bar_gap)
        y = chart_y + chart_h - bar_h
        color = PALETTE[3] if value else BORDER
        out.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{bar_h:.2f}" rx="3" fill="{color}" opacity="{0.95 if value else 0.8}"/>')
        if i % 2 == 0 or i == 13:
            out.append(text(x + bar_w / 2, chart_y + chart_h + 18, day.strftime("%b %d"), 9, MUTED, 400, 'text-anchor="middle"'))
    out.append(f'<line x1="{chart_x}" y1="{chart_y + chart_h}" x2="{chart_x + chart_w}" y2="{chart_y + chart_h}" stroke="{BORDER}"/>')
    selected = kinds.most_common(4)
    kind_text = "  ·  ".join(f"{k.replace('Event','')}: {v}" for k, v in selected) if selected else "No public events returned in this period"
    out.append(text(22, 207, kind_text[:105], 10, TEXT, 500))
    out.append(text(22, 223, "Uses GitHub's recent public-events feed; this is not a complete contribution calendar and excludes private activity.", 9, MUTED))
    out.append("</svg>")
    return "".join(out)


def write_placeholder(path: Path, title: str, detail: str, width: int, height: int):
    svg = [svg_start(width, height, title)]
    svg.append(text(24, 35, title.upper(), 12, MUTED, 600, 'letter-spacing="1.1"'))
    svg.append(text(24, height // 2, "Waiting for the first GitHub Actions refresh", 16, TEXT, 600))
    svg.append(text(24, height // 2 + 28, detail, 11, MUTED))
    svg.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(svg), encoding="utf-8")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        profile = api_json(f"users/{urllib.parse.quote(USERNAME)}")
        repos = []
        for page in range(1, 11):
            batch = api_json(f"users/{urllib.parse.quote(USERNAME)}/repos?per_page=100&page={page}&type=owner&sort=updated")
            if not isinstance(batch, list):
                raise RuntimeError("GitHub repositories endpoint returned an unexpected response.")
            repos.extend(batch)
            if len(batch) < 100:
                break
        events = api_json(f"users/{urllib.parse.quote(USERNAME)}/events/public?per_page=100")
        if not isinstance(events, list):
            events = []
        updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d UTC")
        outputs = {
            "profile-insights.svg": metric_card(profile, repos, updated_at),
            "language-insights.svg": language_card(repos, updated_at),
            "top-repositories.svg": top_repos_card(repos, updated_at),
            "public-activity.svg": activity_card(events, updated_at),
        }
        for filename, data in outputs.items():
            (OUTPUT_DIR / filename).write_text(data, encoding="utf-8")
            print(f"Updated {filename}")
        return 0
    except Exception as exc:
        print(f"Could not refresh profile insights: {exc}", file=sys.stderr)
        print("Existing SVG cards have been left untouched.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
