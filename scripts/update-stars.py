"""Refresh star counts in README.md.

Replaces every `<!--stars:owner/repo-->N<!--/stars-->` marker with the
current stargazer count of owner/repo, formatted like 1.3k.
"""

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"
MARKER = re.compile(r"<!--stars:([\w.-]+/[\w.-]+)-->.*?<!--/stars-->")


def fetch_stars(repo: str) -> int:
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "readme-stars"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)["stargazers_count"]


def fmt(n: int) -> str:
    if n < 1000:
        return str(n)
    return f"{n / 1000:.1f}".rstrip("0").rstrip(".") + "k"


def main() -> int:
    text = README.read_text(encoding="utf-8")
    cache: dict[str, str] = {}

    def repl(m: re.Match) -> str:
        repo = m.group(1)
        if repo not in cache:
            cache[repo] = fmt(fetch_stars(repo))
            print(f"{repo}: {cache[repo]}")
        return f"<!--stars:{repo}-->{cache[repo]}<!--/stars-->"

    new = MARKER.sub(repl, text)
    if new != text:
        README.write_text(new, encoding="utf-8")
        print("README.md updated")
    else:
        print("No change")
    return 0


if __name__ == "__main__":
    sys.exit(main())
