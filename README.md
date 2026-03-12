# Fundación Japón Madrid – Events RSS

## Purpose

This repository generates an **RSS feed of events published on the website of the Fundación Japón Madrid**.

The official website currently does **not provide an RSS or machine-readable feed** for events. This project retrieves the event pages directly from the site, extracts their metadata, and produces a standard RSS feed that can be consumed by feed readers.

Typical use cases include:

* following new events in an RSS reader
* integrating events into personal automation pipelines
* monitoring updates automatically
* publishing the feed through GitHub Pages

The resulting feed is written to:

```
docs/events.xml
```

and can be served statically through GitHub Pages.

---

# How it works

The website organizes activities under several sections:

```
https://md.jpf.go.jp/es/Actividades/<section>
```

Examples include:

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
/es/Actividades/Arte-y-Cultura/evento/5/<slug>
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

# Repository structure

```
.
├── src/
│   └── pipeline.py        # main scraping and RSS generation script
│
├── data/                  # cached HTML pages downloaded from the site
│
├── docs/
│   └── events.xml         # generated RSS feed
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

# Running the script

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

# RSS validation

The generated RSS feed is designed to comply with standard RSS 2.0.

You can validate it using:

* https://validator.w3.org/feed/
* any RSS reader such as `newsboat`

Example:

```
cd jpf_rss
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

# TO DO

The current implementation works but several improvements are planned.

## Scraping improvements

* [ ] Reduce the number of HTTP requests by avoiding unnecessary event page downloads
* [ ] Improve event filtering to avoid non-event pages
* [ ] Extract event **date and time** if present
* [ ] Extract event **location**
* [ ] Improve **description extraction** (currently minimal)
* [ ] Detect and remove **duplicate events**

## Feed improvements

* [ ] Add proper `pubDate` when event dates can be reliably parsed
* [ ] Add `atom:self` link for better RSS interoperability
* [ ] Add richer descriptions (HTML content)

## Reliability

* [ ] Add retry logic for HTTP requests
* [ ] Detect structural changes in the website
* [ ] Add logging instead of simple stdout printing

## Automation

* [ ] Run automatically using **GitHub Actions**
* [ ] Publish RSS feed automatically to **GitHub Pages**
* [ ] Schedule weekly refresh

---

# Disclaimer

This project is an independent tool that retrieves publicly available information from the Fundación Japón Madrid website. It is not affiliated with or endorsed by the institution.

