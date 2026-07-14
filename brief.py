"""Your morning brief pipeline. You never need to edit this file.

What it does, in order:
  1. Reads your settings from config.yml and your instructions from prompt.txt
  2. Downloads the headlines from your three feeds
  3. Sends the headlines plus your instructions to Claude
  4. Emails you the brief Claude wrote

If anything goes wrong, it prints a plain-English message telling you
exactly what to fix.
"""

import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

import requests
import yaml

# The Claude model this workshop edition uses. Pinned on purpose so all
# fifty forks behave identically. Maintainer: see MAINTAINERS.md before
# changing this.
CLAUDE_MODEL = "claude-sonnet-5"

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
RESEND_URL = "https://api.resend.com/emails"
FEED_TIMEOUT = 20        # seconds per feed download
ITEMS_PER_FEED = 12      # headlines taken from each feed


def die(message: str) -> None:
    """Print a fix-it message a non-technical person can act on, then stop."""
    print()
    print("=" * 70)
    print("SOMETHING NEEDS YOUR ATTENTION")
    print("=" * 70)
    print(message)
    print("=" * 70)
    # The ::error:: line makes GitHub show the first sentence in red at
    # the top of the run page.
    print(f"::error::{message.splitlines()[0]}")
    sys.exit(1)


def load_config() -> dict:
    """Read config.yml and check the two things it must contain."""
    try:
        with open("config.yml", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        die("config.yml is missing. It should be in the main folder of your "
            "repository, next to this file. If you renamed or moved it, "
            "rename it back to exactly: config.yml")
    except yaml.YAMLError as exc:
        die("config.yml could not be read. This usually means a quote or "
            "dash got deleted while editing.\n"
            "Open config.yml and check that every feed line looks exactly "
            'like:  - "https://example.com/feed/"\n'
            "and the email line looks exactly like:  email: \"you@example.com\"\n"
            f"Technical detail: {exc}")

    feeds = [u for u in (config.get("feeds") or []) if u and str(u).strip()]
    if not feeds:
        die("No feeds found in config.yml. Add at least one line under "
            '"feeds:" that looks like:  - "https://example.com/feed/"')

    email = str(config.get("email") or "").strip()
    if not email or "@" not in email or email == "you@example.com":
        die("Your email address is not set yet. Open config.yml and replace "
            'you@example.com with your real address, keeping the quotes:\n'
            '  email: "yourname@gmail.com"\n'
            "Use the SAME address you signed up to Resend with.")

    return {"feeds": feeds, "email": email}


def load_prompt() -> str:
    """Read prompt.txt, dropping the # comment lines meant for humans."""
    try:
        with open("prompt.txt", encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        die("prompt.txt is missing. It should be in the main folder of your "
            "repository. If you renamed or moved it, rename it back to "
            "exactly: prompt.txt")

    prompt = "\n".join(
        line for line in lines if not line.lstrip().startswith("#")).strip()
    if not prompt:
        die("prompt.txt is empty (or only contains # comment lines). Put the "
            "instructions back, or re-copy the file from the workshop "
            "repository: github.com/hfscdogg/integrateuworkshops")
    return prompt


def fetch_feed(url: str) -> list[dict]:
    """Download one RSS or Atom feed and return its headlines.

    Returns a list of {"title", "summary", "link"} dicts. Problems are
    printed as warnings; the run continues with the other feeds.
    """
    try:
        resp = requests.get(url, timeout=FEED_TIMEOUT, headers={
            "User-Agent": "Mozilla/5.0 (Workshop Intel Scout)",
        })
    except requests.RequestException as exc:
        print(f"WARNING: could not reach {url}\n"
              f"  The site may be down, or the address has a typo. "
              f"Open the address in your browser to check. ({exc})")
        return []

    if resp.status_code != 200:
        print(f"WARNING: {url} answered with code {resp.status_code} "
              f"instead of content. Open the address in your browser: you "
              f"should see raw code full of <item> or <entry> tags. If you "
              f"see a normal webpage, this is not an RSS feed address.")
        return []

    try:
        root = ET.fromstring(resp.content)
    except ET.ParseError:
        print(f"WARNING: {url} did not return a readable feed. Open it in "
              f"your browser: an RSS feed looks like raw code full of "
              f"<item> tags. If you see a normal webpage, look for an "
              f"'RSS' link on that site and use that address instead.")
        return []

    items = []
    # RSS 2.0: <channel><item><title/link/description>
    for item in root.iter("item"):
        items.append({
            "title": (item.findtext("title") or "").strip(),
            "summary": (item.findtext("description") or "").strip()[:300],
            "link": (item.findtext("link") or "").strip(),
        })
    # Atom: <entry><title/summary/link href=...>
    atom = "{http://www.w3.org/2005/Atom}"
    for entry in root.iter(f"{atom}entry"):
        link_el = entry.find(f"{atom}link")
        items.append({
            "title": (entry.findtext(f"{atom}title") or "").strip(),
            "summary": (entry.findtext(f"{atom}summary")
                        or entry.findtext(f"{atom}content") or "").strip()[:300],
            "link": (link_el.get("href", "") if link_el is not None else ""),
        })

    items = [i for i in items if i["title"]][:ITEMS_PER_FEED]
    print(f"OK: {len(items)} headline(s) from {url}")
    return items


def ask_claude(prompt: str, headlines: list[dict]) -> str:
    """Send the headlines plus your instructions to Claude, return the brief."""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        die("Your ANTHROPIC_API_KEY secret wasn't found. Check the name is "
            "exact: all caps, underscores, no spaces. Add it under "
            "Settings > Secrets and variables > Actions > New repository "
            "secret, in YOUR fork (not the original repository).")

    numbered = "\n".join(
        f"{n}. {i['title']}\n   {i['summary']}\n   Link: {i['link']}"
        for n, i in enumerate(headlines, 1)
    )
    message = f"{prompt}\n\nHere are today's headlines:\n\n{numbered}"

    try:
        resp = requests.post(
            ANTHROPIC_URL,
            timeout=120,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": CLAUDE_MODEL,
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": message}],
            },
        )
    except requests.RequestException as exc:
        die(f"Could not reach Claude's servers. This is usually temporary: "
            f"wait one minute and press Run workflow again. ({exc})")

    if resp.status_code == 401:
        die("Claude rejected your API key. The ANTHROPIC_API_KEY secret "
            "exists but its value is wrong. Common causes: extra spaces "
            "pasted around the key, or an incomplete copy. Create a fresh "
            "key at console.anthropic.com > API keys, then update the "
            "secret under Settings > Secrets and variables > Actions.")

    if resp.status_code == 400 and "credit" in resp.text.lower():
        die("Your Anthropic account is out of credit, so Claude cannot "
            "answer. Go to console.anthropic.com > Billing and add credit "
            "(5 dollars is plenty for months of daily briefs), then press "
            "Run workflow again.")

    if resp.status_code == 429:
        die("Claude is rate limiting requests right now. Wait one minute "
            "and press Run workflow again.")

    if resp.status_code != 200:
        die(f"Claude answered with an unexpected error (code "
            f"{resp.status_code}). Wait a minute and press Run workflow "
            f"again. If it keeps happening, ask for help and share this: "
            f"{resp.text[:300]}")

    brief = "".join(
        block.get("text", "")
        for block in resp.json().get("content", [])
    ).strip()
    if not brief:
        die("Claude answered but the brief came back empty. Press Run "
            "workflow to try again.")
    return brief


def send_email(brief: str, recipient: str) -> None:
    """Deliver the brief to your inbox through Resend."""
    api_key = os.environ.get("RESEND_API_KEY", "").strip()
    if not api_key:
        die("Your RESEND_API_KEY secret wasn't found. Check the name is "
            "exact: all caps, underscores, no spaces. Get the key from "
            "resend.com > API Keys, then add it under Settings > Secrets "
            "and variables > Actions > New repository secret in YOUR fork.")

    today = datetime.now().strftime("%B %d, %Y")
    try:
        resp = requests.post(
            RESEND_URL,
            timeout=30,
            headers={"Authorization": f"Bearer {api_key}",
                     "Content-Type": "application/json"},
            json={
                "from": "Intel Scout <onboarding@resend.dev>",
                "to": [recipient],
                "subject": f"Your Morning Brief for {today}",
                "text": brief,
            },
        )
    except requests.RequestException as exc:
        die(f"Could not reach the email service. This is usually temporary: "
            f"wait one minute and press Run workflow again. ({exc})")

    if resp.status_code in (401, 403) and "testing" not in resp.text.lower():
        die("The email service rejected your RESEND_API_KEY. Create a fresh "
            "key at resend.com > API Keys and update the secret under "
            "Settings > Secrets and variables > Actions.")

    if resp.status_code != 200:
        body = resp.text.lower()
        if "testing" in body or "own email" in body or "verify" in body:
            die(f"Resend refused to deliver to {recipient}. On the free "
                f"plan, Resend only delivers to the email address you "
                f"signed up with. Open config.yml and set the email line "
                f"to the exact address on your Resend account.")
        die(f"The email service answered with an unexpected error (code "
            f"{resp.status_code}). Wait a minute and press Run workflow "
            f"again. If it keeps happening, ask for help and share this: "
            f"{resp.text[:300]}")

    print(f"OK: brief emailed to {recipient}")


def main() -> None:
    print("Step 1 of 4: reading your settings...")
    config = load_config()
    prompt = load_prompt()

    print("Step 2 of 4: downloading your feeds...")
    headlines = []
    for url in config["feeds"]:
        headlines.extend(fetch_feed(url))

    if not headlines:
        die("None of your feeds returned any headlines, so there is nothing "
            "to brief you on. Check each feed address in config.yml by "
            "opening it in your browser: you should see raw code full of "
            "<item> tags. Replace any address that shows a normal webpage "
            "or an error.")
    print(f"Collected {len(headlines)} headline(s) total.")

    print("Step 3 of 4: asking Claude for your brief...")
    brief = ask_claude(prompt, headlines)
    print()
    print("-" * 70)
    print(brief)
    print("-" * 70)
    print()

    print("Step 4 of 4: emailing it to you...")
    send_email(brief, config["email"])
    print()
    print("All done. Check your inbox (and the spam folder, the first time).")


if __name__ == "__main__":
    main()
