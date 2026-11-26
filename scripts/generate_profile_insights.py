
    
  
    width, height = 520, 306
    out = [svg_start(width, height, "Most starred public repositories")]
    out.append(f'<circle cx="25" cy="28" r="4" fill="url(#accent)"/>')
    out.append(text(38, 32, "REPOSITORY HIGHLIGHTS", 11, MUTED, 700, 'letter-spacing="1.2"'))
    out.append(text(width - 20, 32, f"UPDATED  {updated_at}", 9, MUTED, 600, 'text-anchor="end" letter-spacing="0.5"'))
    out.append(text(22, 53, "Your most-starred public projects", 10, MUTED, 400))
    if not top:
        out.append(f'<rect x="20" y="75" width="480" height="190" rx="12" fill="{SURFACE}" stroke="{BORDER}"/>')
        out.append(text(width / 2, 163, "No public repositories found", 14, TEXT, 600, 'text-anchor="middle"'))
        out.append(text(width / 2, 184, "Project highlights will appear after the next refresh.", 10, MUTED, 400, 'text-anchor="middle"'))
    y = 78
    for idx, repo in enumerate(top):
        name = repo.get("name", "Unnamed repository")
        lang = repo.get("language") or "Other / not set"
        stars = int(repo.get("stargazers_count") or 0)
        forks = int(repo.get("forks_count") or 0)
        full_name = repo.get("full_name") or f"{USERNAME}/{name}"
        url = safe(repo.get("html_url") or f"https://github.com/{full_name}")
        color = LANG_COLORS.get(lang, PALETTE[idx % len(PALETTE)])
        out.append(f'<a href="{url}">')
        out.append(f'<rect x="20" y="{y}" width="480" height="36" rx="9" fill="{SURFACE}" stroke="{BORDER}"/>')
        out.append(f'<rect x="20" y="{y}" width="3" height="36" rx="1.5" fill="{color}"/>')
        out.append(text(33, y + 22, f"{idx + 1:02d}", 9, MUTED, 700))
        out.append(text(60, y + 22, name[:31], 11, TEXT, 650))
        out.append(text(402, y + 22, f"STARS  {stars}", 9, MUTED, 650, 'text-anchor="end" letter-spacing="0.25"'))
        out.append(text(482, y + 22, f"FORKS  {forks}", 9, MUTED, 650, 'text-anchor="end" letter-spacing="0.25"'))
        out.append('</a>')
        y += 40
    out.append(f'<line x1="20" y1="284" x2="500" y2="284" stroke="{BORDER}"/>')
    out.append(text(22, 299, "Ranked by stars, then forks. Forked repositories are excluded.", 9, MUTED, 400))
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
    width, height = 760, 278
    out = [svg_start(width, height, "Public GitHub activity over the last 14 days")]
    out.append(f'<circle cx="27" cy="28" r="4" fill="url(#accent)"/>')
    out.append(text(40, 32, "PUBLIC ACTIVITY", 11, MUTED, 700, 'letter-spacing="1.2"'))
    out.append(text(40, 50, "Your public GitHub events over the last 14 days", 10, MUTED, 400))
    out.append(f'<rect x="594" y="17" width="142" height="25" rx="12.5" fill="{SURFACE}" stroke="{BORDER}"/>')
    out.append(f'<circle cx="609" cy="29.5" r="3" fill="url(#accent)"/>')
    out.append(text(621, 33, f"{total_events} EVENTS", 9, TEXT, 700, 'letter-spacing="0.5"'))
    out.append(text(736, 54, f"UPDATED  {updated_at}", 8, MUTED, 500, 'text-anchor="end"'))
    chart_x, chart_y, chart_w, chart_h = 28, 78, 704, 108
    bar_gap = 10
    bar_w = (chart_w - 13 * bar_gap) / 14
    for grid_fraction in (0, 0.5, 1):
        grid_y = chart_y + chart_h * grid_fraction
        out.append(f'<line x1="{chart_x}" y1="{grid_y:.2f}" x2="{chart_x + chart_w}" y2="{grid_y:.2f}" stroke="{BORDER}" stroke-dasharray="3 6" opacity="0.8"/>')
    for i, day in enumerate(days):
        value = counts[day]
        bar_h = max(3, (value / max_count) * (chart_h - 9)) if value else 3
        x = chart_x + i * (bar_w + bar_gap)
        y = chart_y + chart_h - bar_h
        if value:
            out.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{bar_h:.2f}" rx="4" fill="url(#barGlow)"/>')
        else:
            out.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_w:.2f}" height="{bar_h:.2f}" rx="4" fill="{BORDER}" opacity="0.8"/>')
        if i % 2 == 0 or i == 13:
            out.append(text(x + bar_w / 2, 207, day.strftime("%b %d"), 8.5, MUTED, 500, 'text-anchor="middle"'))
    selected = kinds.most_common(4)
    kind_text = "  ·  ".join(f"{k.replace('Event','')}: {v}" for k, v in selected) if selected else "No public events returned in this period"
    out.append(f'<line x1="22" y1="222" x2="738" y2="222" stroke="{BORDER}"/>')
    out.append(text(22, 242, kind_text[:105], 10, TEXT, 600))
    out.append(text(22, 262, "GitHub public-events feed only. Private activity and a complete contribution calendar are not included.", 9, MUTED, 400))
    out.append("</svg>")
    return "".join(out)


def write_placeholder(path: Path, title: str, detail: str, width: int, height: int):
    svg = [svg_start(width, height, title)]
    svg.append(f'<circle cx="28" cy="28" r="4" fill="url(#accent)"/>')
    svg.append(text(41, 32, title.upper(), 11, MUTED, 700, 'letter-spacing="1.2"'))
    svg.append(f'<rect x="20" y="58" width="{width - 40}" height="{height - 82}" rx="12" fill="{SURFACE}" stroke="{BORDER}"/>')
    svg.append(text(width / 2, height // 2 - 5, "Waiting for the first refresh", 15, TEXT, 650, 'text-anchor="middle"'))
    svg.append(text(width / 2, height // 2 + 20, detail, 10, MUTED, 400, 'text-anchor="middle"'))
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

