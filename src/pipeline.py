#!/usr/bin/env python3

"""
Generate RSS feed of events from Fundación Japón Madrid.

Strategy
--------

The website does not expose an API or RSS feed. Events are listed
directly in the HTML of section pages under /Actividades.

Each section page contains links of the form:

    /es/Actividades/<section>/evento/<id>/<slug>

This script:

1. downloads each section page
2. extracts event URLs
3. visits each event page
4. extracts title and description
5. writes an RSS feed

All downloaded HTML pages are stored in /data for debugging and
inspection.
"""

import requests
import re
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

BASE = "https://md.jpf.go.jp"

SECTIONS = [
    "/es/Actividades/Arte-y-Cultura",
    "/es/Actividades/Lengua-Japonesa",
    "/es/Actividades/Estudios-Japoneses",
    "/es/Actividades/Biblioteca",
    "/es/Actividades/Eventos-organizados-por-otras-instituciones",
]

HEADERS = {
    "User-Agent": "jpf-event-rss-bot/1.0"
}

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)


def clean_text(text):
    """Normalize whitespace for RSS-friendly text."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def extract_description(soup):
    """
    Extract event description from known page structures.
    """
    # Preferred container when available.
    candidates = [
        soup.find("div", class_="entry-content"),
        soup.select_one("div#content div.col-md-9"),
        soup.select_one("div.main div.col-md-9"),
    ]

    for node in candidates:
        if not node:
            continue
        text = clean_text(node.get_text(" ", strip=True))
        if text:
            # Keep feed entries readable and reasonably sized.
            return text[:1200].rstrip() + ("..." if len(text) > 1200 else "")

    return ""


def get_html(url):
    """Download a page, store it locally, and return parsed BeautifulSoup."""

    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()

    # store HTML locally
    filename = re.sub(r"[^a-zA-Z0-9]", "_", url)
    path = os.path.join(DATA_DIR, filename + ".html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(r.text)

    return BeautifulSoup(r.text, "html.parser")


def extract_event_links(section_url):
    """
    Extract event links from a section page.
    """

    soup = get_html(section_url)

    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/evento/" in href:
            url = urljoin(BASE, href)
            links.add(url)

    return links


def parse_event(url):
    """
    Extract relevant information from an event page.
    """

    soup = get_html(url)

    title = None
    description = None

    # Prefer visible event heading first. Some pages contain malformed
    # meta title quotes that can truncate og:title parsing.
    heading = soup.find("h2", class_="title")
    if heading:
        title = heading.get_text(strip=True)
    else:
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title.get("content").strip()
        elif soup.title:
            title = soup.title.get_text(strip=True)

    description = extract_description(soup)

    return {
        "title": title or "Evento",
        "description": description or "",
        "link": url,
    }


def build_rss(events, outfile="docs/events.xml"):
    """Generate RSS XML file."""

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")

    title = ET.SubElement(channel, "title")
    title.text = "Eventos Fundación Japón Madrid"

    link = ET.SubElement(channel, "link")
    link.text = BASE

    description = ET.SubElement(channel, "description")
    description.text = "Eventos publicados en Fundación Japón Madrid"

    for e in events:

        item = ET.SubElement(channel, "item")

        t = ET.SubElement(item, "title")
        t.text = e["title"]

        l = ET.SubElement(item, "link")
        l.text = e["link"]

        g = ET.SubElement(item, "guid")
        g.text = e["link"]

        d = ET.SubElement(item, "description")
        d.text = e["description"] or e["title"]

    tree = ET.ElementTree(rss)
    tree.write(outfile, encoding="utf-8", xml_declaration=True)


def main():

    print("Collecting event URLs...")

    event_links = set()

    for section in SECTIONS:
        url = urljoin(BASE, section)
        links = extract_event_links(url)
        event_links.update(links)

    print(f"Found {len(event_links)} events")

    events = []

    for url in sorted(event_links):
        try:
            event = parse_event(url)
            events.append(event)
            print("parsed:", event["title"])
        except Exception as e:
            print("error parsing", url, e)

    build_rss(events)

    print("RSS written to docs/events.xml")


if __name__ == "__main__":
    main()
