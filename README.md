# Fundación Japón Madrid – RSS feed

## Purpose

I keep missing out on the film series/retrospectives, releases and events. I refuse to use instagram/facebook/twitter and just don't want more mail with the newsletter. I like RSS. No RSS? fine, I'll do it myself.

This repository generates an [**RSS feed of events published on the website of the Fundación Japón Madrid**](https://md.jpf.go.jp/es/Actividades).

Copy the link to [`events.xml`](https://lorcai.github.io/jpf-rss/events.xml) in the [Feeder app](https://github.com/spacecowboy/Feeder/) or other RSS reader to get notifications for new events.

The feed is updated automatically every Wednesday at 9:00 AM (Madrid time) using GitHub Actions

## What this repository does

The website does **not provide an RSS or machine-readable feed** for events. This repository retrieves the event pages from the site and produces a standard RSS feed.

The resulting feed is written to: [`docs/events.xml`](https://lorcai.github.io/jpf-rss/events.xml), and a simple HTML index page (for debugging) is generated at: [`docs/index.html`](https://lorcai.github.io/jpf-rss/index.html).

The [Timeline list](#timeline-list-ultimeline) of each "Actividades" section is scraped. This implies that only events starting or ongoing in the current month are included in the feed. Events starting in future months (usually few) may be missed by the feed until the month of the event is reached.

---

# Running the script

## Running with Docker

Build the container:

```
docker build -t jpf-rss .
```

Run the script:

```
docker run --rm \
  -u $(id -u):$(id -g) \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/docs:/app/docs \
  jpf-rss
```

This mounts the repository directory so the generated RSS file and downloaded HTML pages are written to the host filesystem.

---

## Local execution

Install dependencies:

```
pip install -r requirements.txt
```

Run the scraper:

```
python src/pipeline.py
```

The RSS file will be generated at:

```
docs/events.xml
```

---

# How it works

The website organizes activities under several sections:

```
https://md.jpf.go.jp/es/Actividades/<section>
```

Sections include:

* Arte y Cultura
* Lengua Japonesa
* Estudios Japoneses
* Biblioteca
* Eventos organizados por otras instituciones

Each section page contains links to individual event pages of the form:

```
/es/Actividades/<section>/evento/<id>/<slug>
```

Example:

```
/es/Actividades/Arte-y-Cultura/evento/529/jff-theater-peliculas-de-marzo-2026
```

The script performs the following steps:

1. Download the HTML page for each activity section.
2. Extract links that match the event URL pattern.
3. Visit each event page.
4. Extract:

   * event title
   * description
   * canonical link
5. Generate an RSS feed containing all discovered events.

All downloaded HTML pages are stored locally in:

```
data/
```

This allows inspection of the scraped pages and simplifies debugging if the website structure changes.

---

# RSS validation

The generated RSS feed is designed to comply with standard RSS 2.0.

You can validate it using:

* https://validator.w3.org/feed/
* any RSS reader such as `newsboat`

Example:

```
cd jpf-rss
echo "file://$(pwd)/docs/events.xml" >>  ~/.newsboat/urls
newsboat
```

---

# Request volume

The script performs approximately:

```
number_of_sections + number_of_events
```

HTTP requests.

In practice this is roughly:

```
~40 requests per run
```

This is intentionally conservative and safe to execute periodically (e.g., weekly).

---

# Section behavior: calendar, timeline, and search

The Fundación Japón section pages expose event information through two
different UI mechanisms that do not behave the same:

## Calendar widget (`eventData`)

The calendar dots are populated from a JavaScript array (`eventData`).
In practice, this data can be partial:

* it mainly marks events by start date for the selected month
* it may omit ongoing events that started in previous months
* in some views it can even be empty while timeline entries are still present

For this reason, relying only on calendar data is not sufficient for
building a complete feed.

## Timeline list (`ul.timeline`)

The rendered timeline is the most complete monthly listing shown to users.
It typically includes:

* entries in the selected month
* ongoing events that started in previous months

The scraper therefore uses listing pages and extracts event URLs from
timeline-like listings instead of relying only on calendar dots.

## Search-by-date pages (`/buscar/<MM>/<YYYY>/<DD>`)

Section URLs such as:

```
/es/Actividades/<section>/buscar/04/2026/01
```

show a month-oriented listing and can reveal events not visible in the
default section view. This is why some events may appear on the general /Actividades/ page but not show on the default corresponding section page. The `/buscar` (e.g https://md.jpf.go.jp/es/Actividades/Arte-y-Cultura/buscar/04/2026/01; to search April) pages can useful when trying to avoid missing upcoming events for the next month.

---

# TO DO

Possible improvements:

## Scraping improvements

* [x] Improve event filtering to avoid non-event pages. 
URL shape /evento/... is used for both “real event timeline items” and some “informational pages,” and the current collector does not distinguish context (timeline vs static content area).

## Feed improvements

* [ ] Add proper `pubDate` when event dates can be reliably parsed
* [ ] Add `atom:self` link for better RSS interoperability

## Reliability

* [ ] Add retry logic for HTTP requests

## Automation

* [x] Run automatically using **GitHub Actions**
* [x] Publish RSS feed automatically to **GitHub Pages**
* [x] Schedule weekly refresh
* [x] Generate a simple `index.html` from `events.xml` for GitHub Pages

---

# Disclaimer

This project is an independent tool that retrieves publicly available information from the Fundación Japón Madrid website. It is not affiliated with or endorsed by the institution.

