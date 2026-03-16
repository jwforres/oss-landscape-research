#!/usr/bin/env python3
"""
Find viral GitHub repos in AI/ML using the GitHub API.

Two modes:
  1. New launches: recently-created repos with high star counts (default)
  2. Surging repos: older repos with high recent star velocity (--surge mode)

The surge mode catches relaunches/rewrites (e.g., DeerFlow v2) that go viral
but aren't new repos, so they'd be missed by creation-date filtering alone.

Usage:
    # New launches (repos created in last 30 days with ≥5K stars)
    python find_viral_launches.py --days 30 --min-stars 5000

    # Surging repos (any age, ≥10K stars, recently pushed)
    python find_viral_launches.py --surge --days 30 --min-stars 10000

    # Both modes together
    python find_viral_launches.py --days 30 --min-stars 5000 --surge --surge-min-stars 10000

    # Exclude already-tracked projects
    python find_viral_launches.py --days 30 --min-stars 5000 --surge --exclude projects-enriched.json
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta


def search_github(query="", sort="stars", order="desc", per_page=100, **flags):
    """Search GitHub repos via gh search.

    Use keyword arguments for filters instead of inline query qualifiers.
    The gh CLI ignores inline qualifiers like 'stars:>5000' — they must be
    passed as flags like --stars='>5000'.

    Supported flags: stars, created, updated, topic, language
    """
    cmd = ["gh", "search", "repos"]
    if query:
        cmd.append(query)
    cmd.extend(["--sort", sort, "--order", order,
                "--limit", str(per_page),
                "--json", "fullName,stargazersCount,createdAt,description,updatedAt"])

    # Map keyword args to gh CLI flags
    for key, value in flags.items():
        if value is not None:
            cmd.extend([f"--{key}", str(value)])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        flag_str = " ".join(f"--{k}={v}" for k, v in flags.items() if v)
        print(f"Error searching '{query} {flag_str}': {result.stderr.strip()}", file=sys.stderr)
        return []

    try:
        items = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []

    return [
        {
            "full_name": item["fullName"],
            "stars": item["stargazersCount"],
            "created_at": item["createdAt"],
            "updated_at": item.get("updatedAt", ""),
            "description": item.get("description") or "",
        }
        for item in items
    ]


def check_surge(repo_full_name, since_date, total_stars, lookback_stars=5000):
    """Check if a repo gained a large number of stars recently.

    Samples a stargazer page ~lookback_stars positions from the end.
    If that page's timestamps fall within the since_date window,
    the repo gained at least lookback_stars stars in that period — a surge.

    Single API call — total_stars is passed in from search results.
    """
    # Sample the page ~lookback_stars from the end
    # Each page = 100 stargazers, so go back lookback_stars/100 pages
    last_page = max(1, total_stars // 100)
    sample_page = max(1, last_page - (lookback_stars // 100))

    result = subprocess.run(
        ["gh", "api", f"repos/{repo_full_name}/stargazers?per_page=100&page={sample_page}",
         "-H", "Accept: application/vnd.github.star+json",
         "--jq", "[.[].starred_at]"],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        return None

    try:
        timestamps = json.loads(result.stdout)
    except (json.JSONDecodeError, ValueError):
        return None

    if not timestamps:
        return None

    # Check if the median timestamp on this page is after since_date
    mid_timestamp = timestamps[len(timestamps) // 2][:10]
    is_surging = mid_timestamp >= since_date

    return {
        "total_stars": total_stars,
        "sample_page": sample_page,
        "sample_date": mid_timestamp,
        "surging": is_surging,
        "estimated_recent_gain": f">{lookback_stars}" if is_surging else f"<{lookback_stars}",
    }


def find_new_launches(cutoff, min_stars, excluded):
    """Find recently-created repos with high star counts."""
    searches = [
        {"topic": "ai"},
        {"topic": "llm"},
        {"topic": "machine-learning"},
        {"topic": "agents"},
        {"topic": "deep-learning"},
        {"query": "AI OR LLM OR agent OR model", "language": "Python"},
        {"query": "AI OR LLM OR agent", "language": "TypeScript"},
    ]

    seen = set()
    results = []

    for search in searches:
        query = search.pop("query", "")
        repos = search_github(query, created=f">{cutoff}", stars=f">={min_stars}", **search)
        for repo in repos:
            name = repo["full_name"]
            url = f"https://github.com/{name}".lower()
            if name in seen:
                continue
            seen.add(name)
            already_tracked = url in excluded
            results.append({**repo, "already_tracked": already_tracked, "mode": "new_launch"})
        time.sleep(5)

    return results


def find_surging_repos(cutoff, min_stars, excluded):
    """Find older repos with high star counts that were recently active.

    Catches relaunches, major version rewrites, and projects that go viral
    long after initial creation (e.g., DeerFlow v2, a May 2025 repo that
    went #1 trending in Feb 2026 after a ground-up rewrite).

    Uses star-banded searches sorted by 'updated' to avoid being dominated
    by mega-repos (PyTorch, TensorFlow) that push smaller surging repos
    out of the result set. Limits total queries to stay within GitHub's
    secondary rate limit (~30 requests/minute for search).
    """
    # Star bands ensure we don't just get the top 30 biggest repos.
    # Two bands: one for mid-range (where DeerFlow-class projects live)
    # and one for large repos. Keeps total query count manageable.
    star_bands = [
        f"{min_stars}..50000",
        "50000..500000",
    ]

    # Key topics to search — each is a separate API call
    topics = ["ai", "llm", "agents", "machine-learning"]

    seen = set()
    candidates = []

    for star_range in star_bands:
        for topic in topics:
            repos = search_github(sort="updated", updated=f">{cutoff}",
                                  stars=star_range, topic=topic)
            for repo in repos:
                name = repo["full_name"]
                if name in seen:
                    continue
                seen.add(name)
                candidates.append(repo)
            time.sleep(5)
        # Also a broad language-based search per band
        repos = search_github("AI OR LLM OR agent", sort="updated",
                              updated=f">{cutoff}", stars=star_range,
                              language="Python")
        for repo in repos:
            name = repo["full_name"]
            if name in seen:
                continue
            seen.add(name)
            candidates.append(repo)
        time.sleep(5)

    # Check for genuine surges (gained >5K stars in lookback window)
    results = []
    print(f"\n🔍 Checking surge signal for {len(candidates)} candidates...", file=sys.stderr)

    for i, repo in enumerate(candidates):
        name = repo["full_name"]
        url = f"https://github.com/{name}".lower()
        already_tracked = url in excluded

        surge = check_surge(name, cutoff, repo["stars"])
        if surge and surge["surging"]:
            results.append({
                **repo,
                "already_tracked": already_tracked,
                "mode": "surge",
                "surge_info": surge,
            })
        # Pace REST API calls — 1 call per repo
        time.sleep(0.5)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Find viral GitHub launches and surging repos in AI/ML")
    parser.add_argument("--days", type=int, default=30,
                        help="Look back this many days (default: 30)")
    parser.add_argument("--min-stars", type=int, default=5000,
                        help="Minimum star count for new launches (default: 5000)")
    parser.add_argument("--surge", action="store_true",
                        help="Also search for surging older repos (relaunch detection)")
    parser.add_argument("--surge-min-stars", type=int, default=None,
                        help="Minimum star count for surge mode (default: same as --min-stars)")
    parser.add_argument("--exclude", default=None,
                        help="Path to projects-enriched.json to exclude already-tracked projects")
    args = parser.parse_args()

    if args.surge_min_stars is None:
        args.surge_min_stars = args.min_stars

    cutoff = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    # Load exclusion set
    excluded = set()
    if args.exclude:
        try:
            with open(args.exclude) as f:
                data = json.load(f)
            excluded = {p["github_url"].rstrip("/").lower() for p in data}
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    # --- Mode 1: New launches ---
    results = find_new_launches(cutoff, args.min_stars, excluded)

    # --- Mode 2: Surging repos (relaunch detection) ---
    surge_results = []
    if args.surge:
        surge_results = find_surging_repos(cutoff, args.surge_min_stars, excluded)
        # Deduplicate against new launches
        launch_names = {r["full_name"] for r in results}
        surge_results = [r for r in surge_results if r["full_name"] not in launch_names]

    all_results = results + surge_results
    all_results.sort(key=lambda r: r["stars"], reverse=True)

    new_finds = [r for r in all_results if not r["already_tracked"]]
    tracked = [r for r in all_results if r["already_tracked"]]

    # Output: New launches
    launch_finds = [r for r in new_finds if r["mode"] == "new_launch"]
    if launch_finds:
        print(f"\n🔥 NEW viral launches (created after {cutoff}, ≥{args.min_stars} stars, not yet tracked):\n")
        print(f"  {'Repository':<40} {'Stars':>8}  {'Created':>12}  Description")
        print(f"  {'-'*40} {'-'*8}  {'-'*12}  {'-'*40}")
        for r in launch_finds:
            created = r["created_at"][:10]
            desc = r["description"][:50] + "..." if len(r["description"]) > 50 else r["description"]
            print(f"  {r['full_name']:<40} {r['stars']:>8,}  {created:>12}  {desc}")
    else:
        print(f"\nNo new viral launches found (created after {cutoff}, ≥{args.min_stars} stars).")

    # Output: Surging repos
    surge_finds = [r for r in new_finds if r["mode"] == "surge"]
    if surge_finds:
        print(f"\n🚀 SURGING repos (older repos with recent star velocity spike, not yet tracked):\n")
        print(f"  {'Repository':<40} {'Stars':>8}  {'Created':>12}  {'Velocity':>10}  Description")
        print(f"  {'-'*40} {'-'*8}  {'-'*12}  {'-'*10}  {'-'*40}")
        for r in surge_finds:
            created = r["created_at"][:10]
            surge = r.get("surge_info", {})
            gain_str = surge.get("estimated_recent_gain", "?")
            desc = r["description"][:40] + "..." if len(r["description"]) > 40 else r["description"]
            print(f"  {r['full_name']:<40} {r['stars']:>8,}  {created:>12}  {gain_str:>10}  {desc}")

    if tracked:
        print(f"\n✓ Already tracked ({len(tracked)}):")
        for r in tracked:
            print(f"  {r['full_name']} ({r['stars']:,} stars)")

    total_new = len(launch_finds) + len(surge_finds)
    print(f"\nTotal candidates: {len(all_results)} ({total_new} new, {len(tracked)} already tracked)")

    sys.exit(0)


if __name__ == "__main__":
    main()
