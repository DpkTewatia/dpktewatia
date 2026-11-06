"""Refresh the "Recent writing" list in README.md from my C# Corner profile.

C# Corner has no per-member RSS feed, so this reads the public profile page
and takes the first article links it lists. If the page layout changes and
nothing is found, the README is left untouched.
"""
import html
import re
import sys
import urllib.request
from pathlib import Path

PROFILE = "https://www.c-sharpcorner.com/members/deepak-tewatia"
BASE = "https://www.c-sharpcorner.com"
LIMIT = 5
UTM = "?utm_source=github&utm_medium=profile_readme&utm_campaign=github_profile&utm_content=writing"
START, END = "<!-- CSC-ARTICLES:START -->", "<!-- CSC-ARTICLES:END -->"
README = Path(__file__).resolve().parents[2] / "README.md"

ARTICLE = re.compile(
    r'<a href="(/article/[a-z0-9-]+)"><h3 class="post-title[^"]*">([^<]+)</h3></a>'
)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (profile-readme-updater)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def main() -> int:
    page = fetch(PROFILE)
    seen, items = set(), []
    for path, title in ARTICLE.findall(page):
        if path in seen:
            continue
        seen.add(path)
        items.append(f"- [{html.unescape(title).strip()}]({BASE}{path}{UTM})")
        if len(items) == LIMIT:
            break

    if not items:
        print("No articles found; leaving README unchanged.")
        return 0

    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        print("Markers not found in README.md", file=sys.stderr)
        return 1

    block = f"{START}\n" + "\n".join(items) + f"\n{END}"
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    if new != text:
        README.write_text(new, encoding="utf-8")
        print(f"Updated README with {len(items)} articles.")
    else:
        print("README already up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
