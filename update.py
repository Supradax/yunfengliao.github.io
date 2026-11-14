"""Rebuild news/publications from content.json; Python 3, no packages required."""
from pathlib import Path
from html import escape
from collections import Counter
import json
import re
import sys

ROOT = Path(__file__).resolve().parent
MONTH_ABBREVIATIONS = {"January":"Jan", "February":"Feb", "March":"Mar", "April":"Apr", "May":"May", "June":"Jun", "July":"Jul", "August":"Aug", "September":"Sept", "October":"Oct", "November":"Nov", "December":"Dec"}

def text(value):
    return escape(str(value), quote=True)

def url(value):
    value = str(value)
    if not value or value.startswith(("//", "/")) or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", value) and not value.startswith(("https://", "http://")):
        raise ValueError("Use an https:// URL or a relative asset path: " + value)
    return text(value)

def link(href, label):
    return f'<a href="{url(href)}" target="_blank" rel="noopener">{text(label)}</a>'

def markdown_inline(value):
    """Render a safe, small Markdown subset: **bold**, *italic*, and [links](url)."""
    raw = str(value)
    links = []
    def replace_link(match):
        try:
            href = url(match.group(2).strip())
        except ValueError:
            return match.group(0)
        token = f"\x00MDLINK{len(links)}\x00"
        links.append(f'<a href="{href}" target="_blank" rel="noopener">{text(match.group(1))}</a>')
        return token
    raw = re.sub(r"\[([^]]+)\]\(([^)\s]+)\)", replace_link, raw)
    rendered = text(raw)
    rendered = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", rendered)
    for index, html in enumerate(links):
        rendered = rendered.replace(f"\x00MDLINK{index}\x00", html)
    return rendered


def render_parts(parts):
    if not isinstance(parts, list): raise ValueError("description.parts must be a list")
    output=[]
    for part in parts:
        if not isinstance(part, dict) or "text" not in part: raise ValueError("Each description part needs text")
        value=markdown_inline(part["text"])
        if part.get("bold"): value="<strong>"+value+"</strong>"
        if part.get("url"):
            value=f'<a href="{url(part["url"])}" target="_blank" rel="noopener">{value}</a>'
        output.append(value)
    return "".join(output)

def about_html(site):
    about = site.get("about", {})
    required = ("name", "role", "institution", "description", "education", "links")
    if any(key not in about for key in required): raise ValueError("site.about is missing a required field")
    education = about["education"]
    if not isinstance(education, list): raise ValueError("site.about.education must be a list")
    education_rows=[]
    for item in education:
        for key in ("degree","institution","dates"):
            if key not in item: raise ValueError("Each education item needs degree, institution, and dates")
        education_rows.append(f'<div class="education-entry"><strong>{text(item["degree"])}</strong><br/>{text(item["institution"])} <span class="education-dates">· {text(item["dates"])}</span></div>')
    links=[]
    for item in about["links"]:
        href=url(item["url"]); target=' target="_blank" rel="noopener"' if item.get("external") else ""
        links.append(f'<a href="{href}"{target}>{text(item["label"])} <span aria-hidden="true">↗</span></a>')
    description=render_parts(about["description"].get("parts", [])) if isinstance(about["description"],dict) else markdown_inline(about["description"])
    return (f'<h1>{text(about["name"])}<span class="name-alias">({text(about.get("alias", ""))})</span></h1>'
            f'<p class="role">{text(about["role"])} <span>·</span> {text(about["institution"])}</p>'
            f'<p class="about">{description}</p>'
            f'<div class="education"><span class="education-label">{text(about.get("education_label", "Education"))}</span><div class="education-list">{"".join(education_rows)}</div></div>'
            f'<div class="profile-links">{"".join(links)}</div>')

def research_html(items):
    if not isinstance(items,list) or len(items) != 3: raise ValueError("site.research must contain three cards")
    icons = {
      "geometry": '<div aria-hidden="true" class="mini-art geometry-icon"><svg viewBox="0 0 90 60" xmlns="http://www.w3.org/2000/svg"><path d="M4 43Q18 7 44 32T85 18L78 48Q52 60 37 42T4 43" fill="#d7e6f7" stroke="#789cc6"/><path d="m17 34 39-13 24 14-39 13Z" fill="#eef5fd" stroke="#658ab6"/><defs><marker id="tangent-arrowhead" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" markerUnits="userSpaceOnUse" orient="auto"><path d="M1 1L7 4L1 7" fill="none" stroke="#345f93" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs><g fill="none" stroke="#345f93" stroke-width="1.5" stroke-linecap="round"><path d="M41 37L66 28" marker-end="url(#tangent-arrowhead)"/><path d="M41 37L53 49" marker-end="url(#tangent-arrowhead)"/></g><circle cx="41" cy="37" r="2" fill="#345f93"/><text x="17" y="14" fill="#345f93" font-family="Georgia,serif" font-size="13" font-style="italic">TₚM</text></svg></div>',
      "graphics": '<div aria-hidden="true" class="mini-art graphics"><i></i><i></i><i></i></div>',
      "network": '<div aria-hidden="true" class="mini-art network-icon"><svg viewBox="0 0 90 60" xmlns="http://www.w3.org/2000/svg"><g stroke="#8aa9cd" stroke-width=".9"><path d="M10 12 43 7"/><path d="M10 12 43 22"/><path d="M10 12 43 38"/><path d="M10 12 43 53"/><path d="M10 30 43 7"/><path d="M10 30 43 22"/><path d="M10 30 43 38"/><path d="M10 30 43 53"/><path d="M10 48 43 7"/><path d="M10 48 43 22"/><path d="M10 48 43 38"/><path d="M10 48 43 53"/><path d="M43 7 77 20"/><path d="M43 7 77 42"/><path d="M43 22 77 20"/><path d="M43 22 77 42"/><path d="M43 38 77 20"/><path d="M43 38 77 42"/><path d="M43 53 77 20"/><path d="M43 53 77 42"/></g><g fill="#edf4fd" stroke="#416f9f" stroke-width="1.2"><circle cx="10" cy="12" r="4"/><circle cx="10" cy="30" r="4"/><circle cx="10" cy="48" r="4"/><circle cx="43" cy="7" r="4"/><circle cx="43" cy="22" r="4"/><circle cx="43" cy="38" r="4"/><circle cx="43" cy="53" r="4"/><circle cx="77" cy="20" r="4"/><circle cx="77" cy="42" r="4"/></g></svg></div>'}
    cards=[]
    for item in items:
        for key in ("number","title","body","keywords","icon"):
            if key not in item: raise ValueError("Research card is missing field: " + key)
        cards.append(f'<article class="research-card"><span class="card-no">{text(item["number"])}</span>{icons.get(item["icon"], "")}<h3>{text(item["title"])}</h3><p>{text(item["body"])}</p><span class="keywords">{text(item["keywords"])}</span></article>')
    return '<section class="section" id="research"><div class="section-head"><div><p class="eyebrow">01 / RESEARCH</p></div></div><div class="research-grid">' + ''.join(cards) + '</div></section>'

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
        labels = item.get("labels", [])
        if not isinstance(labels, list) or any(not isinstance(label, str) or not label.strip() for label in labels):
            raise ValueError("labels must be a list of non-empty strings")
        label_spans = "".join(
            f'<span class="paper-label" style="display:inline-block;background:#e5eef9;color:#2f5b91;padding:1px 8px;letter-spacing:.7px;font-size:9px;line-height:1.5;vertical-align:middle">{text(label)}</span>'
            for label in labels
        )
        badge = f'<span class="paper-labels" style="display:inline-flex;gap:8px;margin-left:12px;vertical-align:middle">{label_spans}</span>' if labels else ''

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
        rows.append(f'<article class="paper" data-kind="{kind}" data-keywords="{tags_attribute}"><a class="teaser" href="{url(item["url"])}" target="_blank" rel="noopener"><img src="{url(item["teaser"])}" alt="Figure from {title}" loading="lazy"></a><div class="paper-body"><p class="venue">{venue}{badge}</p><h3>{link(item["url"],item["title"])}</h3><p class="authors">{authors}</p><p class="paper-summary">{text(item.get("summary",""))}</p><div class="paper-links">{links}</div></div><span class="paper-year"><span class="paper-date">{text(MONTH_ABBREVIATIONS.get(item.get("month", ""), item.get("month", "")) + " " + str(item["year"]))}</span></span></article>')
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

def news_label(value):
    value = str(value)
    match = re.fullmatch(r"(\d{4})-(\d{1,2})", value)
    if not match: return value
    year, month = match.groups()
    names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"]
    number = int(month)
    return f"{names[number - 1]} {year}" if 1 <= number <= 12 else value

def news(items, per_page=3):
    rows = []
    for item in items:
        if "text" in item:
            body = markdown_inline(item["text"])
        else:
            parts = []
            for part in item.get("parts", [{"text":item.get("text", "")} ]):
                value = markdown_inline(part["text"])
                if part.get("url"): value = f'<a href="{url(part["url"])}" target="_blank" rel="noopener">{value}</a>'
                if part.get("bold"): value = "<strong>" + value + "</strong>"
                parts.append(value)
            body = "".join(parts)
        rows.append(f'<article><time datetime="{text(item["date"])}">{text(item.get("label") or news_label(item["date"]))}</time><p>{body}</p><span class="news-tag">{text(item.get("tag",""))}</span></article>')
    return f'<div class="timeline" data-page-size="{page_size(per_page)}">' + "\n".join(rows) + '</div>' + pager("news")

def main():
    data = json.loads((ROOT / "content.json").read_text(encoding="utf-8-sig"))
    settings = data.get("settings", {})
    publications_per_page = page_size(settings.get("publications_per_page", 4))
    news_per_page = page_size(settings.get("news_per_page", 3))
    page = (ROOT / "index.html").read_text(encoding="utf-8")
    about = about_html(data.get("site", {}))
    research = research_html(data.get("site", {}).get("research", []))
    page, about_count = re.subn(r"<!-- ABOUT_START -->.*?<!-- ABOUT_END -->", lambda _: "<!-- ABOUT_START -->" + about + "<!-- ABOUT_END -->", page, count=1, flags=re.S)
    page, research_count = re.subn(r"<!-- RESEARCH_START -->.*?<!-- RESEARCH_END -->", lambda _: "<!-- RESEARCH_START -->" + research + "<!-- RESEARCH_END -->", page, count=1, flags=re.S)
    if about_count != 1 or research_count != 1: raise ValueError("Missing/duplicate About or Research page marker")
    for label, content in (("PUBLICATIONS",publications(data["publications"],publications_per_page)),("NEWS",news(data["news"],news_per_page))):
        pattern = r"<!-- " + label + r"_START -->.*?<!-- " + label + r"_END -->"
        page, count = re.subn(pattern, lambda _: "<!-- " + label + "_START -->" + content + "<!-- " + label + "_END -->", page, flags=re.S)
        if count != 1: raise ValueError("Missing/duplicate page marker: " + label)
    # Only write after every entry and both page regions validate.
    temporary = ROOT / "index.html.tmp"
    temporary.write_text(page,encoding="utf-8")
    temporary.replace(ROOT / "index.html")
    print(f'Updated: {len(data["publications"])} publications, {len(data["news"])} news items.')
    publication_pages = max(1, (len(data["publications"]) + publications_per_page - 1) // publications_per_page)
    news_pages = max(1, (len(data["news"]) + news_per_page - 1) // news_per_page)
    print(f"Publications: {publications_per_page} per page | {publication_pages} pages before filtering")
    print(f"News: {news_per_page} per page | {news_pages} pages")
    print("Change settings.publications_per_page and settings.news_per_page in content.json.")
    print("Refresh http://127.0.0.1:8765/ to see the changes.")

if __name__ == "__main__":
    try: main()
    except (ValueError,KeyError,TypeError,OSError) as exc:
        print("Update failed. Existing page was preserved.\n" + str(exc), file=sys.stderr)
        sys.exit(1)
