#!/usr/bin/env python3
"""
Verify star counts in projects-enriched.json against live GitHub API data.
Flags and optionally fixes discrepancies > threshold%.

Usage:
    python verify_stars.py --input projects-enriched.json [--fix] [--threshold 10]
"""

import argparse
import json
import re
import subprocess
import sys
import time


def get_live_stars(repo_slug):
    """Fetch current stargazers_count via gh api."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo_slug}", "--jq", ".stargazers_count"],
        capture_output=True, text=True, timeout=15
    )
    if result.returncode != 0:
        return None, result.stderr.strip()
    return int(result.stdout.strip()), None


def main():
    parser = argparse.ArgumentParser(description="Verify star counts against GitHub API")
    parser.add_argument("--input", required=True, help="Path to projects-enriched.json")
    parser.add_argument("--fix", action="store_true", help="Auto-fix discrepancies in-place")
    parser.add_argument("--threshold", type=float, default=10.0,
                        help="Flag if actual differs by more than this %% (default: 10)")
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    mismatches = []
    errors = []

    for p in data:
        url = p.get("github_url", "")
        match = re.match(r"https://github\.com/([^/]+/[^/]+)", url)
        if not match:
            errors.append((p["name"], f"Bad URL: {url}"))
            continue

        repo = match.group(1)
        actual, err = get_live_stars(repo)

        if err:
            errors.append((p["name"], err))
            time.sleep(0.3)
            continue

        reported_k = p["stars"]
        actual_k = actual / 1000
        diff_pct = ((actual_k - reported_k) / reported_k * 100) if reported_k > 0 else 0

        if abs(diff_pct) > args.threshold:
            mismatches.append({
                "name": p["name"],
                "reported": reported_k,
                "actual": actual_k,
                "diff_pct": diff_pct,
            })
            if args.fix:
                p["stars"] = round(actual_k, 1)

        time.sleep(0.3)  # rate limit

    # Report
    if mismatches:
        print(f"\n{'Project':<30} {'Reported':>10} {'Actual':>10} {'Diff':>10}")
        print("-" * 65)
        for m in mismatches:
            print(f"{m['name']:<30} {m['reported']:>9.1f}K {m['actual']:>9.1f}K {m['diff_pct']:>+9.1f}%")
        print(f"\n{len(mismatches)} mismatches found (>{args.threshold}% threshold).")
    else:
        print(f"All {len(data)} projects within {args.threshold}% of live counts.")

    if errors:
        print(f"\n{len(errors)} errors:")
        for name, err in errors:
            print(f"  {name}: {err}")

    if args.fix and mismatches:
        with open(args.input, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nFixed {len(mismatches)} star counts in {args.input}.")

    sys.exit(1 if mismatches or errors else 0)


if __name__ == "__main__":
    main()
