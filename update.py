"""Rebuild news/publications from content.json; Python 3, no packages required."""
from pathlib import Path
from html import escape
from collections import Counter
import json
import re
import sys

ROOT = Path(__file__).resolve().parent

def text(value):
    return escape(str(value), quote=True)

def url(value):
    value = str(value)
    if not value or value.startswith(("//", "/")) or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", value) and not value.startswith(("https://", "http://")):
        raise ValueError("Use an https:// URL or a relative asset path: " + value)
    return text(value)

def link(href, label):
    return f'<a href="{url(href)}" target="_blank" rel="noopener">{text(label)}</a>'

def pager(name):
    return f'<div class="pagination" id="{name}-pagination" aria-label="{name.title()} pagination" hidden><button type="button" data-direction="previous">← Previous</button><span class="page-position" aria-live="polite"></span><button type="button" data-direction="next">Next →</button></div>'

def page_size(value):
    if not isinstance(value,int) or isinstance(value,bool) or not 1 <= value <= 100:
        raise ValueError("Page size must be an integer between 1 and 100")
    return value

def publications(items, per_page=4):
    counts = Counter()
    keywords = Counter()
    seen = set()
    rows = []
    for item in items:
        for key in ("id", "title", "authors", "year", "type", "venue", "url", "teaser"):
            if key not in item:
                raise ValueError("Publication is missing field: " + key)
        kind = item["type"]
        if kind not in ("journal", "conference", "preprint"):
            raise ValueError("type must be journal, conference, or preprint")
        if item["id"] in seen:
            raise ValueError("Duplicate publication id: " + item["id"])
        seen.add(item["id"])
        if not isinstance(item["authors"], list) or not item["authors"]:
            raise ValueError("authors must be a non-empty list")
        counts[kind] += 1
        tags = item.get("keywords", [])
        if not isinstance(tags,list) or any(not isinstance(t,str) or not t.strip() for t in tags):
            raise ValueError("keywords must be a list of non-empty strings")
        tags = list(dict.fromkeys(t.strip() for t in tags))
        keywords.update(tags)
        tags_attribute = text(json.dumps(tags,ensure_ascii=False))
        title = text(item["title"])
        authors = ", ".join('<strong>Yunfeng Liao</strong>' + text(name[len("Yunfeng Liao"):]) if name.startswith("Yunfeng Liao") else text(name) for name in item["authors"])
        badge = ' <span class="spotlight">Spotlight</span>' if item.get("spotlight") else ""
        venue = text(item["venue"])
        links = link(item["url"], "arXiv ↗" if kind == "preprint" else "Journal ↗" if kind == "journal" else "Proceedings ↗")
        for key, label in (("pdf", "PDF ↗"), ("code", "Code ↗"), ("project", "Project ↗")):
            if item.get(key): links += link(item[key], label)
        bib = item.get("bibtex")
        if not bib:
            bibtype = "article" if kind != "conference" else "inproceedings"
            field = "booktitle" if kind == "conference" else "journal"
            names = " and ".join(n.replace("*", "") for n in item["authors"])
            bib = ("@" + bibtype + "{liao" + str(item["year"]) + re.sub(r"[^a-zA-Z0-9]", "", item["id"]) + ",\n"
                   + "  title = {" + item["title"] + "},\n  author = {" + names + "},\n"
                   + "  year = {" + str(item["year"]) + "},\n  " + field + " = {" + item["venue"] + "},\n"
                   + "  url = {" + item["url"] + "}\n}")
        if tags:
            links += '<span class="paper-topics">' + ' · '.join(text(t) for t in tags) + '</span>'
        links += '<details><summary>BibTeX</summary><pre>' + text(bib) + '</pre></details>'
        rows.append(f'<article class="paper" data-kind="{kind}" data-keywords="{tags_attribute}"><a class="teaser" href="{url(item["url"])}" target="_blank" rel="noopener"><img src="{url(item["teaser"])}" alt="Figure from {title}" loading="lazy"></a><div class="paper-body"><p class="venue">{venue}{badge}</p><h3>{link(item["url"],item["title"])}</h3><p class="authors">{authors}</p><p class="paper-summary">{text(item.get("summary",""))}</p><div class="paper-links">{links}</div></div><span class="paper-year">{text(item["year"])}</span></article>')
    buttons = f'<button type="button" aria-pressed="true" data-filter="all">All work <span>{len(items)}</span></button>'
    for kind, label in (("journal", "Journal papers"), ("conference", "Conference papers"), ("preprint", "Preprints")):
        if counts[kind]:
            buttons += f'<button type="button" aria-pressed="false" data-filter="{kind}">{label} <span>{counts[kind]}</span></button>'
    topics = ''
    if keywords:
        topics = '<div class="topic-toolbar"><span class="filter-label">Topic</span><div class="topic-filters" role="group" aria-label="Filter by research topic"><button type="button" data-topic="" aria-pressed="true">All topics</button>'
        for keyword, count in keywords.items():
            topics += f'<button type="button" data-topic="{text(keyword)}" aria-pressed="false">{text(keyword)} <span>{count}</span></button>'
        topics += '</div></div>'
    return '<div class="pub-toolbar"><div class="filters" role="group" aria-label="Filter publications">' + buttons + f'</div><span class="pub-count" aria-live="polite">{len(items)} publications</span></div>' + topics + f'<div id="paper-list" data-page-size="{page_size(per_page)}">' + "\n".join(rows) + '</div>' + pager("publications")

def news(items, per_page=3):
    rows = []
    for item in items:
        parts = []
        # Either simple text or mixed text/link segments can be used.
        for part in item.get("parts", [{"text":item.get("text", "")} ]):
            value = text(part["text"])
            if part.get("url"): value = link(part["url"], part["text"])
            elif part.get("bold"): value = "<strong>" + value + "</strong>"
            parts.append(value)
        rows.append(f'<article><time datetime="{text(item["date"])}">{text(item.get("label",item["date"]))}</time><p>{"".join(parts)}</p><span class="news-tag">{text(item.get("tag",""))}</span></article>')
    return f'<div class="timeline" data-page-size="{page_size(per_page)}">' + "\n".join(rows) + '</div>' + pager("news")

def main():
    data = json.loads((ROOT / "content.json").read_text(encoding="utf-8-sig"))
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    for label, content in (("PUBLICATIONS",publications(data["publications"],data.get("settings",{}).get("publications_per_page",4))),("NEWS",news(data["news"],data.get("settings",{}).get("news_per_page",3)))):
        pattern = r"<!-- " + label + r"_START -->.*?<!-- " + label + r"_END -->"
        page, count = re.subn(pattern, lambda _: "<!-- " + label + "_START -->" + content + "<!-- " + label + "_END -->", page, flags=re.S)
        if count != 1: raise ValueError("Missing/duplicate page marker: " + label)
    # Only write after every entry and both page regions validate.
    temporary = ROOT / "index.html.tmp"
    temporary.write_text(page,encoding="utf-8")
    temporary.replace(ROOT / "index.html")
    print(f'Updated: {len(data["publications"])} publications, {len(data["news"])} news items.')
    print("Refresh http://127.0.0.1:8765/ to see the changes.")

if __name__ == "__main__":
    try: main()
    except (ValueError,KeyError,TypeError,OSError) as exc:
        print("Update failed. Existing page was preserved.\n" + str(exc), file=sys.stderr)
        sys.exit(1)
