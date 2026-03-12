#!/usr/bin/env python3
"""
Find recently-created GitHub repos with high star counts using the GitHub API.
Catches viral launches that web searches haven't indexed yet.

Usage:
    python find_viral_launches.py --days 30 --min-stars 5000 [--exclude projects-enriched.json]
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta


def search_github(query, sort="stars", order="desc", per_page=30):
    """Search GitHub repos via gh search."""
    result = subprocess.run(
        ["gh", "search", "repos", query,
         "--sort", sort, "--order", order,
         "--limit", str(per_page),
         "--json", "fullName,stargazersCount,createdAt,description"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"Error searching '{query}': {result.stderr.strip()}", file=sys.stderr)
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
            "description": item.get("description") or "",
        }
        for item in items
    ]


def main():
    parser = argparse.ArgumentParser(description="Find viral GitHub launches")
    parser.add_argument("--days", type=int, default=30,
                        help="Look back this many days (default: 30)")
    parser.add_argument("--min-stars", type=int, default=5000,
                        help="Minimum star count (default: 5000)")
    parser.add_argument("--exclude", default=None,
                        help="Path to projects-enriched.json to exclude already-tracked projects")
    args = parser.parse_args()

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

    # Search across AI-related topics
    queries = [
        f"created:>{cutoff} stars:>={args.min_stars} topic:ai",
        f"created:>{cutoff} stars:>={args.min_stars} topic:llm",
        f"created:>{cutoff} stars:>={args.min_stars} topic:machine-learning",
        f"created:>{cutoff} stars:>={args.min_stars} topic:agents",
        f"created:>{cutoff} stars:>={args.min_stars} topic:deep-learning",
        # Catch repos without topic tags — broad search filtered by star threshold
        f"created:>{cutoff} stars:>={args.min_stars} language:Python AI OR LLM OR agent OR model",
        f"created:>{cutoff} stars:>={args.min_stars} language:TypeScript AI OR LLM OR agent",
    ]

    seen = set()
    results = []

    for query in queries:
        repos = search_github(query)
        for repo in repos:
            name = repo["full_name"]
            url = f"https://github.com/{name}".lower()
            if name in seen:
                continue
            seen.add(name)

            already_tracked = url in excluded
            results.append({**repo, "already_tracked": already_tracked})

    # Sort by stars descending
    results.sort(key=lambda r: r["stars"], reverse=True)

    # Output
    new_finds = [r for r in results if not r["already_tracked"]]
    tracked = [r for r in results if r["already_tracked"]]

    if new_finds:
        print(f"\n🔥 NEW viral launches (created after {cutoff}, ≥{args.min_stars} stars, not yet tracked):\n")
        print(f"  {'Repository':<40} {'Stars':>8}  {'Created':>12}  Description")
        print(f"  {'-'*40} {'-'*8}  {'-'*12}  {'-'*40}")
        for r in new_finds:
            created = r["created_at"][:10]
            desc = r["description"][:50] + "..." if len(r["description"]) > 50 else r["description"]
            print(f"  {r['full_name']:<40} {r['stars']:>8,}  {created:>12}  {desc}")
    else:
        print(f"\nNo new viral launches found (created after {cutoff}, ≥{args.min_stars} stars).")

    if tracked:
        print(f"\n✓ Already tracked ({len(tracked)}):")
        for r in tracked:
            print(f"  {r['full_name']} ({r['stars']:,} stars)")

    print(f"\nTotal candidates: {len(results)} ({len(new_finds)} new, {len(tracked)} already tracked)")

    # Exit with code 1 if there are new finds (useful for CI/scripting)
    sys.exit(1 if new_finds else 0)


if __name__ == "__main__":
    main()
