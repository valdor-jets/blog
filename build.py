#!/usr/bin/env python3
"""Builds blog.valdorjets.com into _site/ (no dependencies).

Articles live in <slug>/ folders (index.html, hero.jpg, meta.json), committed
by the Valdor content engine. This script adds the home page, the waitlist
page, the 404 page, feed.xml and sitemap.xml around them.
"""
from __future__ import annotations

import html
import json
import shutil
from datetime import date
from email.utils import format_datetime
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
OUT = ROOT / "_site"
BASE = "https://blog.valdorjets.com"
SKIP = {"_site", "assets", "templates", "waitlist", ".github", ".git"}


def articles() -> list[dict]:
    items = []
    for meta in ROOT.glob("*/meta.json"):
        if meta.parent.name in SKIP:
            continue
        m = json.loads(meta.read_text())
        m.setdefault("slug", meta.parent.name)
        m["hero"] = (meta.parent / "hero.jpg").exists()
        items.append(m)
    return sorted(items, key=lambda m: m.get("date", ""), reverse=True)


def human(d: str) -> str:
    try:
        x = date.fromisoformat(d[:10])
        return f"{x:%B} {x.day}, {x:%Y}"
    except ValueError:
        return d


def card(m: dict) -> str:
    img = (f'<img src="/{m["slug"]}/hero.jpg" alt="" loading="lazy">' if m["hero"]
           else '<div class="noimg"></div>')
    return (f'<a class="card" href="/{m["slug"]}/">{img}<div class="body">'
            f'<div class="date">{html.escape(human(m.get("date", "")))}</div>'
            f'<h3>{html.escape(m.get("title", ""))}</h3>'
            f'<p>{html.escape(m.get("description", ""))}</p></div></a>')


def page(name: str, **values: str) -> str:
    t = (ROOT / "templates" / name).read_text()
    for part in ("header", "footer"):
        t = t.replace("{{" + part + "}}", (ROOT / "templates" / f"_{part}.html").read_text())
    values.setdefault("year", str(date.today().year))
    for k, v in values.items():
        t = t.replace("{{" + k + "}}", v)
    return t


def feed(items: list[dict]) -> str:
    entries = []
    for m in items[:20]:
        try:
            pub = format_datetime(datetime.fromisoformat(m["date"][:10]).replace(tzinfo=timezone.utc))
        except (KeyError, ValueError):
            pub = ""
        url = f"{BASE}/{m['slug']}/"
        entries.append(f"<item><title>{html.escape(m.get('title', ''))}</title><link>{url}</link>"
                       f"<guid>{url}</guid><pubDate>{pub}</pubDate>"
                       f"<description>{html.escape(m.get('description', ''))}</description></item>")
    return ('<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>'
            f"<title>Valdor Jets Guides</title><link>{BASE}/</link>"
            "<description>Guides to private charter and empty-leg flights.</description>"
            + "".join(entries) + "</channel></rss>")


def sitemap(items: list[dict]) -> str:
    urls = [f"{BASE}/", f"{BASE}/waitlist/"] + [f"{BASE}/{m['slug']}/" for m in items]
    return ('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + "".join(f"<url><loc>{u}</loc></url>" for u in urls) + "</urlset>")


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    items = articles()
    for p in ROOT.iterdir():
        if p.name in SKIP or p.name in {"build.py", "README.md", "tests.py"}:
            continue
        if p.is_dir():
            shutil.copytree(p, OUT / p.name)
        else:
            shutil.copy2(p, OUT / p.name)
    shutil.copytree(ROOT / "assets", OUT / "assets")
    listing = ("".join(card(m) for m in items) if items else "")
    empty = "" if items else (
        '<div class="empty">Our first guides publish this week: how empty-leg flights work, '
        "what to know before you book a charter, and more. Join the waitlist and we'll send them to you.</div>")
    (OUT / "index.html").write_text(page("home.html", cards=listing, empty=empty))
    (OUT / "waitlist").mkdir()
    (OUT / "waitlist" / "index.html").write_text(page("waitlist.html"))
    (OUT / "404.html").write_text(page("404.html"))
    (OUT / "feed.xml").write_text(feed(items))
    (OUT / "sitemap.xml").write_text(sitemap(items))
    print(f"Built {len(items)} article(s) into {OUT}")


if __name__ == "__main__":
    main()
