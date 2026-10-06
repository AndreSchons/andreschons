#!/usr/bin/env python3
import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

USERNAME = os.getenv("GH_PROFILE_USER", "AndreSchons")
TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")

if not TOKEN:
    raise SystemExit("GH_TOKEN/GITHUB_TOKEN is required.")

today = datetime.now(timezone.utc).date()
to_dt = datetime(
    today.year, today.month, today.day, 23, 59, 59, tzinfo=timezone.utc
)
from_dt = to_dt - timedelta(days=364)

query = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    login
    name
    avatarUrl(size: 460)
    followers {
      totalCount
    }
    repositories(ownerAffiliations: OWNER, isFork: false) {
      totalCount
    }
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            contributionLevel
            weekday
          }
        }
      }
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalPullRequestReviewContributions
      restrictedContributionsCount
    }
  }
}
"""

payload = json.dumps(
    {
        "query": query,
        "variables": {
            "login": USERNAME,
            "from": from_dt.isoformat().replace("+00:00", "Z"),
            "to": to_dt.isoformat().replace("+00:00", "Z"),
        },
    }
).encode("utf-8")

req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "AndreSchons-profile-readme",
    },
    method="POST",
)

try:
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.load(response)
except urllib.error.HTTPError as exc:
    body = exc.read().decode("utf-8", errors="replace")
    raise SystemExit(f"GitHub GraphQL HTTP {exc.code}: {body}") from exc

if result.get("errors"):
    raise SystemExit(json.dumps(result["errors"], indent=2, ensure_ascii=False))

user = result.get("data", {}).get("user")
if not user:
    raise SystemExit(f"GitHub user not found: {USERNAME}")

out = {
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "user": {
        "login": user["login"],
        "name": user.get("name") or user["login"],
        "avatar_url": user["avatarUrl"],
        "followers": user["followers"]["totalCount"],
        "repositories": user["repositories"]["totalCount"],
    },
    "contributions": user["contributionsCollection"],
}

output_path = DATA / "github.json"
output_path.write_text(
    json.dumps(out, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print(f"Wrote {output_path}")
