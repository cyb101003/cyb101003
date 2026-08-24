#!/usr/bin/env python3
"""Generate dependency-free SVG cards for the GitHub profile README."""

from __future__ import annotations

import html
import json
import os
import subprocess
from pathlib import Path

USERNAME = "cyb101003"
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SELECTED = {
    "echo-blog": "repo-echo-blog.svg",
    "rednote-tools": "repo-rednote-tools.svg",
    "web3-learning-notes": "repo-web3-learning-notes.svg",
}
COLORS = {
    "CSS": "#663399",
    "HTML": "#e34c26",
    "JavaScript": "#f1e05a",
    "Python": "#3572A5",
    "Solidity": "#AA6746",
    "TypeScript": "#3178c6",
}


def api(path: str):
    command = [
        "curl",
        "--fail",
        "--silent",
        "--show-error",
        "--header",
        "Accept: application/vnd.github+json",
        "--header",
        "User-Agent: cyb101003-profile-card-generator",
        "--header",
        "X-GitHub-Api-Version: 2022-11-28",
    ]
    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        command.extend(["--header", f"Authorization: Bearer {token}"])
    command.append(f"https://api.github.com{path}")
    return json.loads(subprocess.check_output(command, text=True))


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def trim(value: str | None, limit: int = 68) -> str:
    text = " ".join((value or "Public repository · open for exploration.").split())
    return text if len(text) <= limit else f"{text[: limit - 1].rstrip()}…"


def base_svg(body: str, *, width: int = 620, height: int = 150, label: str) -> str:
    body = body.lstrip("\n")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(label)}">
  <rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="#0d1117" stroke="#21262d"/>
  <path d="M12 1H608" stroke="#30363d"/>
  {body}
</svg>
'''


def repo_card(repo: dict) -> str:
    language = (repo.get("language") or "Other").strip()
    language_color = COLORS.get(language, "#8b949e")
    updated = (repo.get("updated_at") or "")[:10]
    body = f'''
  <text x="26" y="39" fill="#f0f6fc" font-size="19" font-weight="650" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">{esc(repo["name"])}</text>
  <text x="518" y="38" fill="#6e7681" font-size="10" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" letter-spacing="1">PUBLIC REPO</text>
  <text x="26" y="70" fill="#8b949e" font-size="13" font-family="ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif">{esc(trim(repo.get("description")))}</text>
  <path d="M26 94H594" stroke="#21262d"/>
  <circle cx="31" cy="119" r="4" fill="{language_color}"/>
  <text x="42" y="123" fill="#8b949e" font-size="12" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">{esc(language)}</text>
  <text x="180" y="123" fill="#6e7681" font-size="12" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">★ {repo.get("stargazers_count", 0)}</text>
  <text x="246" y="123" fill="#6e7681" font-size="12" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">⑂ {repo.get("forks_count", 0)}</text>
  <text x="458" y="123" fill="#484f58" font-size="11" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">UPDATED {esc(updated)}</text>'''
    return base_svg(body, label=f"{repo['name']} repository card")


def stats_card(profile: dict, repos: list[dict]) -> str:
    owned = [repo for repo in repos if not repo.get("fork")]
    stars = sum(repo.get("stargazers_count", 0) for repo in owned)
    forks = sum(repo.get("forks_count", 0) for repo in owned)
    metrics = [
        ("PUBLIC BUILDS", len(owned), 34),
        ("STARS", stars, 183),
        ("FORKS", forks, 309),
        ("FOLLOWERS", profile.get("followers", 0), 430),
    ]
    metric_svg = "".join(
        f'<text x="{x}" y="84" fill="#f0f6fc" font-size="25" font-weight="700" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">{value}</text>'
        f'<text x="{x}" y="105" fill="#6e7681" font-size="10" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" letter-spacing="0.8">{label}</text>'
        for label, value, x in metrics
    )
    body = f'''
  <text x="26" y="38" fill="#f0f6fc" font-size="18" font-weight="650" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">GITHUB SIGNAL</text>
  <text x="508" y="37" fill="#6e7681" font-size="10" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" letter-spacing="1">LIVE DATA</text>
  <path d="M26 51H594" stroke="#21262d"/>
  {metric_svg}
  <text x="26" y="132" fill="#484f58" font-size="11" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">Generated from the GitHub API · @{USERNAME}</text>'''
    return base_svg(body, label="Echo GitHub statistics")


def language_card(language_bytes: dict[str, int]) -> str:
    ranked = sorted(language_bytes.items(), key=lambda item: item[1], reverse=True)[:5]
    total = sum(value for _, value in ranked) or 1
    x = 30.0
    segments = []
    labels = []
    for index, (language, value) in enumerate(ranked):
        width = 560 * value / total
        color = COLORS.get(language, "#8b949e")
        segments.append(f'<rect x="{x:.1f}" y="58" width="{max(width, 2):.1f}" height="8" fill="{color}"/>')
        lx = 30 + (index % 3) * 190
        ly = 98 + (index // 3) * 25
        percent = round(100 * value / total)
        labels.append(f'<circle cx="{lx + 4}" cy="{ly - 4}" r="4" fill="{color}"/><text x="{lx + 15}" y="{ly}" fill="#8b949e" font-size="11" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">{esc(language)} {percent}%</text>')
        x += width
    body = f'''
  <text x="26" y="38" fill="#f0f6fc" font-size="18" font-weight="650" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">LANGUAGE MIX</text>
  <text x="477" y="37" fill="#6e7681" font-size="10" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" letter-spacing="1">PUBLIC BUILDS</text>
  <rect x="30" y="58" width="560" height="8" rx="4" fill="#21262d"/>
  {''.join(segments)}
  {''.join(labels)}'''
    return base_svg(body, label="Echo most used repository languages")


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    profile = api(f"/users/{USERNAME}")
    repos = api(f"/users/{USERNAME}/repos?per_page=100&sort=updated")
    by_name = {repo["name"]: repo for repo in repos}
    missing = sorted(set(SELECTED) - set(by_name))
    if missing:
        raise SystemExit(f"Missing selected repositories: {', '.join(missing)}")
    for name, filename in SELECTED.items():
        (ASSETS / filename).write_text(repo_card(by_name[name]), encoding="utf-8")

    language_bytes: dict[str, int] = {}
    for repo in repos:
        if repo.get("fork"):
            continue
        for language, count in api(f"/repos/{USERNAME}/{repo['name']}/languages").items():
            language_bytes[language] = language_bytes.get(language, 0) + count

    (ASSETS / "stats.svg").write_text(stats_card(profile, repos), encoding="utf-8")
    (ASSETS / "languages.svg").write_text(language_card(language_bytes), encoding="utf-8")
    print(f"Generated {len(SELECTED) + 2} cards for @{USERNAME}.")


if __name__ == "__main__":
    main()
